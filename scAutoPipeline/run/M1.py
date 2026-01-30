import os
import sys
import unittest
from scAutoPipeline.tools.M1.dnbc4tools import DNBC4tools
from scAutoPipeline.tools.M1.cellranger import CellRanger
from scAutoPipeline.tools.M1.fastp import Fastp
from scAutoPipeline.tools.M1.qc import QC
from scAutoPipeline.tools.utils import (
    Step,
    s_common,
    read_yaml,
    get_analysis,
    check_none,
    get_all_folders,
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
        self.types = self.data["param"]["types"]

        self.thread = 8 if args.thread == None else int(args.thread)

    def cellranger(self, type):
        with CellRanger(
            data=self.data,
            type=type,
            analysis="cellranger",
            input=self.data["param"]["input"],
        ) as runner:
            runner.run()

    def dnbc4tools(self,type):
        with DNBC4tools(
            data=self.data,
            analysis="dnbc4tools",
            input=self.data["param"]["input"],
            type=type,
        ) as runner:
            runner.run()

    def fastp(self, type):
        with Fastp(
            data=self.data,
            type=type,
            analysis="fastp",
            input=self.data["param"]["input"],
        ) as runner:
            runner.run()

    def qc(self, input, type, upstream):
        with QC(
            data=self.data,
            input=input,
            type=type,
            upstream=upstream,
            analysis="qc",
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
                    if "cellranger" in self.analysis_list:
                        self.cellranger(type=type)

                    if "dnbc4tools" in self.analysis_list:
                        self.dnbc4tools(type=type)

                    if "fastp" in self.analysis_list:
                        self.fastp(type=type)

                    if "qc" in self.analysis_list:
                        if "cellranger" in self.analysis_list:
                            input = f"{self.cwd}/result/M1/{type}/cellranger/info.csv"
                            upstream = "cellranger"
                        elif "dnbc4tools" in self.analysis_list:
                            input = f"{self.cwd}/result/M1/{type}/dnbc4tools/info.csv"
                            upstream = "dnbc4tools"
                        else:
                            input = self.data["param"]["input"]
                            upstream = None
                        self.qc(
                            type=type,
                            input=input,
                            upstream=upstream,
                        )
            else:
                if "cellranger" in self.analysis_list:
                    self.cellranger(type=self.types)

                if "dnbc4tools" in self.analysis_list:
                    self.dnbc4tools(self.types)

                if "fastp" in self.analysis_list:
                    self.fastp(type=self.types)

                if "qc" in self.analysis_list:
                    if "cellranger" in self.analysis_list:
                        input = f"{self.cwd}/result/M1/{self.types}/cellranger/info.csv"
                        upstream = "cellranger"
                    elif "dnbc4tools" in self.analysis_list:
                        input = f"{self.cwd}/result/M1/{self.types}/dnbc4tools/info.csv"
                        upstream = "dnbc4tools"
                    else:
                        input = self.data["param"]["input"]
                        upstream = None
                    self.qc(
                        input=input,
                        type=self.types,
                        upstream=upstream,
                    )
        else:
            all_folders = get_all_folders(self.data["param"]["input"])
            if len(all_folders) == 0:
                exit('input 不存在 文件夹（样本）')
            for type in all_folders:
                if "cellranger" in self.analysis_list:
                    self.cellranger(type)

                if "dnbc4tools" in self.analysis_list:
                    self.dnbc4tools(type)

                if "fastp" in self.analysis_list:
                    self.fastp(type=type)

                if "qc" in self.analysis_list:
                    if "cellranger" in self.analysis_list:
                        input = f"{self.cwd}/result/M1/{type}/cellranger/info.csv"
                        upstream = "cellranger"
                    elif "dnbc4tools" in self.analysis_list:
                        input = f"{self.cwd}/result/M1/{type}/dnbc4tools/info.csv"
                        upstream = "dnbc4tools"
                    else:
                        input = self.data["param"]["input"]
                        upstream = None
                    self.qc(
                        type=type,
                        input=input,
                        upstream=upstream,
                    )


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
