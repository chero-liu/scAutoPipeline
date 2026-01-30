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
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"路径不存在: {directory_path}")
    
    fastq_files = glob.glob(os.path.join(directory_path, "*.fastq.gz"))
    
    if not fastq_files:
        raise ValueError(f"在路径 {directory_path} 中未找到.fastq.gz文件")
    
    classified_files = {
        "cDNAfastq1": [],
        "cDNAfastq2": [],
        "oligofastq1": [],
        "oligofastq2": []
    }
    
    for file_path in fastq_files:
        filename = file_path
        if "oligo" in filename:
            if "_R1_" in filename:
                classified_files["oligofastq1"].append(filename)
            elif "_R2_" in filename:
                classified_files["oligofastq2"].append(filename)
        else:
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
