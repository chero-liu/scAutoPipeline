import importlib
import os
from scAutoPipeline.__init__ import ROOT_PATH
import abc
import sys
from scAutoPipeline.config.config import DATABASE
import yaml


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

    def __init__(self, data, input, analysis, upstream=None):
        self,
        self.cwd = os.getcwd()
        self.data = data
        self.input = input
        self.analysis = analysis
        self.upstream = upstream

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
        if "10x" in self.input:
            self.refgenome = DATABASE["refgenome"][self.species]["cellranger"][
                "index_path"
            ]
        elif "c4" in self.input:
            self.refgenome = DATABASE["refgenome"][self.species]["dnbc4tools"][
                "index_path"
            ]
        else:
            print(self.input)
            print("input路径必须包含测序平台")
        self.thread = DATABASE["pipelines"][self.module]["tools"][self.analysis][
            "thread"
        ]

    @abc.abstractmethod
    def run(self):
        sys.exit("Please implement run() method.")

    # def save_script(self, shell_script_content):
    #     shell_path = f"{self.cwd}/script/{self.module}/{self.analysis}_{self.prefix}.sh"
    #     with open(
    #         shell_path,
    #         "w",
    #     ) as file:
    #         file.write(shell_script_content)

    #     string = f"""echo sbatch -J {os.path.basename(shell_path)} -c {self.thread} --mem=64G --output={self.cwd}/script/{self.module}/logs/{os.path.basename(shell_path)}_%j.o --error={self.cwd}/script/{self.module}/logs/{os.path.basename(shell_path)}_%j.e --chdir={self.cwd} {shell_path}  >> {self.cwd}/sbatch.sh"""
    #     os.system(string)

    def save_script(self, shell_script_content):
        shell_path = f"{self.cwd}/script/{self.module}/{self.analysis}_{self.prefix}.sh"

        # 保存脚本文件
        with open(shell_path, "w") as file:
            file.write(shell_script_content)

        if self.upstream:
            sbatch_line = (
                f"{self.analysis}_{self.prefix}_ID=$(sbatch --dependency=afterok:${self.upstream}_{self.prefix}_ID "
                f"-J {os.path.basename(shell_path)} "
                f"-c {self.thread} --mem=64G "
                f"--output={self.cwd}/script/{self.module}/logs/{os.path.basename(shell_path)}_%j.o "
                f"--error={self.cwd}/script/{self.module}/logs/{os.path.basename(shell_path)}_%j.e "
                f"--chdir={self.cwd} "
                f"{shell_path} | awk '{{print $4}}')\n"
            )
        else:
            sbatch_line = (
                f"{self.analysis}_{self.prefix}_ID=$(sbatch -J {os.path.basename(shell_path)} "
                f"-c {self.thread} --mem=64G "
                f"--output={self.cwd}/script/{self.module}/logs/{os.path.basename(shell_path)}_%j.o "
                f"--error={self.cwd}/script/{self.module}/logs/{os.path.basename(shell_path)}_%j.e "
                f"--chdir={self.cwd} "
                f"{shell_path} | awk '{{print $4}}')\n"
            )

        with open(f"{self.cwd}/sbatch.sh", "a") as f:
            f.write(sbatch_line)

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

import os
import glob

def classify_fastq_files(directory_path):
    """
    根据文件名分类FASTQ文件
    
    参数:
    directory_path: 包含FASTQ文件的目录路径
    
    返回:
    dict: 包含分类后的文件名字典
    """
    # 确保路径存在
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"路径不存在: {directory_path}")
    
    # 获取所有fastq.gz文件
    fastq_files = glob.glob(os.path.join(directory_path, "*.fastq.gz"))
    
    if not fastq_files:
        raise ValueError(f"在路径 {directory_path} 中未找到.fastq.gz文件")
    
    # 初始化分类字典
    classified_files = {
        "cDNAfastq1": [],
        "cDNAfastq2": [],
        "oligofastq1": [],
        "oligofastq2": []
    }
    
    for file_path in fastq_files:
        # 获取文件名（不含路径）
        filename = os.path.basename(file_path)
        
        # 判断文件类型
        if "oligo" in filename:
            if "_R1_" in filename:
                classified_files["oligofastq1"].append(filename)
            elif "_R2_" in filename:
                classified_files["oligofastq2"].append(filename)
        else:
            # cDNA文件（不包含"oligo"）
            if "_R1_" in filename:
                classified_files["cDNAfastq1"].append(filename)
            elif "_R2_" in filename:
                classified_files["cDNAfastq2"].append(filename)
    
    # 对每个列表中的文件名进行排序（按字母顺序）
    for key in classified_files:
        classified_files[key].sort()
    
    # 将列表转换为逗号分隔的字符串
    result = {}
    for key, file_list in classified_files.items():
        if file_list:
            result[key] = ",".join(file_list)
        else:
            result[key] = ""  # 如果没有文件，返回空字符串
    
    return result


# 示例使用
if __name__ == "__main__":
    # 使用示例路径
    path = "/nas/projects/scrna/c4/TSE20251209-021-00003/raw_data/mc38control"
    
    try:
        result_dict = classify_fastq_files(path)
        
        # 打印结果
        print("分类结果:")
        for key, value in result_dict.items():
            print(f"{key}: {value}")
            
        # 格式化输出
        print("\n格式化输出:")
        print("{")
        for key, value in result_dict.items():
            print(f'    "{key}": "{value}",')
        print("}")
        
    except Exception as e:
        print(f"错误: {e}")


def get_all_folders(folder_path, exclude_hidden=True):
    """
    Parameters:
        folder_path (str): 目标文件夹路径
        exclude_hidden (bool): 是否排除隐藏文件夹，默认True

    Returns:
        list: 文件夹名列表，路径无效返回空列表
    """
    folder_names = []

    try:
        # 解析绝对路径
        target_dir = os.path.abspath(folder_path)

        # 校验路径有效性
        if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
            print(f"⚠️  错误：路径 '{folder_path}' 不存在或不是文件夹")
            return folder_names

        # 遍历并筛选目录
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            if os.path.isdir(item_path):
                if exclude_hidden and item.startswith("."):
                    continue
                folder_names.append(item)

    except Exception as e:
        print(f"❌ 获取文件夹列表失败：{str(e)}")

    return folder_names
