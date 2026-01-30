library(ggplot2)
library(ggrepel)
library(dplyr)
library(optparse)

option_list <- list(
    make_option(c("--input", "-i"),
        type = "character",
        help = "The input differential gene table.e.g.*-vs-*all_diffexp_genes.xls"
    ),
    make_option(c("--foldchange", "-f"),
        type = "double", default = 2,
        help = "foldchange threshold."
    ),
    make_option(c("--symbol_fc", "-n"),
        type = "double", default = 2,
        help = "the foldchange threshold to display the gene symbol."
    ),
    make_option(c("--symbol_topn"),
        type = "integer", default = NULL,
        help = "the top n gene to display the gene symbol."
    ),
    make_option(c("--symbol_gene"),
        type = "character", default = NULL,
        help = "[OPTIONAL]the list of gene to display the gene symbol."
    ),
    make_option(c("--outdir", "-o"),
        type = "character", default = "./",
        help = "the output directory of Clustering results."
    ),
    make_option(c("--log2fc_col"),
        type = "character", default = "log2FoldChange",
        help = "Column name for log2 fold change values."
    ),
    make_option(c("--basemean_col"),
        type = "character", default = "baseMean",
        help = "Column name for base mean values."
    ),
    make_option(c("--foldchange_col"),
        type = "character", default = "FoldChange",
        help = "Column name for fold change values."
    ),
    make_option(c("--gene_col"),
        type = "character", default = "gene",
        help = "Column name for gene identifiers."
    )
)
opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)
if (is.null(opt$outdir)) {
    output_dir <- getwd()
} else {
    if (file.exists(opt$outdir)) {
        output_dir <- opt$outdir
    } else {
        output_dir <- opt$outdir
        dir.create(output_dir, recursive = T)
    }
}

DEG <- read.delim(opt$input, header = T, sep = "\t")
rownames(DEG) <- DEG[, 1]

## Rename columns to match expected names
# Store original column names for reference
log2fc_col <- opt$log2fc_col
basemean_col <- opt$basemean_col
foldchange_col <- opt$foldchange_col
gene_col <- opt$gene_col

# Create new columns with expected names
DEG$log2FoldChange <- DEG[[log2fc_col]]
DEG$baseMean <- DEG[[basemean_col]]
DEG$FoldChange <- DEG[[foldchange_col]]
DEG$gene <- DEG[[gene_col]]

## categorize and coloring
logFC_cutoff <- log(opt$foldchange, 2)
DEG$change <- as.factor(ifelse(abs(DEG$log2FoldChange) > logFC_cutoff,
    ifelse(DEG$log2FoldChange > logFC_cutoff, "Up", "Down"), "Normal"
))

## label
if (!is.null(opt$symbol_gene)) {
    symbol_genes <- read.table(opt$symbol_gene, header = T)
    DEG$label <- ""
    label <- DEG$gene[DEG$gene %in%
        as.character(symbol_genes$gene) & abs(DEG$log2FoldChange) > logFC_cutoff]
    DEG$label[DEG$gene %in%
        as.character(symbol_genes$gene) &
        abs(DEG$log2FoldChange) > logFC_cutoff] <- as.character(label)
} else if (!is.null(opt$symbol_topn)) {
    up <- filter(DEG, FoldChange > 1) %>%
        filter(log2FoldChange > logFC_cutoff) %>%
        arrange(desc(log2FoldChange)) %>%
        top_n(opt$symbol_topn, log2FoldChange)
    down <- filter(DEG, FoldChange < 1) %>%
        filter(log2FoldChange < -logFC_cutoff) %>%
        arrange(log2FoldChange) %>%
        top_n(-opt$symbol_topn, log2FoldChange)
    DEG$significant <- DEG$gene %in% c(as.character(up$gene), as.character(down$gene))
    DEG$label <- ""
    DEG[DEG$significant, "label"] <- as.character(DEG[DEG$significant, "gene"])
} else {
    DEG$significant <- (abs(DEG$log2FoldChange) > log(opt$symbol_fc, 2)) # 基因名展示阈值
    DEG$label <- ""
    DEG[DEG$significant, "label"] <- as.character(DEG[DEG$significant, "gene"])
}

## 极值处理
g <- ggplot(data = DEG, aes(x = DEG$baseMean, y = DEG$log2FoldChange, color = change)) +
    geom_point(size = 1.75) +
    theme_set(theme_set(theme_bw(base_size = 15))) +
    xlab(expression(paste("base Mean"))) +
    ylab(expression(paste(log[2], "Fold Change"))) +
      geom_text_repel( aes(label = label),
                       size = 3,
                       vjust=-0.5,
                       alpha=0.8) +
    scale_colour_manual(values = c("blue", "black", "red")) ## corresponding to the levels(res$change)
g <- g + geom_hline(yintercept = -log(opt$foldchange, 2), linetype = "dashed", color = "grey", size = 1) +
    geom_hline(yintercept = log(opt$foldchange, 2), linetype = "dashed", color = "grey", size = 1) +
    theme_bw() +
    theme(
        plot.title = element_text(hjust = 0.5),
        panel.grid = element_blank(),
        legend.title = element_blank()
    )
ggsave(file.path(output_dir, paste(strsplit(strsplit(opt$input, split = "/")[[1]][length(strsplit(opt$input, split = "/")[[1]])], split = "-all")[[1]][1], "-MA.pdf", sep = "")), height = 7, width = 7, plot = g,bg="white")
ggsave(file.path(output_dir, paste(strsplit(strsplit(opt$input, split = "/")[[1]][length(strsplit(opt$input, split = "/")[[1]])], split = "-all")[[1]][1], "-MA.png", sep = "")), height = 7, width = 7, plot = g, dpi = 1000,bg="white")
