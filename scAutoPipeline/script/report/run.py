import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import numpy as np
import pyreball as pb

report_name = "单细胞转录组测序数据分析报告"
sequencing_platform = "DNBelab C4"
project_id = "RAD-C4-2025"
client_name = "test_name"
species = "human"
tissue = "脑"

pb.print(
    f'<div style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 30px;">{report_name}</div>'
)

pb.print_h1("前言")
pb.print_div(
    "本报告基于DNBC4tools流程产生，旨在展示样本 alignment 和基因表达饱和度分析的核心结果。"
)

pb.print_h1("分析流程")
# 使用无序列表
pb.ulist("样本：sample1", "分析模块：M1", "比对工具：DNBC4tools")
# 使用强调文本
pb.print_div(pb.bold("注意：") + " 本报告仅展示部分分析结果，完整结果请参考附加文件。")

# 添加多级标题
pb.print_h2("详细方法")
pb.print_div("此处可填写详细的分析流程描述..." + pb.em("例如使用STAR进行比对。"))

# 内联代码高亮
pb.print_div("本次分析使用的关键参数为: " + pb.code("--outFilterMismatchNmax 5"))


pb.print_h1("分析结果")

# 4.1 从本地文件嵌入图片 (你原有的方式)
pb.print_h2("cDNA饱和度曲线")
image_path = "/nas/projects/scrna/standard_analysis/c4/KSXY-TJQK-DO25112701-1/result/KSXY-TJQK-DO25112701-1_2025-12-04/sample1/03.analysis/cluster_annotation.png"
img = mpimg.imread(image_path)
fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.imshow(img)
ax1.axis("off")
pb.print_figure(fig1, caption="cDNA Saturation Plot")

pb.print_h2("模拟基因表达分布")
# 生成模拟数据
np.random.seed(42)
gene_names = [f"Gene_{i}" for i in range(1, 11)]
expression = np.random.lognormal(mean=3, sigma=1.0, size=10)
# 创建图表
fig2, ax2 = plt.subplots(figsize=(8, 5))
sns.barplot(x=gene_names, y=expression, ax=ax2, palette="viridis")
ax2.set_title("Top 10")
ax2.set_ylabel("Expression (FPKM)")
ax2.set_xlabel("Gene ID")
ax2.tick_params(axis="x", rotation=45)
plt.tight_layout()
# 核心函数：将matplotlib图形对象加入报告
pb.print_figure(fig2, caption="基因表达柱状图")

pb.print_h2("多图组合展示")
fig3, ((ax3_1, ax3_2), (ax3_3, ax3_4)) = plt.subplots(2, 2, figsize=(12, 10))
# 子图1: 散点图
ax3_1.scatter(np.random.rand(50), np.random.rand(50), c="blue", alpha=0.6)
ax3_1.set_title("")
# 子图2: 箱线图
ax3_2.boxplot([np.random.normal(0, 1, 100) for _ in range(3)])
ax3_2.set_title("")
# 子图3: 折线图
x = np.linspace(0, 10, 100)
ax3_3.plot(x, np.sin(x), "r-")
ax3_3.set_title("")
# 子图4: 直方图
ax3_4.hist(np.random.randn(1000), bins=30, alpha=0.7, color="green")
ax3_4.set_title("")
plt.tight_layout()
pb.print_figure(fig3, caption="复合图表示例")

# 新增：表格展示（使用翻页模式）
pb.print_h2("单细胞数据表格预览")
try:
    # 读取CSV文件
    table_path = "/nas/projects/scrna/standard_analysis/c4/KSXY-TJQK-DO25112701-1/result/KSXY-TJQK-DO25112701-1_2025-12-04/sample2/03.analysis/marker.csv"
    df = pd.read_csv(table_path)

    # 显示数据基本信息
    pb.print_h3("数据概览")
    pb.print(
        f"<div><strong>数据维度：</strong> {df.shape[0]} 行 × {df.shape[1]} 列</div>"
    )

    # 显示列名
    pb.print_h3("列名信息")
    columns_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px;'>"
    for col in df.columns:
        columns_html += f"<span style='background-color: #f0f0f0; padding: 5px 10px; border-radius: 4px;'>{col}</span>"
    columns_html += "</div>"
    pb.print(columns_html)

    # 显示完整数据表格（使用翻页模式）
    pb.print_h3("完整数据表格")
    pb.print_table(
        df,
        caption="单细胞数据完整表格",
        display_option="paging",
        paging_sizes=[10, 20, 50, "All"],
    )

    # 显示数据统计信息
    pb.print_h3("数值列统计信息")
    if df.select_dtypes(include=[np.number]).shape[1] > 0:
        pb.print_table(
            df.describe().round(2),
            caption="数值列统计信息",
            display_option="paging",
            paging_sizes=[5, 10, "All"],
        )
    else:
        pb.print_div("数据中没有数值列可供统计。")

except FileNotFoundError:
    pb.print_div(pb.bold("错误：") + "未找到指定的CSV文件，请检查文件路径。")
except pd.errors.EmptyDataError:
    pb.print_div(pb.bold("错误：") + "CSV文件为空。")
except Exception as e:
    pb.print_div(pb.bold("错误：") + f"读取CSV文件时发生错误：{str(e)}")

pb.print_h1("参考文献")
# 添加超链接
pb.print_div(
    "详细分析方法请参考: "
    + pb.link("DNBC4tools官方文档", "https://example.com/dnbc4tools")
)
pb.print_div("生信分析常见问题: " + pb.link("FAQ页面", "https://example.com/faq"))

# 添加一条水平分割线
pb.print_div('<hr style="height:2px;border-width:0;color:gray;background-color:gray">')
