# =============================================================================
# 09_medium_constants.R  -  Medium-dependent cell size / carbon / inoculum
# =============================================================================
# STANDALONE add-on. Changes NOTHING in the existing pipeline. It reads the
# finished derived table (whose r and K are immune to these conversions),
# applies a GROWTH-MEDIUM-dependent set of constants
#   - cell carbon per cell   (fg C)          -> growth_fgC_h, CUE
#   - inoculum N0            (cells / L)      -> per-cell respiration = K / N0
#   - cell volume           (um^3, reference)
# then re-derives every N0- and carbon-dependent column and re-plots. Growth
# rate (h^-1 = r*60), K, and every thermal SHAPE are unchanged; only absolute
# per-cell / carbon LEVELS and CUE move.
#
# WHY per-medium (not per-temperature): the cell VOLUME is set per medium from
# Volkmer & Heinemann 2011 (nutrient modulation of size at fixed T), and carbon
# follows from a fixed direct-measurement carbon DENSITY (fg C um^-3, see below).
# Nutrient modulation changes cell size at fixed T; temperature-modulated growth
# does NOT shrink cells the same way (E. coli size ~invariant 15-30 C), so one
# set of constants per medium is applied uniformly across the temperature range.
#
# Constants below are literature-derived from the measured 37 C growth rates.
# EDIT THEM HERE if you refine the values.
#
# Outputs (all NEW, nothing overwritten): figures/medium_constants/
#   derived_medium_constants.csv   + candle figures + stacked grids
#
# Run:  source("scripts/09_medium_constants.R")   (run 06 first)
# =============================================================================

.this_dir <- if (
  requireNamespace("rstudioapi", quietly = TRUE) &&
  rstudioapi::isAvailable() &&
  nzchar(rstudioapi::getActiveDocumentContext()$path)
) {
  dirname(rstudioapi::getActiveDocumentContext()$path)
} else {
  tryCatch(dirname(sys.frame(1)$ofile), error = function(e) getwd())
}
source(file.path(.this_dir, "config.R"))

suppressPackageStartupMessages({
  library(dplyr); library(readr); library(tibble); library(tidyr)
  library(ggplot2); library(rlang)
})

# ===== Per-medium constants (keyed by otu_name in the derived table) ==========
# cell_carbon_fg : DIRECT-MEASUREMENT route -> carbon = CARBON_DENSITY x volume.
#   Carbon per unit CELL VOLUME is far more conserved across growth conditions
#   than carbon per cell, so we fix the density and let the medium-specific
#   volume set the per-cell carbon. CARBON_DENSITY_FG_PER_UM3 = 180 fg C um^-3
#   is the mid-range of direct measurements of actively growing E. coli:
#     - Fagerbakke, Heldal & Norland 1996 (Aquat Microb Ecol 10:15): X-ray
#       microanalysis of single cells, ~0.2 pg C um^-3 wet volume (growth phase).
#     - Loferer-Krossbacher, Klima & Psenner 1998 (AEM 64:688): TEM densitometry,
#       ~435 fg dry mass um^-3 x 0.47 C ~= 200 fg C um^-3.
#     - Neidhardt/Ingraham, Physiology of the Bacterial Cell: ~1 um^3 cell,
#       ~280 fg dry, ~50% C -> ~140 fg C um^-3.
#   Carbon fraction of dry weight (47%) is Folsom & Carlson 2015 (Microbiology
#   161:1659), measured on the exact strain MG1655. This REPLACES the earlier
#   Bremer & Dennis growth-law dry-mass route (which extrapolated past its
#   fast-growth calibration ceiling for LB/R2A); the density route rests on
#   direct elemental/mass measurements instead.
# N_inoc         : computed uniformly from cell volume by the SAME OD rule for
#                  every medium (see OD_* constants below) - not hand-typed.
# cell_volume    : Volkmer & Heinemann 2011 volume(mu) per medium. This is the
#                  single per-medium INPUT; carbon and N_inoc both derive from it
#                  by fixed formulas, so all media follow identical processing.
CARBON_DENSITY_FG_PER_UM3 <- 180   # direct-measurement mid-range (see refs above)

# Uniform OD -> inoculum-cell-density rule (Volkmer & Heinemann 2011 OD invariant
# = 3.6 uL packed cell volume per mL at OD600 = 1; inoculum OD600 = 0.0005):
#   N_inoc [cells/L] = 3.6 * 0.0005 * 1e9 (uL->um^3) * 1e3 (mL->L) / V
#                    = 1.8e9 / V
OD_CELLVOL_UL_PER_ML_AT_OD1 <- 3.6
OD_INOC                     <- 0.0005

MEDIUM_CONSTANTS <- tibble::tribble(
  ~otu_name,     ~cell_volume_um3, ~is_real,
  "Ecoli_R2A",   3.8,              TRUE,
  "Ecoli_LB",    4.4,              TRUE,
  "Ecoli_M9",    2.2,              TRUE,
  "M9",          2.2,              FALSE   # M9 blank/control
) %>%
  dplyr::mutate(
    cell_carbon_fg = CARBON_DENSITY_FG_PER_UM3 * cell_volume_um3,
    N_inoc         = OD_CELLVOL_UL_PER_ML_AT_OD1 * OD_INOC * 1e9 * 1e3 / cell_volume_um3
  ) %>%
  dplyr::relocate(cell_carbon_fg, N_inoc, .after = otu_name)

# ===== Load + guard ==========================================================
if (!file.exists(derived_csv)) stop("Run 06 first: derived table not found\n  ", derived_csv)
if (isTRUE(N0_BACKPROJECT))
  stop("09_medium_constants.R assumes N0_BACKPROJECT <- FALSE (N0 = N_inoc). Current config has TRUE.")

d <- readr::read_csv(derived_csv, show_col_types = FALSE) %>%
  dplyr::mutate(OTU = as.integer(OTU), T = as.numeric(T))

present <- intersect(unique(d$otu_name), MEDIUM_CONSTANTS$otu_name)
message("09: media in derived table: ", paste(unique(d$otu_name), collapse = ", "))
message("09: constants applied to:   ", paste(present, collapse = ", "))

# ===== Re-derive with medium constants (N0_BACKPROJECT = FALSE) ================
mc <- MEDIUM_CONSTANTS %>%
  dplyr::select(otu_name, cc_new = cell_carbon_fg, ninoc_new = N_inoc, vol_new = cell_volume_um3)

d2 <- d %>%
  dplyr::left_join(mc, by = "otu_name") %>%
  dplyr::mutate(
    cc    = dplyr::coalesce(cc_new,    cell_carbon_fg),
    ninoc = dplyr::coalesce(ninoc_new, N_inoculation_cells_per_L),
    vol   = dplyr::coalesce(vol_new,   cell_volume_um3),
    N_inoculation_cells_per_L        = ninoc,
    delta_Ninoc_to_N0_min            = 0,
    N0_cells_per_L                   = ninoc,
    cell_carbon_fg                   = cc,
    cell_volume_um3                  = vol,
    C_tot_O2_mg_per_L                = (K/r)*(exp(r*T_end_min) - 1),
    biomass_integral_cells_min_per_L = ninoc*(exp(r*T_end_min) - 1)/r,
    R_O2_mg_cell_min                 = K / ninoc,
    growth_fgC_h                     = r * cc * MIN_TO_H,
    respiration_fgC_h                = R_O2_mg_cell_min * MG_TO_FG * O2_TO_C_MASS *
                                       RESPIRATORY_QUOTIENT * MIN_TO_H,
    growth_C_per_C_h                 = growth_fgC_h / cc,
    respiration_C_per_C_h            = respiration_fgC_h / cc,
    CUE                              = growth_fgC_h / (growth_fgC_h + respiration_fgC_h),
    resp_over_growth                 = respiration_fgC_h / growth_fgC_h,
    growth_rate_h                    = r * 60
  ) %>%
  dplyr::select(-cc_new, -ninoc_new, -vol_new, -cc, -ninoc, -vol)

# ===== Output folder (NEW, under figures/) ====================================
out_dir <- file.path(figures_dir, "medium_constants")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
readr::write_csv(d2, file.path(out_dir, "derived_medium_constants.csv"))
readr::write_csv(MEDIUM_CONSTANTS, file.path(out_dir, "medium_constants_used.csv"))

# ===== Plot data: real media, plot-point exclusions applied ===================
plot_d <- d2 %>% dplyr::filter(otu_name %in% (MEDIUM_CONSTANTS %>% filter(is_real) %>% pull(otu_name)))
if (exists("PLOT_EXCLUDE_POINTS") && nrow(PLOT_EXCLUDE_POINTS) > 0) {
  .ex <- PLOT_EXCLUDE_POINTS %>% dplyr::mutate(T = as.numeric(T), OTU = as.integer(OTU),
                                               Replicate = toupper(as.character(Replicate)))
  plot_d <- dplyr::anti_join(plot_d, .ex, by = c("T","OTU","Replicate"))
}

med_of <- function(x) x   # otu_name is already the label
otu_colour_scale <- ggplot2::scale_colour_brewer(palette = "Dark2", name = "Medium")

mean_sd <- function(x){ m<-mean(x,na.rm=TRUE); s<-stats::sd(x,na.rm=TRUE); if(!is.finite(s)) s<-0
  data.frame(y=m, ymin=m-s, ymax=m+s) }
candles <- function() list(
  ggplot2::geom_point(size=1.6, alpha=0.35, position=ggplot2::position_jitter(width=0.5, height=0)),
  ggplot2::stat_summary(fun.data=mean_sd, geom="errorbar", width=1.6, linewidth=0.8),
  ggplot2::stat_summary(fun=mean, geom="point", size=2.8, shape=18))

save_fig <- function(p, name, w=7.5, h=4.8){
  ggplot2::ggsave(file.path(out_dir, name), p, width=w, height=h, dpi=300)
  message("  saved ", name)
}

METRICS <- list(
  list(col="growth_rate_h",   ylab=expression("Growth rate (h"^{-1}*")"),                 title="Growth rate"),
  list(col="R_O2_mg_cell_min",ylab=expression("Per-cell respiration (mg O"[2]*" cell"^{-1}*" min"^{-1}*")"), title="Per-cell respiration"),
  list(col="CUE",             ylab="CUE",                                                  title="Carbon-use efficiency"),
  list(col="growth_fgC_h",    ylab=expression("Growth (fg C h"^{-1}*")"),                  title="Growth (carbon units)")
)

message("\n09: drawing medium-constant figures -> ", out_dir)
for (m in METRICS) {
  cd <- plot_d %>% dplyr::filter(is.finite(.data[[m$col]]))
  p <- ggplot2::ggplot(cd, ggplot2::aes(T, .data[[m$col]], colour = otu_name)) +
    candles() + otu_colour_scale +
    ggplot2::facet_wrap(~ otu_name, scales = "free_y") +
    ggplot2::labs(title=paste0(m$title, " (medium-dependent constants)"),
                  subtitle="cell carbon + inoculum N0 set per medium from growth law; mean ± SD",
                  x="Temperature (°C)", y=m$ylab) +
    ggplot2::theme_classic(12) + ggplot2::theme(legend.position="none")
  save_fig(p, sprintf("mc_%s.png", m$col))
}

# ===== Stacked grid: growth (top) / per-cell respiration (bottom) / CUE =======
build_grid <- function(specs, file, title, rowh=3.0){
  parts <- lapply(specs, function(s) plot_d %>%
    dplyr::filter(is.finite(.data[[s$col]])) %>%
    dplyr::transmute(T, otu_name, value=.data[[s$col]], panel=s$row_lab))
  g <- dplyr::bind_rows(parts) %>% dplyr::mutate(panel=factor(panel, levels=vapply(specs,function(s)s$row_lab,"")))
  p <- ggplot2::ggplot(g, ggplot2::aes(T, value, colour=otu_name)) +
    candles() + otu_colour_scale +
    ggplot2::facet_grid(panel ~ otu_name, scales="free_y", switch="y",
                        labeller=ggplot2::labeller(panel=ggplot2::label_wrap_gen(26))) +
    ggplot2::labs(title=title, subtitle="medium-dependent constants; mean ± SD; shared temperature axis",
                  x="Temperature (°C)", y=NULL) +
    ggplot2::theme_classic(12) +
    ggplot2::theme(strip.placement="outside", strip.background=ggplot2::element_rect(fill="grey95",colour=NA),
                   legend.position="none", panel.spacing.y=ggplot2::unit(1.6,"lines"),
                   panel.spacing.x=ggplot2::unit(1.0,"lines"))
  n_med <- dplyr::n_distinct(g$otu_name)
  save_fig(p, file, w=2.5+3.0*n_med, h=1.4+(rowh+0.4)*length(specs))
}
build_grid(list(list(col="growth_rate_h",    row_lab="Growth rate (h⁻¹)"),
                list(col="R_O2_mg_cell_min", row_lab="Per-cell respiration (mg O₂ cell⁻¹ min⁻¹)")),
           "grid_growth_vs_percell_respiration.png",
           "Growth vs per-cell respiration (medium-dependent constants)")
build_grid(list(list(col="growth_rate_h",    row_lab="Growth rate (h⁻¹)"),
                list(col="R_O2_mg_cell_min", row_lab="Per-cell respiration (mg O₂ cell⁻¹ min⁻¹)"),
                list(col="CUE",              row_lab="Carbon-use efficiency (CUE)")),
           "grid_growth_percell_CUE.png",
           "Growth, per-cell respiration and CUE (medium-dependent constants)")

message("\nDone: 09_medium_constants.R  ->  ", out_dir)
