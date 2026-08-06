import os
import unittest

from scAutoPipeline.tools.utils import Step, s_common


class UpDownTosutil(Step):
    """使用tosutil工具从OSS下载/上传数据到本地"""

    def __init__(self, args):
        super().__init__(args)
        self.input = args.input
        self.outdir = args.outdir

    def run(self):
        os.system(
            f"""
tosutil share-cp -r {self.input} {self.outdir}
            """
        )


def udtos(args):
    with UpDownTosutil(args) as runner:
        runner.run()


def get_opts_udtos(parser, sub_program=True):
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default="./",
        help="path of clean",
    )

    if sub_program:
        parser = s_common(parser)

    return parser


if __name__ == "__main__":
    unittest.main()
