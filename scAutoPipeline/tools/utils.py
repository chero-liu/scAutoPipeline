import importlib
import os
from scAutoPipeline.__init__ import ROOT_PATH
import abc
import sys
from scAutoPipeline.config.config import DATABASE
import yaml

import random

random_number = random.randint(10000, 99999)


def find_assay_init(assay):
    init_module = importlib.import_module(f"scAutoPipeline.{assay}.__init__")
    return init_module


def find_step_module(assay, step):
    file_path_dict = {
        "assay": f"{ROOT_PATH}/{assay}/{step}.py",
        "tools": f"{ROOT_PATH}/tools/{step}.py",
    }

    init_module = find_assay_init(assay)

    if os.path.exists(file_path_dict["assay"]):
        step_module = importlib.import_module(f"scAutoPipeline.{assay}.{step}")
    elif hasattr(init_module, "IMPORT_DICT") and step in init_module.IMPORT_DICT:
        module_path = init_module.IMPORT_DICT[step]
        step_module = importlib.import_module(f"{module_path}.{step}")
    elif os.path.exists(file_path_dict["tools"]):
        step_module = importlib.import_module(f"scAutoPipeline.tools.{step}")
    else:
        raise ModuleNotFoundError(f"No module found for {assay}.{step}")

    return step_module


class Step:
    """
    Step class with integrated logging support
    """

    def __init__(self, args):
        self.args = args
        self.outdir = args.outdir
        self.prefix = args.prefix
        self.species = args.species
        # self.assay = args.subparser_assay
        self.thread = args.thread

    @abc.abstractmethod
    def run(self):
        sys.exit("Please implement run() method.")

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        print("bye")


def s_common(parser):
    """subparser common arguments"""
    parser.add_argument("-o", "--outdir", default="./", help="Output diretory.")
    parser.add_argument(
        "-p",
        "--prefix",
        default=None,
        help="Prefix of all output files.",
    )
    parser.add_argument("-s", "--species", help="Species")
    parser.add_argument("--thread", help="", default=None)

    return parser


class ModuleFun:
    """
    Module class
    """

    def __init__(self, data, input, analysis):
        self,
        self.cwd = os.getcwd()
        self.data = data
        self.input = input
        self.analysis = analysis

        self.module = self.data["module"]
        self.script = DATABASE["pipelines"][self.module]["tools"][self.analysis][
            "script"
        ]
        self.environment = DATABASE["pipelines"][self.module]["tools"][self.analysis][
            "environment"
        ]
        self.outdir = os.path.join(self.cwd, "result", self.data["module"])
        self.prefix = self.data["param"]["prefix"]
        self.species = self.data["species"]
        self.programID = self.data["programID"]
        self.refgenome = DATABASE["refgenome"][self.species][self.analysis][
            "index_path"
        ]
        self.thread = DATABASE["pipelines"][self.module]["tools"][self.analysis][
            "thread"
        ]

    @abc.abstractmethod
    def run(self):
        sys.exit("Please implement run() method.")

    def save_script(self, shell_script_content):
        shell_path = f"{self.cwd}/script/{self.module}/{self.prefix}_{self.analysis}_{random_number}.sh"
        with open(
            shell_path,
            "w",
        ) as file:
            file.write(shell_script_content)

        string = f"""echo sbatch -J {os.path.basename(shell_path)} -c {self.thread} --mem=64G --output={self.cwd}/script/{self.module}/logs/{os.path.basename(shell_path)}_%j.o --error={self.cwd}/script/{self.module}/logs/{os.path.basename(shell_path)}_%j.e --chdir={self.cwd} {shell_path}  >> {self.cwd}/sbatch.sh"""
        os.system(string)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        print(f"Init shell script for {self.analysis} of {self.module} finished.")


def read_yaml(file_path):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return data


def get_analysis(dic, condition=lambda x: x != 0):
    result = [key for key, value in dic.items() if condition(value)]
    if not result:
        print("No analysis found, Please select at least one valid analysis")
        sys.exit(1)
    else:
        print(f"Analysis list: {result}")
    return result


def check_none(*args):
    return any(arg is None for arg in args)
