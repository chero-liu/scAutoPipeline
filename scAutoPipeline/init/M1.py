import os
import sys
import unittest
from scAutoPipeline.tools.utils import Step, s_common
from ruamel.yaml import YAML
from scAutoPipeline.config.config import DATABASE
from scAutoPipeline.init.__init__ import M1DIRECTORIES


class Module1(Step):
    def __init__(self, args):
        Step.__init__(self, args)
        # self.prefix = args.prefix
        self.input = args.input
        self.outdir = args.outdir
        self.species = args.species
        self.directory_list = M1DIRECTORIES

    def init_dirs(self):
        for directory in self.directory_list:
            dir_path = os.path.join(self.outdir, directory)
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                print(f"Failed to create directory {dir_path}: {e}")
                sys.exit(1)
        print("Directory structure initialized successfully")

    def init_yaml(self):
        yaml = YAML()

        templates_yaml = DATABASE["pipelines"]["M1"]["config_yaml"]

        with open(
            templates_yaml,
            "r",
        ) as file:
            data = yaml.load(file)

        if self.prefix:
            data["programID"] = self.prefix
            print(f"Set programID to: {self.prefix}")
        else:
            current_path = os.getcwd()
            data["programID"] = os.path.basename(current_path)
            print(f"Set programID: {data["programID"]}")
        if self.species:
            data["species"] = self.species
            print(f"Set species: {self.species}")

        output_file = os.path.join(self.outdir, "config", "cfgM1.yaml")
        with open(output_file, "w") as file:
            yaml.dump(data, file)

    def run(self):
        self.init_dirs()
        self.init_yaml()


def M1(args):
    with Module1(args) as runner:
        runner.run()


def get_opts_M1(parser, sub_program=True):
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="",
    )
    if sub_program:
        parser = s_common(parser)

    return parser


if __name__ == "__main__":
    unittest.main()
