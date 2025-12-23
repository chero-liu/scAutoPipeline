import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import numpy as np
import pyreball as pb
import json
from pathlib import Path
import pandas as pd


def extract_cellranger_stats(input_path):
    """
    收集CellRanger分析结果中的metrics_summary.csv文件，合并为一个统计表格。

    参数:
    input_path (str): CellRanger结果目录的路径，该目录下每个子目录为一个样本

    输出:
    在input_path目录下生成stats.csv文件，包含所有样本的统计信息
    """
    input_path = Path(input_path)

    # 检查输入路径是否存在
    if not input_path.exists():
        raise FileNotFoundError(f"输入路径不存在: {input_path}")

    # 获取所有样本目录（排除非目录文件）
    sample_dirs = [d for d in input_path.iterdir() if d.is_dir()]

    if not sample_dirs:
        raise ValueError(f"在路径 {input_path} 下未找到样本目录")

    all_data = []

    for sample_dir in sample_dirs:
        sample_name = sample_dir.name
        metrics_file = sample_dir / "outs" / "metrics_summary.csv"

        if not metrics_file.exists():
            print(f"警告: 样本 {sample_name} 中未找到 metrics_summary.csv，跳过")
            continue

        try:
            # 读取CSV文件
            df = pd.read_csv(metrics_file)

            # 添加样本名列
            df.insert(0, "Sample", sample_name)

            all_data.append(df)
            print(f"已处理样本: {sample_name}")

        except Exception as e:
            print(f"处理样本 {sample_name} 时出错: {e}")
            continue

    if not all_data:
        raise ValueError("未成功读取任何样本的数据")

    # 合并所有数据
    combined_df = pd.concat(all_data, ignore_index=True)

    # 输出文件路径
    output_file = input_path / "stats.csv"

    # 保存到CSV
    combined_df.to_csv(output_file, index=False)
    print(f"统计表格已保存到: {output_file}")

    return combined_df


def extract_fastp_stats(fastp_dir, output_csv=None):
    """
    Extract Fastp statistics from all_lanes.json files.

    Args:
        fastp_dir (str): Path to the Fastp directory containing sample subdirectories
        output_csv (str, optional): Output CSV file path. If not provided,
                                   defaults to 'fastp_stats.csv' in the fastp_dir.

    Returns:
        pandas.DataFrame: DataFrame containing the extracted statistics
    """
    fastp_dir = Path(fastp_dir)

    # Validate directory
    if not (fastp_dir.exists() and fastp_dir.is_dir()):
        raise FileNotFoundError(f"Fastp directory not found: {fastp_dir}")

    # Process each sample directory
    data = []
    for sample_dir in (d for d in fastp_dir.iterdir() if d.is_dir()):
        json_file = sample_dir / "all_lanes.json"

        if not json_file.exists():
            print(f"Warning: {json_file} not found")
            continue

        try:
            with open(json_file) as f:
                stats = json.load(f).get("summary", {}).get("before_filtering", {})

            if not stats:
                continue

            # Extract and compute needed metrics
            total_bases = stats.get("total_bases", 0)
            q20_bases = stats.get("q20_bases")
            q30_bases = stats.get("q30_bases")

            sample_data = {
                "sample": sample_dir.name,
                "total_reads": stats.get("total_reads"),
                "total_bases": total_bases,
                "q20_bases": q20_bases,
                "q30_bases": q30_bases,
                "q20_rate": stats.get(
                    "q20_rate",
                    q20_bases / total_bases if q20_bases and total_bases else None,
                ),
                "q30_rate": stats.get(
                    "q30_rate",
                    q30_bases / total_bases if q30_bases and total_bases else None,
                ),
                "gc_content": stats.get("gc_content"),
            }
            data.append(sample_data)
            print(f"✓ {sample_dir.name}")

        except (json.JSONDecodeError, KeyError, ZeroDivisionError) as e:
            print(f"Error processing {sample_dir.name}: {e}")

    if not data:
        print("No data extracted")
        return pd.DataFrame()

    # Create and save DataFrame
    df = pd.DataFrame(data)
    output_path = Path(output_csv or fastp_dir / "fastp_stats.csv")
    df.to_csv(output_path, index=False)

    print(f"\nSaved {len(df)} samples to: {output_path}")
    print(
        df[["sample", "total_reads", "q20_rate", "q30_rate", "gc_content"]].to_string()
    )

    return df


pjinfo_path = "/nas/projects/scrna/standard_analysis/10x/project_test/info.xls"

pjinfo = pd.read_csv(pjinfo_path, sep="\t")
pb.print(
    f'<div style="text-align: center; font-size: 35px; font-weight: bold; margin-bottom: 30px;">{pjinfo.loc[1, '合同内容']}</div>'
)
pb.print_table(
    pjinfo,
)
txt = pd.read_csv(
    "/home/chenglong.liu/RaD/scAutoPipeline/scAutoPipeline/docs/cellranger/TechnicalBackground.txt"
)

pb.print_h1("实验流程")
pb.print_div(
    "10x Genomics Chromium™系统的关键技术是利用上百万独特的Barcode标记不同的样品（长链DNA分子/单细胞）。首先，含有Barcode序列的Gel beads与样品和酶的混合物混合，然后与油表面活性剂结合形成GEMs（Gel Bead-In-Emulsions，意为包裹Gel beads，样品以及酶的混合物的油滴）。收集GEMs 流到储液器，Gel beads溶解释放Barcode序列，开始对样本进行标记。将每个液滴中含有Barcode 信息的产物混合，构建标准测序文库。"
)
pb.print_div(
    "从细胞样品提取到最终数据获得，样品检测、建库、测序等每一环节都会直接影响数据的数量和质量，从而影响后续信息分析的结果。为从源头保证测序数据准确可靠，诺禾致源承诺在数据的所有生产环节都严格把关，从根源上确保高质量数据的产出。10x Genomics Chromium™单细胞转录组整体实验流程图如下："
)

image_path = (
    "/home/chenglong.liu/RaD/scAutoPipeline/scAutoPipeline/docs/cellranger/library.png"
)
img = mpimg.imread(image_path)
fig1, ax1 = plt.subplots(figsize=(7, 1))
ax1.imshow(img)
ax1.axis("off")
pb.print_figure(fig1, caption="")
pb.print_div("单细胞转录组的应用方向主要包括以下几个方面：")
pb.print_div("细胞类型鉴定与分类")
pb.print_div("细胞发育轨迹分析")
pb.print_div("细胞间通讯分析")
pb.print_div("疾病机制研究")
pb.print_div("药物靶点发现与验证")

pb.print_h2("单细胞悬液寄送")
pb.print_div(
    "样本类型不同，处理制备方法也存在差异。客户依据样本特性进行细胞悬液制备，具体可参考10X官方样本处理建议"
)
pb.print_h2("样本质检")
pb.print_div(
    "对单细胞悬液样本进行质检，质检标准：细胞活性符合要求（AO/PI 荧光计数活性>80%或台盼蓝计数活性>75%），细胞浓度700-1200 cells/μL，细胞直径5-30μm，细胞总量可达10万个，悬液背景干净，无明显碎片或杂质。达到质检要求的样本，可继续进行后续实验，否则会和客户及时沟通，确定是否进行后续的实验。"
)
pb.print_h2("反转录+建库")
pb.print_div(
    "将检测合格的细胞经洗涤、重悬，制备成合适浓度的单细胞悬液。根据目标细胞数进行相应的上样，上样后，观察GEMs是否能够正常形成，若可以，则将GEMs吸出转移到PCR管中进行反转录及文库构建。库检合格后，上机测序。"
)
pb.print_h2("上机测序")
pb.print_div(
    "10x单细胞转录组文库，采用Illumina NovaSeq PE150测序策略，推荐每个细胞测50,000-100,000条reads（最少20,000 read pairs/cell），即每个细胞测15-30M数据量。测序存在一定饱和性，适当加大测序数据量可提高基因的检出率。"
)


pb.print_h1("分析流程")


pb.print_div(
    "获得原始测序序列(Sequenced Reads)后，通过如下流程进行生物信息分析。单细胞转录组的分析核心是细胞的分群和亚群差异基因的鉴定，使用10X官方分析软件Cell Ranger对细胞进行分型和差异分析，后续对这些差异基因进行功能富集，从而鉴定亚群的功能特征。"
)


image_path = "/home/chenglong.liu/RaD/scAutoPipeline/scAutoPipeline/docs/cellranger/pipeline3.0.1.png"
img = mpimg.imread(image_path)
fig1, ax1 = plt.subplots(figsize=(7, 5))
ax1.imshow(img)
ax1.axis("off")
pb.print_figure(fig1, caption="")


pb.print_div(
    "单细胞研究部致力于单细胞数据挖掘，为您提供不同的视角理解单细胞水平的生物学现象。目前单细胞数据挖掘工具日益丰富，在探索性的标准分析之后我们为您提供更多选择："
)
image_path = "/home/chenglong.liu/RaD/scAutoPipeline/scAutoPipeline/docs/cellranger/pipeline3.0.2.png"
img = mpimg.imread(image_path)
fig1, ax1 = plt.subplots(figsize=(7, 5))
ax1.imshow(img)
ax1.axis("off")
pb.print_figure(fig1, caption="")


pb.print_h1("质控分析")
pb.print_h2("原始测序数据说明")

pb.print_div(
    "高通量测序（如Illumina HiSeq PE125/PE150）下机得到的原始图像文件经CASAVA碱基识别转化为测序读段（Sequenced Reads），以FASTQ格式存储。FASTQ是一种存储生物序列及相应质量值的常用文本格式，以Illumina HiSeq PE150测序数据为例，双端长度均为150bp，10x文库read1的前26bp为细胞barcode和UMI信息，是区分read2来自哪个细胞的重要依据，26bp后的碱基为非有效数据，read2均为有效数据。"
)
pb.print_div("fastq格式文件中每个read由四行描述信息组成，如下所示：")


pb.print_div(
    "@ST-E00310:278:HF3GJALXX:5:1101:6745:1924 1:N:0:ACGCTCGA  TTTGGGCCCTTGGCAATGAATGTTGCCACCACTGTTCTGGGTGCAGAGGGGAAATGGAA&lt-FJFJ7J&ltJJFFJJFJJJ&ltFJJJJJJJJFJJJJFJJJJJAFJ7FJJJJ  @ST-E00310:278:HF3GJALXX:5:1101:6908:1924 1:N:0:ACGCTCGA"
)
pb.print_div(
    "上述文件中第一行以“@”开头，随后为Illumina测序标识符(Squence Identifiers)和描述文字；第二行是测序片段的碱基序列；第三行以“+”开头，随后为Illumina测序标识符(也可为空)；第四行是测序片段每个碱基相对应的测序质量值，该行中每个字符对应的ASCII值减去33，即为该碱基的测序质量值。"
)


pb.print_h2("RawData数据质量评估")
pb.print_div(
    "通过测序可以获得海量的数据信息，如何从得到的数据中获取合格的数据是信息分析的基础。因此对下机数据进行质量控制（QC）是数据分析的首项内容。fastp是目前常用的数据质量评估软件。采用fastp对下机后的数据（raw reads）质量进行基本的统计。原始下机数据根据index，lane或测序的时间不同，统一按照样本名称-1,2,3,4...依次排序命名，R1、R2为样品的read1和read2。数据质量会直接影响后续信息分析的结果。统计原始数据的质量和产出情况，汇总结果如下表所示："
)

df = extract_fastp_stats(
    "/nas/projects/scrna/standard_analysis/10x/project_test/result/M1/Fastp",
)
pb.print_table(df)

pb.print_div("sample：样品名称")
pb.print_div("total_reads：原始数据中的read pairs数")
pb.print_div("total_bases：原始数据的碱基数")
pb.print_div("q20_rate：Phred数值大于20的碱基占总碱基的百分比")
pb.print_div("q30_rate：Phred数值大于30的碱基占总碱基的百分比")
pb.print_div("gc_content：raw reads中G与C占四种碱基的百分比")


pb.print_h2("数据统计")
pb.print_div(
    "Cell Ranger是由10x genomic公司官方提供的专门用于其单细胞转录组数据分析的软件包。Cell Ranger将前面产生的fastq测序数据比对到参考基因组上进行细胞和UMI计数，生成细胞-基因表达矩阵。"
)

pb.print_div("（1）比对")
pb.print_div(
    "Cell Ranger使用的比对软件是star，将reads比对到参考基因组上后使用GTF注释文件进行校正，并区分出外显子区、内含子区、基因间区。具体的区分规则为：至少50% 比对到外显子上reads记为外显子区、将比对到非外显子区且与内含子区有交集的reads记为内含子区、除此之外均为基因间区。具体算法可参考10X官网。"
)

pb.print_div("（2）细胞计数")
pb.print_div(
    "Cell Ranger能够通过输入数据的barcode将每个细胞的reads区分出来，经过过滤筛选处理将统计出样品中的细胞数量、细胞的reads数和检测到的基因数。Cell Ranger 首先指定一个期望细胞数(N，默认为3000)，然后将barcodes按照各自的UMI总数由高到低进行排序，取前N个UMI数值的99%分位数为最大估算UMI总数(m)，将UMI数目超过m/10的barcodes作为最终捕获到的细胞。当有多个参考基因组（如人H和鼠M）时，Cell Ranger可以通过多基因组分析区分多物种混合建库的样品，主要根据barcode内每个物种对应的UMI数量进行区分，将其分成H和M两类。最后还会根据H，M各自UMI的分布和最大似然估计法估计多细胞比例(multiplet rate)，即(H,M)、(H,H)、(M,M)三种类型的多细胞占比。"
)
pb.print_div(
    "Cell Ranger 3.0引入了一种改进的细胞计数算法，该算法能够更好地识别低RNA含量的细胞群体，特别是当低RNA含量的细胞与高RNA含量的细胞混合时。该算法分为两步：第一步用上面的方法确定高RNA含量的barcode；在第二步中，选择一组具有低UMI计数的barcode，这些barcode可能表示“空的”GEM分区，建立RNA图谱背景模型。利用Simple Good-Turing smoothing平滑算法，对典型空GEM集合中未观测到的基因进行非零模型估计。最后，将第一步中未作为细胞计数的barcode RNA图谱与背景模型进行比较，其RNA谱与背景模型存在较大差异的barcode用于低RNA含量的细胞计数。当有多个参考基因组（如人H和鼠M）时，Cell Ranger可以通过多基因组分析区分多物种混合建库的样品，主要根据barcode内每个物种对应的UMI数量进行区分，将其分成H和M两类。最后还会根据H，M各自UMI的分布和最大似然估计法估计多细胞比例(multiplet rate)，即(H,M)、(H,H)、(M,M)三种类型的多细胞占比。"
)

pb.print_div(
    "基于Cell Ranger进行基本的数据分析，主要结果包括：实验捕获的细胞数目统计、检测到的gene数目统计、测序数据的产出和质量统计、参考基因组比对情况等。该项目每个样本的统计结果如下："
)

df = extract_cellranger_stats(
    "/nas/projects/scrna/standard_analysis/10x/project_test/result/M1/CellRanger",
)
pb.print_table(df)
# Sample	Estimated Number of Cells	Mean Reads per Cell	Median Genes per Cell	Number of Reads	Valid Barcodes	Valid UMI Sequences	Sequencing Saturation	Q30 Bases in Barcode	Q30 Bases in RNA Read	Q30 Bases in UMI	Reads Mapped to Genome	Reads Mapped Confidently to Genome	Reads Mapped Confidently to Intergenic Regions	Reads Mapped Confidently to Intronic Regions	Reads Mapped Confidently to Exonic Regions	Reads Mapped Confidently to Transcriptome	Reads Mapped Antisense to Gene	Fraction Reads in Cells	Total Genes Detected	Median UMI Counts per Cell
pb.print_div("Sample：样本名称")
pb.print_div("Estimated Number of Cells：估计的细胞数量")
pb.print_div("Mean Reads per Cell：每个细胞的平均reads数")
pb.print_div("Median Genes per Cell：每个细胞检测到的基因数中位数")
pb.print_div("Number of Reads：测序总reads数")
pb.print_div("Valid Barcodes：有效barcode的百分比")
pb.print_div("Valid UMI Sequences：有效UMI序列的百分比")
pb.print_div("Sequencing Saturation：测序饱和度")
pb.print_div("Q30 Bases in Barcode：barcode区域Q30碱基的百分比")
pb.print_div("Q30 Bases in RNA Read：RNA read区域Q30碱基的百分比")
pb.print_div("Q30 Bases in UMI：UMI区域Q30碱基的百分比")
pb.print_div("Reads Mapped to Genome：比对到基因组的reads百分比")
pb.print_div("Reads Mapped Confidently to Genome：可靠比对到基因组的reads百分比")
pb.print_div(
    "Reads Mapped Confidently to Intergenic Regions：可靠比对到基因间区的reads百分比"
)
pb.print_div(
    "Reads Mapped Confidently to Intronic Regions：可靠比对到内含子区的reads百分比"
)
pb.print_div(
    "Reads Mapped Confidently to Exonic Regions：可靠比对到外显子区的reads百分比"
)
pb.print_div("Reads Mapped Confidently to Transcriptome：可靠比对到转录组的reads百分比")
pb.print_div("Reads Mapped Antisense to Gene：比对到基因反义链的reads百分比")
pb.print_div("Fraction Reads in Cells：细胞内reads的比例")
pb.print_div("Total Genes Detected：检测到的基因总数")
pb.print_div("Median UMI Counts per Cell：每个细胞UMI计数的中位数")
