import os
import sys
import unittest
from scAutoPipeline.tools.M2.clustering import Clustering
from scAutoPipeline.tools.utils import (
    Step,
    s_common,
    read_yaml,
    get_analysis,
    check_none,
    get_all_folders,
)


class Module2(Step):
    def __init__(self, args):
        super().__init__(args)
        self.cwd = os.getcwd()
        self.input = (
            args.outdir + "/config/cfgM2.yaml"
            if args.input != "./config/cfgM2.yaml"
            else args.input
        )

        self.data = read_yaml(self.input)
        self.analysis_list = get_analysis(self.data["analysis"])
        self.module = self.data["module"]
        self.programID = self.data["programID"]
        self.species = self.data["species"]
        self.types = self.data["param"]["types"]

        self.thread = 8 if args.thread == None else int(args.thread)

    def clustering(self, type, input):
        with Clustering(
            data=self.data,
            type=type,
            analysis="clustering",
            input=input,
        ) as runner:
            runner.run()

    def run(self):
        # check required parameters
        if check_none(
            self.programID,
            self.species,
        ):
            sys.exit("Error: ProgramID , species and type are required.")

        if self.types:
            if isinstance(self.types, list):
                for type in self.types:
                    if "clustering" in self.analysis_list:
                        self.clustering(type=type)
            else:
                if "clustering" in self.analysis_list:
                    self.clustering(type=self.types)
        else:
            all_folders = get_all_folders(self.data["param"]["input"])
            for type in all_folders:
                if "clustering" in self.analysis_list:
                    self.clustering(
                        type,
                        os.path.join(
                            self.data["param"]["input"],
                            type,
                            "qc",
                            "filtered.h5ad",
                        ),
                    )


def M2(args):
    with Module2(args) as runner:
        runner.run()


def get_opts_M2(parser, sub_program=True):
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default="./config/cfgM1.yaml",
        help="path of cfgM1.yaml",
    )

    if sub_program:
        parser = s_common(parser)

    return parser


if __name__ == "__main__":
    unittest.main()
