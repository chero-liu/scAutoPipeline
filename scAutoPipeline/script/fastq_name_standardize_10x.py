import os
import re
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
import logging
import time

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FastqFileProcessor:
    """使用DeepSeek API处理fastq.gz文件的智能处理器"""

    def __init__(self, api_key: str):
        """
        初始化处理器

        Args:
            api_key: DeepSeek API密钥
        """
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def analyze_files_with_deepseek(
        self, input_path: str, file_list: List[str]
    ) -> Dict:
        """
        使用DeepSeek API分析文件命名模式

        Args:
            input_path: 输入路径
            file_list: 文件列表

        Returns:
            DeepSeek返回的处理方案
        """
        # 构造详细的提示词
        prompt = f"""
        你是专业的生物信息学文件命名专家。请分析以下fastq.gz文件，并生成重命名和组织方案。

        原始文件路径：{input_path}

        文件列表（共{len(file_list)}个文件）：
        {json.dumps(file_list, indent=2, ensure_ascii=False)}

        规则要求：
        1. 输出文件必须命名为：[样本名]_S1_L00[通道号]_[读数类型]_001.fastq.gz
        2. 每个样本需要有自己的独立文件夹
        3. 对于未知信息（如通道号），使用合理的默认值（通常是1）
        4. 读数类型通常是R1、R2、I1等，请根据文件名推断

        命名规范说明：
        - 样本名(sample_name)：通常从原始文件名中提取，如"SAMPLE1"、"TUMOR_01"等
        - 通道号(lane_number)：L001、L002等，如无法确定则用L001
        - 读数类型(read_type)：R1（读段1）、R2（读段2）、I1（index读段）

        请分析每个文件名，提取样本名、通道号和读数类型，然后生成JSON格式的处理方案。

        注意：样本名应该有意义且一致，同一组文件应有相同的样本名。

        返回的JSON必须严格遵循以下格式：
        {{
            "analysis_summary": {{
                "total_files": 数字,
                "detected_samples": ["样本1", "样本2"],
                "detected_read_types": ["R1", "R2", "I1"],
                "detected_lanes": ["1", "2"],
                "confidence": "high/medium/low"
            }},
            "processing_plan": [
                {{
                    "original_filename": "原始文件名.fastq.gz",
                    "sample_name": "推断的样本名",
                    "lane_number": "推断的通道号（如1、2）",
                    "read_type": "推断的读数类型（R1、R2、I1等）",
                    "new_filename": "按规则生成的新文件名",
                    "target_folder": "目标文件夹名（通常与样本名相同）",
                    "confidence": "high/medium/low",
                    "notes": "任何备注信息"
                }}
            ],
            "folder_structure": [
                "需要创建的文件夹路径1",
                "需要创建的文件夹路径2"
            ],
            "recommendations": [
                "给用户的建议1",
                "给用户的建议2"
            ]
        }}

        请确保：
        1. new_filename严格按照要求格式生成
        2. 同一样本的所有文件放在同一个文件夹
        3. 如果有不确定的信息，在confidence中标记为low或medium
        4. 在notes中说明推断的依据
        """

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": """你是一个专业的生物信息学专家，专门处理高通量测序文件的命名和组织。
                    你精通各种fastq文件命名规范，包括10x Genomics、Illumina等。
                    你会仔细分析文件名模式，做出合理的推断。
                    你总是返回完整、准确的JSON格式结果。""",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,  # 低温度确保确定性输出
            "max_tokens": 4000,
            "response_format": {"type": "json_object"},  # 强制JSON输出
        }

        try:
            logger.info("正在调用DeepSeek API分析文件命名...")
            response = requests.post(
                self.api_url, headers=self.headers, json=payload, timeout=120
            )
            response.raise_for_status()

            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]

            # 解析JSON响应
            try:
                processing_plan = json.loads(ai_response)
                logger.info(
                    f"DeepSeek分析完成！检测到 {len(processing_plan.get('processing_plan', []))} 个文件处理方案"
                )
                return processing_plan
            except json.JSONDecodeError as e:
                logger.error(f"解析DeepSeek响应失败: {e}")
                # 尝试从响应中提取JSON
                json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(0))
                    except:
                        pass
                raise ValueError(f"无法解析DeepSeek的JSON响应: {ai_response[:200]}...")

        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"处理DeepSeek响应时出错: {e}")
            raise

    def collect_files(self, input_path: str) -> List[Dict]:
        """
        收集指定路径下的fastq.gz文件

        Args:
            input_path: 输入路径

        Returns:
            文件信息列表
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"路径不存在: {input_path}")

        file_info = []
        fastq_extensions = [".fastq.gz", ".fq.gz", ".fastq", ".fq"]

        for root, dirs, files in os.walk(input_path):
            for file in files:
                if any(file.endswith(ext) for ext in fastq_extensions):
                    file_path = os.path.join(root, file)
                    file_info.append(
                        {
                            "original_path": file_path,
                            "filename": file,
                            "directory": root,
                            "size": os.path.getsize(file_path),
                            "modified_time": os.path.getmtime(file_path),
                        }
                    )

        if not file_info:
            raise ValueError(f"在路径 {input_path} 中未找到fastq文件")

        logger.info(f"找到 {len(file_info)} 个fastq文件")
        return file_info

    def create_soft_link(self, original_file_path, link_filepath):
        """
        创建软链接（符号链接），替代文件移动操作
        :param original_file_path: 原文件的绝对/相对路径（真实文件路径）
        :param link_filepath: 要创建的软链接路径
        """
        # 1. 校验原文件是否存在
        if not os.path.exists(original_file_path):
            raise FileNotFoundError(f"原文件不存在：{original_file_path}")

        # 2. 获取原文件的绝对路径
        original_abs_path = os.path.abspath(original_file_path)

        # 3. 若目标软链接已存在，先删除（避免报错）
        if os.path.exists(link_filepath):
            # 如果是软链接，直接删除；如果是真实文件/目录，可根据需求调整逻辑
            if os.path.islink(link_filepath):
                os.unlink(link_filepath)
                logger.info(f"删除已存在的软链接: {link_filepath}")
            else:
                # 如果是真实文件，重命名备份而不是报错
                backup_path = link_filepath + ".backup_" + str(int(time.time()))
                os.rename(link_filepath, backup_path)
                logger.warning(f"目标路径已存在，已备份到: {backup_path}")

        # 4. 确保目标目录存在
        os.makedirs(os.path.dirname(link_filepath), exist_ok=True)

        # 5. 创建软链接（核心操作）
        try:
            os.symlink(original_abs_path, link_filepath)
            logger.info(f"软链接创建成功: {link_filepath} -> {original_abs_path}")
            return True
        except Exception as e:
            logger.error(f"创建软链接失败: {link_filepath}, 错误: {e}")
            raise

    def execute_processing_plan(
        self,
        input_path: str,
        processing_plan: Dict,
        output_path: Optional[str] = None,
    ) -> Dict:
        """
        执行DeepSeek生成的处理方案

        Args:
            input_path: 输入路径
            processing_plan: 处理方案
            output_path: 输出路径，如果为None则使用input_path

        Returns:
            执行结果
        """
        # 设置输出路径
        if output_path is None:
            output_path = input_path

        # 验证处理方案
        if not processing_plan or "processing_plan" not in processing_plan:
            logger.error("无效的处理方案")
            return {
                "input_path": input_path,
                "output_path": output_path,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "error": "无效的处理方案",
                "processed_files": [],
                "created_folders": [],
                "errors": ["处理方案格式不正确"],
                "warnings": [],
                "summary": {},
            }

        # 预收集所有文件，避免重复遍历
        file_info = self.collect_files(input_path)
        file_dict = {f["filename"]: f["original_path"] for f in file_info}

        results = {
            "input_path": input_path,
            "output_path": output_path,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "processed_files": [],
            "created_folders": [],
            "errors": [],
            "warnings": [],
            "summary": {},
        }

        # 1. 创建文件夹结构
        if "folder_structure" in processing_plan:
            for folder_rel in processing_plan["folder_structure"]:
                folder_path = os.path.join(output_path, folder_rel)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path, exist_ok=True)
                    results["created_folders"].append(folder_path)
                    logger.info(f"创建文件夹: {folder_path}")
                else:
                    logger.debug(f"文件夹已存在: {folder_path}")

        # 2. 处理文件重命名和移动
        if "processing_plan" in processing_plan:
            for plan_item in processing_plan["processing_plan"]:
                try:
                    original_filename = plan_item.get("original_filename")
                    if not original_filename:
                        results["errors"].append("处理方案中缺少original_filename")
                        continue

                    # 查找原始文件
                    original_file_path = file_dict.get(original_filename)
                    if not original_file_path:
                        # 如果没找到，尝试在子目录中查找
                        for root, dirs, files in os.walk(input_path):
                            if original_filename in files:
                                original_file_path = os.path.join(
                                    root, original_filename
                                )
                                break

                    if not original_file_path:
                        error_msg = f"未找到文件: {original_filename}"
                        results["errors"].append(error_msg)
                        logger.warning(error_msg)
                        continue

                    # 获取新文件名和路径
                    sample_name = plan_item.get("sample_name", "unknown_sample")
                    lane_number = plan_item.get("lane_number", "1")
                    read_type = plan_item.get("read_type", "R1")

                    # 确保lane_number是两位数字
                    lane_str = str(lane_number).zfill(2)

                    # 生成新文件名
                    new_filename = plan_item.get(
                        "new_filename",
                        f"{sample_name}_S1_L00{lane_str}_{read_type}_001.fastq.gz",
                    )

                    # 目标文件夹
                    target_folder_name = plan_item.get("target_folder", sample_name)
                    target_folder = os.path.join(output_path, target_folder_name)
                    new_filepath = os.path.join(target_folder, new_filename)

                    # 验证新文件名格式
                    if not self.validate_filename_format(new_filename):
                        warning_msg = f"新文件名格式可能不正确: {new_filename}"
                        results["warnings"].append(warning_msg)
                        logger.warning(warning_msg)

                    # 执行操作
                    operation_info = {
                        "original_file": original_filename,
                        "original_path": original_file_path,
                        "new_filename": new_filename,
                        "new_path": new_filepath,
                        "sample_name": sample_name,
                        "lane_number": lane_number,
                        "read_type": read_type,
                        "confidence": plan_item.get("confidence", "unknown"),
                        "notes": plan_item.get("notes", ""),
                    }

                    # 确保目标文件夹存在
                    os.makedirs(target_folder, exist_ok=True)

                    # 移动并重命名文件
                    try:
                        self.create_soft_link(original_file_path, new_filepath)
                    except Exception as e:
                        logger.error(f"创建软链接失败：{e}")
                        results["errors"].append(
                            f"创建软链接失败：{original_filename} -> {new_filename}: {str(e)}"
                        )
                        continue

                    logger.info(f"[执行] 已处理: {original_filename} -> {new_filename}")

                    results["processed_files"].append(operation_info)

                except Exception as e:
                    error_msg = f"处理文件 {plan_item.get('original_filename', 'unknown')} 时出错: {str(e)}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg, exc_info=True)

        # 3. 生成总结报告
        results["summary"] = {
            "total_files_processed": len(results["processed_files"]),
            "unique_samples_created": (
                len(set(f["sample_name"] for f in results["processed_files"]))
                if results["processed_files"]
                else 0
            ),
            "folders_created": len(results["created_folders"]),
            "errors_count": len(results["errors"]),
            "warnings_count": len(results["warnings"]),
            "analysis_summary": processing_plan.get("analysis_summary", {}),
        }

        # 4. 输出详细报告
        self.generate_report(results, processing_plan)

        return results

    def validate_filename_format(self, filename: str) -> bool:
        """
        验证文件名是否符合要求格式

        支持格式：
        - SAMPLE_S1_L001_R1_001.fastq.gz
        - SAMPLE_S1_L001_I1_001.fastq.gz
        - SAMPLE_S1_L001_R2_001.fastq.gz

        Args:
            filename: 文件名

        Returns:
            是否符合格式
        """
        # 更宽松的匹配，允许样本名包含下划线
        pattern = r"^.+_S\d+_L\d+_[RI]\d+_001\.(fastq|fq)(\.gz)?$"
        return bool(re.match(pattern, filename))

    def generate_report(self, results: Dict, processing_plan: Dict):
        """
        生成处理报告

        Args:
            results: 处理结果
            processing_plan: 原始处理方案
        """
        logger.info("\n" + "=" * 60)
        logger.info("文件处理完成报告")
        logger.info("=" * 60)

        summary = results["summary"]
        logger.info(f"处理时间: {results['timestamp']}")
        logger.info(f"输入路径: {results['input_path']}")
        logger.info(f"处理文件总数: {summary['total_files_processed']}")
        logger.info(f"创建的样本文件夹数: {summary['unique_samples_created']}")
        logger.info(f"新建文件夹数: {summary['folders_created']}")
        logger.info(f"错误数: {summary['errors_count']}")
        logger.info(f"警告数: {summary['warnings_count']}")

        # 显示分析总结
        if "analysis_summary" in processing_plan:
            analysis = processing_plan["analysis_summary"]
            logger.info("\nDeepSeek分析总结:")
            logger.info(
                f"  检测到的样本: {', '.join(analysis.get('detected_samples', []))}"
            )
            logger.info(
                f"  检测到的读数类型: {', '.join(analysis.get('detected_read_types', []))}"
            )
            logger.info(
                f"  检测到的通道: {', '.join(analysis.get('detected_lanes', []))}"
            )
            logger.info(f"  分析置信度: {analysis.get('confidence', 'unknown')}")

        # 显示推荐
        if "recommendations" in processing_plan and processing_plan["recommendations"]:
            logger.info("\nDeepSeek推荐:")
            for i, rec in enumerate(processing_plan["recommendations"], 1):
                logger.info(f"  {i}. {rec}")

        # 显示错误和警告
        if results["errors"]:
            logger.info("\n错误列表:")
            for error in results["errors"]:
                logger.error(f"  - {error}")

        if results["warnings"]:
            logger.info("\n警告列表:")
            for warning in results["warnings"]:
                logger.warning(f"  - {warning}")

        logger.info("=" * 60)

    def process_fastq_files(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        max_retries: int = 2,
    ) -> Dict:
        """
        主处理函数：使用DeepSeek API智能处理fastq文件

        Args:
            input_path: 输入路径
            output_path: 输出路径，如果为None则使用input_path
            max_retries: API调用重试次数

        Returns:
            处理结果
        """
        logger.info(f"开始处理路径: {input_path}")

        try:
            # 验证输入路径
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"输入路径不存在: {input_path}")

            # 1. 收集文件
            file_info = self.collect_files(input_path)
            file_list = [f["filename"] for f in file_info]

            # 2. 调用DeepSeek API分析文件
            processing_plan = None
            for attempt in range(max_retries):
                try:
                    processing_plan = self.analyze_files_with_deepseek(
                        input_path, file_list
                    )
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"API调用失败，第{attempt+1}次重试...")
                        time.sleep(2)
                    else:
                        logger.error(f"API调用失败，已达到最大重试次数: {e}")
                        raise

            if not processing_plan:
                raise ValueError("无法获取有效的处理方案")

            # 3. 显示处理方案预览
            logger.info("\nDeepSeek生成的处理方案预览:")
            if "processing_plan" in processing_plan:
                for i, plan in enumerate(
                    processing_plan["processing_plan"][:3], 1
                ):  # 只显示前3个
                    logger.info(
                        f"  {i}. {plan.get('original_filename')} -> {plan.get('new_filename')}"
                    )
                if len(processing_plan["processing_plan"]) > 3:
                    logger.info(
                        f"  ... 还有{len(processing_plan['processing_plan']) - 3}个文件"
                    )

            # 4. 执行处理方案
            results = self.execute_processing_plan(
                input_path=input_path,
                processing_plan=processing_plan,
                output_path=output_path,
            )

            return results

        except Exception as e:
            logger.error(f"处理过程失败: {e}", exc_info=True)
            return {
                "error": str(e),
                "input_path": input_path,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "processed_files": [],
                "created_folders": [],
                "errors": [str(e)],
                "warnings": [],
                "summary": {},
            }


def process_fastq_directory(
    input_path: str,
    api_key: str = "sk-dc704c6bb6bb42f896734498d7f51fdc",
    output_path: Optional[str] = None,
):
    """
    处理fastq目录的主函数

    Args:
        input_path: 输入路径
        api_key: DeepSeek API密钥
        output_path: 输出路径，如果为None则使用input_path
    """
    # 验证API密钥格式
    if not api_key.startswith("sk-"):
        print("错误: API密钥格式不正确，应以'sk-'开头")
        return

    # 创建处理器
    processor = FastqFileProcessor(api_key=api_key)

    try:
        # 执行处理
        results = processor.process_fastq_files(
            input_path=input_path,
            output_path=output_path,
        )

        # 确定日志文件保存路径
        log_dir = output_path if output_path else input_path
        log_file = os.path.join(log_dir, f"processing_log_{int(time.time())}.json")
        with open(log_file, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n处理日志已保存到: {log_file}")

        if "error" in results:
            print(f"\n处理失败: {results['error']}")
        else:
            print(
                f"\n处理完成！总计处理 {results['summary']['total_files_processed']} 个文件"
            )

    except Exception as e:
        print(f"处理过程中发生错误: {e}")


# 命令行接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="使用DeepSeek API智能处理fastq.gz文件")
    parser.add_argument("input_path", help="输入文件路径")
    parser.add_argument("--api-key", required=True, help="DeepSeek API密钥")
    parser.add_argument("--outdir", help="输出目录路径，如果不指定则使用输入路径")

    args = parser.parse_args()

    print("=" * 60)
    print("DeepSeek Fastq文件智能处理器")
    print("=" * 60)

    # 执行处理
    process_fastq_directory(
        input_path=args.input_path,
        api_key=args.api_key,
        output_path=args.outdir,
    )

# python fastq_processor_10x.py /nas/projects/scrna/10x/test20260122/config/raw_data/20260115_2 --api-key sk-dc704c6bb6bb42f896734498d7f51fdc
