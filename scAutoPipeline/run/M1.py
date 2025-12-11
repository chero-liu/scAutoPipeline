import os
import sys
import unittest
from scAutoPipeline.tools.M1.dnbc4tools import DNBC4tools
from scAutoPipeline.tools.utils import (
    Step,
    s_common,
    read_yaml,
    get_analysis,
    check_none,
)


class Module1(Step):
    def __init__(self, args):
        super().__init__(args)
        self.cwd = os.getcwd()
        self.input = (
            args.outdir + "/config/cfgM1.yaml"
            if args.input != "./config/cfgM1.yaml"
            else args.input
        )

        self.data = read_yaml(self.input)
        self.analysis_list = get_analysis(self.data["analysis"])
        self.module = self.data["module"]
        self.programID = self.data["programID"]
        self.species = self.data["species"]

        self.thread = 8 if args.thread == None else int(args.thread)

    def dnbc4tools(self):
        with DNBC4tools(
            data=self.data,
            analysis="dnbc4tools",
            input=self.data["param"]["input"],
        ) as runner:
            runner.run()

    def run(self):
        # check required parameters
        if check_none(
            self.programID,
            self.species,
        ):
            sys.exit("Error: ProgramID , species and type are required.")

        self.dnbc4tools()


def M1(args):
    with Module1(args) as runner:
        runner.run()


def get_opts_M1(parser, sub_program=True):
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
