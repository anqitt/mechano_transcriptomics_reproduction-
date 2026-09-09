#!/usr/bin/env Rscript

suppressPackageStartupMessages(library(mgcv))
suppressPackageStartupMessages(library(foreach))
suppressPackageStartupMessages(library(doParallel))
suppressPackageStartupMessages(library(iterators))

source("TensionMap/notebooks/helper_functions.R")

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 4) {
  stop("Usage: benchmark_figure5_gsem.R FILTERED_GEX_CSV TENSIONMAP_CSV FILTER_AUDIT_CSV OUTPUT_DIR")
}

gex_path <- args[[1]]
tensionmap_path <- args[[2]]
filter_audit_path <- args[[3]]
output_dir <- args[[4]]
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

rss_mb <- function() {
  # Process RSS inspection is blocked by this desktop sandbox; R heap usage is
  # recorded below instead.
  NA_real_
}

cat("Reading official processed matrices...\n")
load_start <- proc.time()[["elapsed"]]
tensionmap_res <- read.table(
  tensionmap_path, sep = ",", header = TRUE, row.names = 1,
  check.names = FALSE
)
gex_res <- read.table(
  gex_path, sep = ",", header = TRUE, row.names = 1,
  check.names = FALSE
)
load_seconds <- proc.time()[["elapsed"]] - load_start

# This line is copied from the official Figure 5 notebook.
tensionmap_res[["stresstensor_magnitude"]] <- tensionmap_res[["stresstensor_eigval1"]] + tensionmap_res[["stresstensor_eigval2"]]

expression_cells <- colnames(gex_res)
mechanics_cells <- rownames(tensionmap_res)
matched_cells <- intersect(expression_cells, mechanics_cells)
if (!identical(expression_cells, mechanics_cells)) {
  stop("Expression and mechanics cell identifiers are not in identical order")
}

expressed_genes <- rownames(gex_res)
filter_audit <- read.csv(filter_audit_path, stringsAsFactors = FALSE)
filtered_gene_count <- as.numeric(filter_audit$value[filter_audit$measure == "filtered_genes"])

data_audit <- data.frame(
  measure = c(
    "expression_cells", "mechanics_cells", "matched_cells",
    "expression_genes", "filtered_genes", "load_seconds"
  ),
  value = c(
    length(expression_cells), length(mechanics_cells), length(matched_cells),
    as.numeric(filter_audit$value[filter_audit$measure == "expression_genes"]),
    filtered_gene_count, load_seconds
  )
)
write.csv(data_audit, file.path(output_dir, "data_audit.csv"), row.names = FALSE)

one_gene <- expressed_genes[[1]]
one_metric <- "pressure"
one_start <- proc.time()[["elapsed"]]
one_res <- do_gsem_regression(
  one_gene, one_metric, tensionmap_res, gex_res,
  k_sp = 300, model_fx = TRUE, method = "REML"
)
one_seconds <- proc.time()[["elapsed"]] - one_start
one_mod <- one_res[[1]]
one_raw_gene <- as.numeric(gex_res[one_gene, mechanics_cells])
one_raw_mechanics <- log(tensionmap_res[[one_metric]])

summarize_vector <- function(name, values) {
  data.frame(
    variable = name, n = length(values), min = min(values),
    q1 = unname(quantile(values, 0.25)), median = median(values),
    mean = mean(values), q3 = unname(quantile(values, 0.75)),
    max = max(values), sd = sd(values)
  )
}

one_summary <- rbind(
  summarize_vector("raw_gene_expression", one_raw_gene),
  summarize_vector("raw_log_pressure", one_raw_mechanics),
  summarize_vector("residual_gene_expression", one_res[[3]]),
  summarize_vector("residual_log_pressure", one_res[[2]])
)
one_summary$gene <- one_gene
one_summary$cells <- length(mechanics_cells)
one_summary$beta <- unname(coef(one_mod)[[2]])
one_summary$stat <- summary(one_mod)$coefficients[2, 3]
one_summary$pval <- summary(one_mod)$coefficients[2, 4]
one_summary$runtime_seconds <- one_seconds
one_summary$success <- TRUE
write.csv(one_summary, file.path(output_dir, "one_gene_test.csv"), row.names = FALSE)

run_benchmark <- function(n_genes) {
  genes <- expressed_genes[seq_len(n_genes)]
  gc(reset = TRUE)
  rss_before <- rss_mb()
  started <- proc.time()[["elapsed"]]
  result <- tryCatch(
    parallel_gsem_regression(
      genes, tensionmap_res, gex_res,
      k_sp = 300, model_fx = TRUE, method = "REML", ncores = 2
    ),
    error = function(e) e
  )
  runtime <- proc.time()[["elapsed"]] - started
  rss_after <- rss_mb()
  gc_stats <- gc()

  if (inherits(result, "error")) {
    summary_row <- data.frame(
      genes = n_genes, successful = 0, failed = n_genes,
      runtime_seconds = runtime, seconds_per_gene = runtime / n_genes,
      projected_seconds_12704 = runtime / n_genes * 12704,
      master_rss_before_mb = rss_before, master_rss_after_mb = rss_after,
      r_heap_max_used_mb = max(gc_stats[, "max used"] * c(8, 56) / 1024^2),
      error = conditionMessage(result)
    )
    return(list(summary = summary_row, results = NULL))
  }

  result$padj <- p.adjust(result$pval, method = "BH")
  result$sign <- ifelse(result$beta > 0, "positive",
                        ifelse(result$beta < 0, "negative", "zero"))
  result$benchmark_genes <- n_genes
  successful_genes <- length(unique(result$gene[is.finite(result$beta) & is.finite(result$pval)]))
  summary_row <- data.frame(
    genes = n_genes, successful = successful_genes,
    failed = n_genes - successful_genes, runtime_seconds = runtime,
    seconds_per_gene = runtime / n_genes,
    projected_seconds_12704 = runtime / n_genes * 12704,
    master_rss_before_mb = rss_before, master_rss_after_mb = rss_after,
    r_heap_max_used_mb = max(gc_stats[, "max used"] * c(8, 56) / 1024^2),
    error = ""
  )
  list(summary = summary_row, results = result)
}

benchmark_summaries <- list()
for (n_genes in c(10, 50, 100)) {
  cat("Running deterministic benchmark:", n_genes, "genes with 2 workers\n")
  benchmark <- run_benchmark(n_genes)
  benchmark_summaries[[as.character(n_genes)]] <- benchmark$summary
  if (!is.null(benchmark$results)) {
    write.csv(
      benchmark$results,
      file.path(output_dir, paste0("gsem_results_", n_genes, "_genes.csv")),
      row.names = FALSE
    )
  }
  if (n_genes == 100 && benchmark$summary$failed == n_genes) break
}

benchmark_summary <- do.call(rbind, benchmark_summaries)
write.csv(benchmark_summary, file.path(output_dir, "benchmark_summary.csv"), row.names = FALSE)

session <- capture.output(sessionInfo())
writeLines(session, file.path(output_dir, "session_info.txt"))
cat("Benchmark complete.\n")
