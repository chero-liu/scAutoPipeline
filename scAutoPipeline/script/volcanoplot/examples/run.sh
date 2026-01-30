# Rscript ./volcanoplot/volcano.r \
#     -i volcanoplot/examples/group_BAV-vs-AV-all_diffexp_genes.xls \
#     -q 0.05 \
#     -f 1.5 \
#     -o volcanoplot/examples/out_up_down \
#     --symbol_topn 20

# Rscript ./volcanoplot/volcano.r \
#     -i /gpfs/oe-scrna/further_analysis/stRNA/10x/DZOE2023101583/DZOE2023101583-b1-panyunbao-h-cyffpe/result/report/DZOE2023101583_Report_2023_11_24/6.Diffexp/EBER_group_EBER_1-vs-EBER_0-all_diffexp_genes_anno.xls \
#     -q 0.05 \
#     -f 1.5 \
#     -o volcanoplot/examples/out_up_down \
#     --symbol_topn 20
    # --geneTextColors "#c8ff00,#008cff,#ff002b,#ffffff,#000000" \
Rscript ./volcano.r \
    -i examples/group_BAV-vs-AV-all_diffexp_genes.xls \
    -P BAV-vs-AV \
    --symbol_gene  examples/BAV-vs-AV_show.xls \
    -q 0.05 \
    -f 1.5 \
    -o examples/out_label
