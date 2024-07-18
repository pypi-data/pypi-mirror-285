#!/usr/bin/env python
#  Copyright Femtosense 2024
#
#  By using this software package, you agree to abide by the terms and conditions
#  in the license agreement found at https://femtosense.ai/legal/eula/
#


import os
import pathlib
import sys
import numpy as np

import torch
import pickle

import pkg_resources

import femtodriver
from femtorun import FemtoRunner, DummyRunner
from femtodriver import SPURunner, FakeSPURunner
from femtodriver.fx_runner import FXRunner

from femtodriver.program_handler import ProgramHandler, NullHandler

from scipy.io import wavfile
import zipfile

try:
    from femtobehav.sim.runner import SimRunner  # for comparison
    from femtomapper.run import FQIRArithRunner, FMIRRunner

    DEV_MODE = True
except ImportError:
    DEV_MODE = False

import logging

import argparse
from argparse import (
    RawTextHelpFormatter,
)  # allow carriage returns in help strings, for displaying model options

import yaml

from femtodriver.util.run_util import process_single_outputs
from pathlib import Path


if DEV_MODE:
    TOP_LEVEL_PACKAGE_DIR = Path(femtodriver.__file__).parent.parent.parent
    MODEL_SOURCE_DIR = TOP_LEVEL_PACKAGE_DIR / Path("models")
    # will only work if installed locally with -e
    if os.path.exists(MODEL_SOURCE_DIR):
        MODEL_SOURCE_DIR = str(MODEL_SOURCE_DIR)
    else:
        MODEL_SOURCE_DIR = None
else:
    MODEL_SOURCE_DIR = None


def check_dev_mode(feat):
    if not DEV_MODE:
        raise RuntimeError(
            f"{feat} is a FS-only feature, requires internal packages. Exiting"
        )


class Femtodriver:
    def __init__(self, model_source_dir: str = MODEL_SOURCE_DIR):
        self.model_source_dir = model_source_dir

        self.args = None  # argparse args

        self.model_dir = None  # the output dir for the model
        self.metadata_zip = None
        self.modelname = None
        self.fqir = None
        self.fasmir = None

        self.fmir = None

        # important internal objs
        self.hw_runner: SPURunner = None
        self.compare_runners: list[FemtoRunner] = None

        # recording of simulation metrics
        self.sim_metrics: dict = None
        self.metrics_path: str = None

    def _parse_args(self, argv):
        """returns argparse object and sets self.args
        also sets:
            self.comparisons
        """
        parser = argparse.ArgumentParser(
            formatter_class=RawTextHelpFormatter,
            description="run a pickled FASMIR or FQIR on hardware. Compare with output of FB's SimRunner\n\n"
            + "Useful recipes:\n"
            + "----------------------\n"
            + "Run on hardware, default comparisons with full debug (fasmir):\n"
            + "\tpython run_from_pt.py ../models/modelname --hardware=zynq --runners=fasmir --debug --debug_vars=all\n\n"
            + "Generate SD (no board/cable needed):\n"
            + "\tpython run_from_pt.py ../models/modelname\n\n"
            + "Run simulator (no board/cable needed, ignore the comparison):\n"
            + "\tpython run_from_pt.py ../models/modelname --runners=fasmir\n\n",
        )

        parser.add_argument(
            "model",
            help="model to run. " + self._model_helpstr(),
        )
        parser.add_argument(
            "--model_options_file",
            default=None,
            help=".yaml with run options for different models (e.g. compiler options). Default is femtodriver/femtodriver/models/options.yaml",
        )
        parser.add_argument(
            "--output_dir",
            default="model_datas",
            help="where to write fasmir, fqir, programming images, programming streams, etc",
        )
        parser.add_argument(
            "--n_inputs",
            default=2,
            type=int,
            help="number of random sim inputs to drive in",
        )
        parser.add_argument(
            "--input_file",
            default=None,
            help="file with inputs to drive in. Expects .npy from numpy.save. Expecting single 2D array of values, indices are (timestep, vector_dim)",
        )
        parser.add_argument(
            "--input_file_sample_indices",
            default=None,
            help="lo,hi indices to run from input_file",
        )
        parser.add_argument(
            "--force_femtocrux_compile",
            default=False,
            action="store_true",
            help="force femtocrux as the compiler, even if FS internal packages present",
        )
        parser.add_argument(
            "--force_femtocrux_sim",
            default=False,
            action="store_true",
            help="force femtocrux as the simulator, even if FS internal packages present",
        )
        parser.add_argument(
            "--hardware",
            default="fakezynq",
            help="primary runner to use: (options: zynq, fakezynq, redis)",
        )
        parser.add_argument(
            "--runners",
            default="",
            help="which runners to execute. If there are multiple, compare each of them to the first, "
            "comma-separated. Options: hw, fasmir, fqir, fmir, fakehw",
        )
        parser.add_argument(
            "--debug_vars",
            default=None,
            help="debug variables to collect and compare values for, comma-separated (no spaces), or 'all'",
        )
        parser.add_argument(
            "--debug_vars_fname",
            default=None,
            help="file with a debug variable name on each line",
        )
        parser.add_argument(
            "--debug", default=False, action="store_true", help="set debug log level"
        )
        parser.add_argument(
            "--noencrypt",
            default=False,
            action="store_true",
            help="don't encrypt programming files",
        )
        parser.add_argument(
            "--sim_est_input_period",
            default=None,
            type=float,
            help="simulator input period for energy estimation. No impact on runtime. Floating point seconds",
        )
        parser.add_argument(
            "--dummy_output_file",
            default=None,
            help="for fakezynq, the values that the runner should reply with. Specify a .npy for a single variable",
        )

        args = parser.parse_args(argv)

        ####################################
        # checks, some derived vars

        # collect comparisons
        if args.runners == "":
            self.comparisons = []
        else:
            self.comparisons = args.runners.split(",")

        self._suppress_import_debug(args.debug)

        return args

    def load_model(self, model_path: str):
        """try to find the model, figure out what format it is:
          - pytorch pickle : FQIR
          - plain pickle : FASMIR
          - zipfile : zipped metadata dir (output of FX)
          - directory : previously-run model_data/MODEL dir
        unpack and expand each

        sets:
            self.modelname
            self.metadata_zip
            self.fqir
            self.fmir
            self.fasmir
        """

        # get "hello world"/identity out of the way, it's in the package
        if model_path == "LOOPBACK":
            model_path = pkg_resources.resource_filename(
                "femtodriver", "resources/identity.pt"
            )
            self.modelname = "LOOPBACK"
            self.fqir = torch.load(model_path, map_location=torch.device("cpu"))
            return

        if not os.path.exists(model_path):
            raise ValueError(f"supplied model file {model_path} does not exist")

        model_with_ext = os.path.basename(os.path.expanduser(model_path))
        self.modelname, model_ext = os.path.splitext(model_with_ext)

        def _load_fasmir_pickle(model_path):
            fasmir = pickle.load(open(model_path, "rb"))
            if fasmir.__class__.__name__ not in ["FASMIR"]:
                raise RuntimeError(f"supplied model {model_path} didn't contain FASMIR")
            return fasmir

        def _load_fqir_torchpickle(model_path):
            fqir = torch.load(model_path, map_location=torch.device("cpu"))
            if fqir.__class__.__name__ not in ["GraphProto"]:
                raise RuntimeError(f"supplied model {model_path} didn't contain FQIR")
            return fqir

        if model_ext in [".pt", ".pth"]:
            # open model
            self.fqir = _load_fqir_torchpickle(model_path)
        elif model_ext == ".pck":
            # open model
            self.fasmir = _load_fasmir_pickle(model_path)
        elif model_ext == "":
            # metadata dir
            self.model_dir = model_path
        elif model_ext == ".zip":
            # zipped metadata dir
            self.metadata_zip = model_path
        else:
            raise ValueError(
                f"invalid model extension. Got {model_ext}. Need one of: .pt/.pth (FQIR pickle) or .pck (FASMIR pickle)"
            )

    def compile_model(self) -> str:
        """compile the model, dumping into meta_dir

        also may generate new self.fmir, self.fasmir if starting w/ FQIR
        """

        args = self.args

        if self.model_dir is not None:
            found = False
            PREV_COMPILED = ["femtomapper", "femtocrux", "zipfile"]
            for compiler_name in PREV_COMPILED:
                # find first working meta dir
                meta_dir = os.path.join(self.model_dir, f"meta_from_{compiler_name}")
                if os.path.exists(meta_dir):
                    found = True
                    break

            # doesn't do anything, just provides handler.fasmir/fmir/fqir = None
            if not found:
                raise RuntimeError(
                    f"couldn't find previously compiled meta_from_ {PREV_COMPILED} in {self.model_dir}"
                )
            handler = NullHandler(meta_dir)

        else:
            if self.metadata_zip is not None:
                compiler_name = "zipfile"
            elif DEV_MODE and not args.force_femtocrux_compile:
                compiler_name = "femtomapper"
            else:
                compiler_name = "femtocrux"

            self.model_dir = os.path.join(
                os.path.expanduser(args.output_dir), f"{self.modelname}"
            )
            meta_dir = os.path.join(self.model_dir, f"meta_from_{compiler_name}")
            if not os.path.exists(meta_dir):
                os.makedirs(meta_dir)

            # get compiler args
            model_options_path = self._get_options_path(
                self.model_source_dir, args.model_options_file
            )
            self.compiler_kwargs = self._load_model_options(
                self.modelname, model_options_path
            )

            handler = ProgramHandler(
                fasmir=self.fasmir,
                fqir=self.fqir,
                compiler=compiler_name,
                compiler_kwargs=self.compiler_kwargs,
                zipfile_fname=self.metadata_zip,
                encrypt=not args.noencrypt,
                meta_dir=meta_dir,
            )

        # if using internal packages (DEV_MODE), it might have made a new FASMIR/FMIR
        self.fasmir = handler.fasmir
        self.fmir = handler.fmir

        if DEV_MODE:
            with open(os.path.join(self.model_dir, "fasmir.txt"), "w") as f:
                f.write(str(self.fasmir))
            if self.fqir is not None:
                with open(os.path.join(self.model_dir, "fqir.txt"), "w") as f:
                    f.write(str(self.fqir))

        return meta_dir

    @staticmethod
    def _get_runner_kwargs(args):
        runner_kwargs = {"encrypt": not args.noencrypt}
        if args.hardware == "zynq":  # hard SPU plugged into FPGA
            runner_kwargs["platform"] = "zcu104"
            runner_kwargs["program_pll"] = True
            runner_kwargs["fake_connection"] = False

        elif args.hardware == "fpgazynq":  # soft SPU inside FPGA logic
            runner_kwargs["platform"] = "zcu104"
            runner_kwargs["program_pll"] = False
            runner_kwargs["fake_connection"] = False

        elif args.hardware == "redis":  # redis-based simulation (questa)
            runner_kwargs["platform"] = "redis"
            runner_kwargs["program_pll"] = True
            runner_kwargs["fake_connection"] = False

        elif args.hardware == "fakezynq":  # e.g. for generating EVK program
            runner_kwargs["platform"] = "zcu104"
            runner_kwargs["program_pll"] = False
            runner_kwargs["fake_connection"] = True

        elif args.hardware == "fakeredis":  # e.g. for integration test
            runner_kwargs["platform"] = "redis"
            runner_kwargs["program_pll"] = False
            runner_kwargs["fake_connection"] = True

        else:
            raise RuntimeError(f"Unknown runner {args.hardware}")

        return runner_kwargs

    def create_SPURunner(self, meta_dir):
        """instantiates self.hw_runner = SPURunner()
        handles debug-vars-related options
        and fake outputs/recv vals
        """

        args = self.args

        runner_kwargs = self._get_runner_kwargs(args)

        if not os.path.exists(self.io_records_dir):
            os.makedirs(self.io_records_dir)

        # make SPURunner and SimRunner to compare it to
        fake_hw_recv_vals = None
        if args.dummy_output_file is not None:
            fake_hw_recv_vals = np.load(args.dummy_output_file)

        # collect debug vars
        self.debug_vars = []
        if args.debug_vars_fname is not None:
            varf = open(args.debug_vars_fname, "r")
            self.debug_vars += varf.readlines()

        if args.debug_vars is not None:
            self.debug_vars += args.debug_vars.split(",")

        hw_runner = SPURunner(
            meta_dir,
            fake_hw_recv_vals=fake_hw_recv_vals,
            debug_vars=self.debug_vars,
            **runner_kwargs,
            io_records_dir=self.io_records_dir,
        )

        if DEV_MODE:
            hw_runner.attach_debugger(self.fasmir)

        # fill in for 'all' debug vars option
        # not all runners can necesarily take 'all' as a debug vars arg
        if args.debug_vars == "all" or args.debug_vars == ["all"]:
            self.debug_vars = hw_runner.debug_vars

        return hw_runner

    def run_comparisons(self, hw_runner: SPURunner, comparisons: list[str]) -> int:
        args = self.args
        fqir = self.fqir
        fasmir = self.fasmir

        if DEV_MODE and args.force_femtocrux_compile and not args.force_femtocrux_sim:
            self._check_dev_mode("FX compile but dev mode sim")
            # have to make our own FASMIR so we can simulate it
            # this is a little iffy, weakly relies on compiler determinism
            # since we have compiled twice here
            # even a nondeterministic compiler should always be correct, though
            unused_meta_dir = f"{self.modelname}_unused_fx_compile_but_not_sim"
            parallel_dev_handler = ProgramHandler(
                fasmir=None,
                fqir=fqir,
                compiler="femtomapper",
                compiler_kwargs=self.compiler_kwargs,
                encrypt=not args.noencrypt,
                meta_dir=unused_meta_dir,
            )
            sim_fasmir = parallel_dev_handler.fasmir
            sim_fmir = parallel_dev_handler.fmir
        else:
            sim_fasmir = self.fasmir
            sim_fmir = self.fmir

        if "fqir" in comparisons or "fmir" in comparisons:
            if fqir is None:
                raise RuntimeError(
                    "asked for fqir or fmir comparison, but did't start from FQIR"
                )

        compare_runners = []
        compare_names = []

        # Make use of pythons treatment of empty list as False in if statements
        if comparisons:
            for comp in comparisons:
                if comp == "hw":
                    compare_runners.append(hw_runner)
                    compare_names.append("hardware")
                elif comp == "fasmir":
                    if DEV_MODE and not args.force_femtocrux_sim:
                        # FB runner
                        fasmir_runner = SimRunner(
                            sim_fasmir,  # model might be fqir, need to compile for SimRunner
                            input_padding=hw_runner.io.input_padding,
                            output_padding=hw_runner.io.output_padding,
                        )

                    else:
                        # use FXRunner which wraps docker
                        fasmir_runner = FXRunner(
                            self.fqir,  # XXX it will recompile, not sure if there's a way to get it to use what it already compiled
                            input_padding=hw_runner.io.input_padding,
                            output_padding=hw_runner.io.output_padding,
                        )

                    compare_runners.append(fasmir_runner)
                    compare_names.append("fasmir")

                elif comp == "fqir":
                    self._check_dev_mode("comparison to FQIR runner")
                    # FIXME, could move FQIRRunner def from FM to fmot
                    if fqir is not None:
                        fq_runner = FQIRArithRunner(fqir)
                        compare_runners.append(fq_runner)
                        compare_names.append("fqir")
                elif comp == "fmir":
                    self._check_dev_mode("comparison to FMIR runner")
                    if args.force_femtocrux_compile and args.force_femtocrux_sim:
                        raise NotImplementedError("FX can't simulate FMIR")
                    if fqir is not None:
                        fm_runner = FMIRRunner(sim_fmir)
                        compare_runners.append(fm_runner)
                        compare_names.append("fmir")
                elif comp == "dummy":
                    # for fake runner, what do you reply with
                    if args.dummy_output_file is not None:
                        fname = args.dummy_output_file
                        if fname.endswith(".npy"):
                            dummy_vals = np.load(fname)
                            dummy_output_dict = {
                                hw_runner.get_single_output_name(): dummy_vals
                            }
                        elif fname.endswith(".pt"):
                            # would put dictionary with multiple output vars in here
                            raise RuntimeError(
                                "unsupported file format for --dummy_output_file, only .npy is supported"
                            )
                        else:
                            raise RuntimeError(
                                "unsupported file format for --dummy_output_file, only .npy is supported"
                            )
                    else:
                        dummy_output_dict = None

                    fakehw_runner = DummyRunner(dummy_output_dict)
                    compare_runners.append(fakehw_runner)
                    compare_names.append("dummy")
                else:
                    raise RuntimeError(f"unknown comparison runner '{comp}'")

        self.compare_runners = compare_runners

        # simulator input preparation
        # make some fake inputs, or load from file

        N = args.n_inputs

        if args.input_file is None:
            inputs = hw_runner.make_fake_inputs(N, style="random")
        else:
            if args.input_file.endswith(".wav"):
                input_vals = self.create_shaped_input_from_wav(args.input_file)
            elif args.input_file.endswith(".npy"):
                input_vals = np.load(args.input_file)
            else:
                raise RuntimeError(
                    "unsupported file format for --input_file, only .wav and .npy is supported"
                )

            N = input_vals.shape[0]
            inputs = hw_runner.make_fake_inputs(N, style="random")
            if len(inputs) > 1:
                raise RuntimeError("can only support one input via file")
            for k, v in inputs.items():
                inputs[k] = input_vals

            # trim to sample range, if supplied
            if args.input_file_sample_indices is not None:
                lo, hi = args.input_file_sample_indices.split(",")
                for k, v in inputs.items():
                    inputs[k] = inputs[k][int(lo) : int(hi)]

        if len(inputs) == 1:
            print("single input variable detected, saving to inputs.npy")
            np.save("inputs.npy", inputs[next(iter(inputs))])

        # if no runners specified, just reset (e.g. to record PROG) and exit
        if args.runners == "":
            hw_runner.reset()
            return 0

        hw_runner.ioplug.start_recording("io_sequence")

        if len(comparisons) > 1:
            self.compare_status = {}
            outputs, internals = FemtoRunner.compare_runs(
                inputs,
                *compare_runners,
                names=compare_names,
                compare_internals=len(self.hw_runner.debug_vars) > 0,
                except_on_error=False,
                compare_status=self.compare_status,
            )

        else:
            compare_runners[0].reset()
            output_vals, internal_vals, _ = compare_runners[0].run(inputs)
            outputs = {compare_names[0]: output_vals}
            internals = {compare_names[0]: internal_vals}
            compare_runners[0].finish()

        hw_runner.ioplug.commit_recording("all.yaml")

        pickle.dump(
            inputs, open(os.path.join(self.meta_dir, "runner_inputs.pck"), "wb")
        )
        pickle.dump(
            outputs, open(os.path.join(self.meta_dir, "runner_outputs.pck"), "wb")
        )
        pickle.dump(
            internals, open(os.path.join(self.meta_dir, "runner_internals.pck"), "wb")
        )

        print(
            f"outputs and internal variables pickles saved to {os.path.join(self.meta_dir, 'runner_*.pck')}"
        )
        print(
            "  unpickle with internals = pickle.load(open('runner_internals.pck', 'rb'))"
        )
        print("  then internals[runner_name][varname][j]")
        print("  is runner_name's values for varname at timestep j")
        print("  fasmir, fmir, fqir will report everything.")
        print(
            "  the setting of --debug_vars determines what's available from hardware."
        )

        out_fnames, _ = process_single_outputs(outputs)
        if out_fnames is not None:
            print(
                f"also saved single output variable's values for each runner to {out_fnames}"
            )
            print("  summarized to output_diff.png")

        for runner in compare_runners:
            if runner.__class__.__name__ == "SimRunner":
                print(
                    f"found a SimRunner, sending metrics to {os.path.join(self.model_dir, 'metrics.yaml')}"
                )

                yaml_fb_metrics = runner.get_metrics(
                    input_period=args.sim_est_input_period,
                    as_yamlable=True,
                    concise=True,
                )

                self.metrics_path = os.path.join(self.model_dir, "metrics.yaml")
                with open(self.metrics_path, "w") as f:
                    yaml.dump(yaml_fb_metrics, f, sort_keys=False)

                self.sim_metrics = runner.get_metrics(
                    input_period=args.sim_est_input_period,
                )
                print("power was", self.sim_metrics["Power (W)"])

            elif runner.__class__.__name__ == "FXRunner":
                print(
                    f"found Femtocrux's simulator, sending metrics to {os.path.join(self.model_dir, 'metrics.txt')}"
                )
                print(runner.sim_report)
                metrics_str = runner.sim_report

                self.metrics_path = os.path.join(self.model_dir, "metrics.txt")
                with open(self.metrics_path, "w") as f:
                    f.writelines(metrics_str)

        # repeat output comparison result
        print()
        if len(comparisons) > 1:
            if self.compare_status["pass"]:
                print("===================================")
                print("comparison good!")
                print("===================================")
            else:
                print(self.compare_status["status_str"])
                print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                print("COMPARISON FAILED")
                print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                return 1
        else:
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("comparison not performed")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        return 0

    def _suppress_import_debug(self, debug):
        if debug:
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
            # turn these down, they're long and annoying
            mpl_logger = logging.getLogger("matplotlib")
            mpl_logger.setLevel(logging.WARNING)
            PIL_logger = logging.getLogger("PIL")
            PIL_logger.setLevel(logging.WARNING)
        else:
            logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    @staticmethod
    def _check_dev_mode(feat):
        if not DEV_MODE:
            raise RuntimeError(
                f"{feat} is a FS-only feature, requires internal packages. Exiting"
            )

    @staticmethod
    def _model_helpstr(model_source_dir=MODEL_SOURCE_DIR):
        if model_source_dir is None:
            return ""

        yamlfname = f"{model_source_dir}/options.yaml"
        with open(yamlfname, "r") as file:
            model_desc = yaml.safe_load(file)

        s = "\navailable models in femtodriver/femtodriver/models:\n"
        thisdir, subdirs, files = next(iter(os.walk(model_source_dir)))
        for file in files:
            if file.endswith(".pt"):
                modelname = file[:-3]

                s += f"  {modelname}"
                if modelname not in model_desc:
                    s += f"\t  <-- missing specification in options.yaml"
                s += "\n"
            elif file.endswith(".pck"):
                modelname = file[:-4]

                s += f"  {modelname}"
                if modelname not in model_desc:
                    s += f"\t  <-- missing specification in options.yaml"
                s += "\n"

        return s

    @staticmethod
    def _get_options_path(model_source_dir, model_options_file):
        if model_options_file is not None:
            model_options_file = os.path.expanduser(model_options_file)
            if not os.path.exists(model_options_file):
                raise ValueError(
                    f"supplied model options file {model_options_file} does not exist"
                )
            return model_options_file

        else:
            if model_source_dir is None:
                return None
            else:
                return os.path.join(model_source_dir, "options.yaml")

    @staticmethod
    def _load_model_options(model, options_path):
        """look up the options (just compiler kwargs right now) for the model"""

        # open yaml to get model options
        if options_path is not None:
            with open(options_path, "r") as file:
                model_desc = yaml.safe_load(file)

            if "DEFAULT" in model_desc:
                print("found DEFAULT compiler options")
                compiler_kwargs = model_desc["DEFAULT"]["compiler_kwargs"]
            else:
                compiler_kwargs = {}

            if model in model_desc:
                if "compiler_kwargs" in model_desc[model]:
                    compiler_kwargs.update(model_desc[model]["compiler_kwargs"])
        else:
            model_desc = {}
            compiler_kwargs = {}

        print("loaded the following compiler options")
        if "DEFAULT" in model_desc:
            print("(based on DEFAULT from options file)")

        for k, v in compiler_kwargs.items():
            print(f"  {k} : {v}")

        return compiler_kwargs

    @property
    def io_records_dir(self):
        return os.path.join(self.model_dir, "io_records")

    def create_shaped_input_from_wav(self, file_path: str) -> np.ndarray:
        """
        Convert an input wav file to a numpy array with the correct shape
        to run through the model. This often means converting it to a
        shape of (frames, samples) where the value of samples is the hop_size.

        file_path: input wavfile
        """
        # Load the wav file
        sampling_rate, data = wavfile.read(file_path)

        # 'sampling_rate' is the sampling rate of the wav file
        # 'data' is a numpy array containing the audio data
        print(f"Input wavfile sampling rate: {sampling_rate} data type: {data.dtype}")

        # Figure out the shape that we need by creating a fake input and reshaping
        # the real data to match this shape.
        fake_input = self.hw_runner.make_fake_inputs(1, style="random")
        if len(fake_input.keys()) != 1:
            raise (
                Exception(
                    "There is more than 1 expected input for this model so we can't pass the wavfile to it."
                )
            )

        # This just gets the first key from the dict since there should only be 1.
        input_var_name = next(iter(fake_input))

        # This is to find out the shape the input needs to be for the model
        _, samples = fake_input[input_var_name].shape

        # The first part of this line data[:len(data)//samples * samples]
        # truncates the data into something divisible by samples and
        # then we reshape to (frames, samples) to match what the model expects
        data = data[: len(data) // samples * samples].reshape(-1, samples)

        return data

    def generate_program_files(
        self, model_filename: Path | str, output_dir: Path | str = "model_datas"
    ):
        """
        Generate the program files from an input model. The input model can be an fqir or a bitfile.zip

        @params
        model_filename: the model filename which can be a model_file_name.fqir or bitfile.zip
        output_dir: top level output dir for the generated program files
        """
        if isinstance(model_filename, Path):
            model_filename = str(model_filename)
        if isinstance(output_dir, Path):
            output_dir = str(output_dir)

        self.run(model_filename, output_dir=output_dir)

    def generate_input_from_wav(self, model, wavfile_path: str | Path) -> np.ndarray:
        """ """
        if isinstance(wavfile_path, Path):
            wavfile_path = str(wavfile_path)

        self.run(model)
        return self.create_shaped_input_from_wav(wavfile_path)

    def run(
        self,
        model: str,
        model_options_file=None,
        output_dir: str = "model_datas",
        n_inputs: int = 2,
        input_file: str = None,
        input_file_sample_indices: str = None,
        force_femtocrux_compile: bool = False,
        force_femtocrux_sim: bool = False,
        hardware: str = "fakezynq",
        runners: str = "",
        debug_vars: str = None,
        debug_vars_fname: str = None,
        debug: bool = False,
        noencrypt: bool = False,
        sim_est_input_period: float = None,
        dummy_output_file: str = None,
    ):
        """
        This is the python API version of the CLI argparse arguments. The descriptions from there hold.

        Required params:
        model:                          Model to run.

        Optional:
        model_options_file:             .yaml with run options for different models (e.g., compiler options).
                                        Default is femtodriver/femtodriver/models/options.yaml
        output_dir:                     Directory where to write fasmir, fqir, programming images,
                                        programming streams, etc.
        n_inputs:                       Number of random sim inputs to drive in.
        input_file:                     File with inputs to drive in. Expects .npy from numpy.save.
                                        Expecting single 2D array of values, indices are (timestep, vector_dim)
        input_file_sample_indices:      lo, hi indices to run from input_file.
        force_femtocrux_compile:        Force femtocrux as the compiler, even if FS internal packages present.
        force_femtocrux_sim:            Force femtocrux as the simulator, even if FS internal packages present.
        hardware:                       Primary runner to use: (options: zynq, fakezynq, redis).
        runners:                        Which runners to execute. If there are multiple, compare each of them
                                        to the first, comma-separated. Options: hw, fasmir, fqir, fmir, fakehw.
        debug_vars:                     Debug variables to collect and compare values for, comma-separated
                                        (no spaces), or 'all'.
        debug_vars_fname:               File with a debug variable name on each line.
        debug:                          Set debug log level.
        noencrypt:                      Don't encrypt programming files.
        sim_est_input_period:           Simulator input period for energy estimation. No impact on runtime.
                                        Floating point seconds.
        dummy_output_file:              For fakezynq, the values that the runner should reply with.
                                        Specify a .npy for a single variable.

        """
        ## Hack to convert function args to argparse Namespace object
        #  because we need to fix how this code works
        this_functions_args = locals()
        self.args = dict_to_namespace(this_functions_args)
        # collect comparisons
        if runners == "":
            self.comparisons = []
        else:
            self.comparisons = runners.split(",")
        ########################################################

        if isinstance(model, Path):
            model = str(model)
        if isinstance(output_dir, Path):
            output_dir = str(output_dir)

        self.load_model(model)

        # now set:
        # self.modelname
        # self.fqir
        # self.fmir
        # self.fasmir

        # compile the model using ProgramHandler
        # regardless of the input type, all paths end in a metadata dir
        self.meta_dir = self.compile_model()

        # load the hardware from the metadata dir
        self.hw_runner = self.create_SPURunner(self.meta_dir)

        # run comparisons with other runners
        return self.run_comparisons(self.hw_runner, self.comparisons)

    def main(self, argv) -> int:
        self.args = self._parse_args(argv)
        args_dict = vars(self.args)

        return self.run(**args_dict)


def main(argv, model_source_dir=MODEL_SOURCE_DIR):
    fd = Femtodriver(model_source_dir=model_source_dir)
    return fd.main(argv)


def dict_to_namespace(dictionary: dict):
    """Convert a dictionary to an argparse.Namespace object."""
    namespace = argparse.Namespace()
    for key, value in dictionary.items():
        setattr(namespace, key, value)
    return namespace


if __name__ == "__main__":
    fd = Femtodriver()
    exit(fd.main(sys.argv[1:]))
