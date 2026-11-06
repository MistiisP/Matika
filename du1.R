library(readxl)
library(moments)
.libPaths(Sys.getenv('R_LIBS_USER'))

# Načtení dat
df <- read_excel("FPS_data.xlsx")

karty <- c("Nvidia RTX 3070 Ti", "AMD Radeon RX 6800 XT")

# Funkce pro výpočet kompletní popisné statistiky dle R/VŠB standardů
spocitej_statistiky <- valik <- function(s) {
  n <- length(s)
  min_val <- min(s)
  q1 <- quantile(s, 0.25, type = 7)
  med <- median(s)
  mean_val <- mean(s)
  q3 <- quantile(s, 0.75, type = 7)
  max_val <- max(s)
  sd_val <- sd(s)
  skew_val <- skewness(s)
  kurt_val <- kurtosis(s) - 3 # Excess kurtosis (kolem 0)
  
  list(n = n, min = min_val, q1 = q1, med = med, mean = mean_val, 
       q3 = q3, max = max_val, sd = sd_val, skew = skew_val, kurt = kurt_val)
}

st_puvodni <- list()
st_ciste <- list()

cat("====================================================================\n")
cat(" TABULKA 1 & 2: SOUHRNNÉ STATISTIKY\n")
cat("====================================================================\n")

for (k in karty) {
  col_rel <- paste0(k, " average FPS release (FPS)")
  col_pat <- paste0(k, " average FPS patched (FPS)")
  
  s <- na.omit(df[[col_pat]] - df[[col_rel]])
  
  # Původní data
  st_puvodni[[k]] <- spocitej_statistiky(s)
  
  # Odstranění odlehlých pozorování metodou IQR (type = 7)
  q1 <- quantile(s, 0.25, type = 7)
  q3 <- quantile(s, 0.75, type = 7)
  iqr <- q3 - q1
  dolni_hradba <- q1 - 1.5 * iqr
  horni_hradba <- q3 + 1.5 * iqr
  
  s_ciste <- s[s >= dolni_hradba & s <= horni_hradba]
  odlehle <- s[s < dolni_hradba | s > horni_hradba]
  
  st_ciste[[k]] <- spocitej_statistiky(s_ciste)
  
  cat(sprintf("\n--- KARTA: %s ---\n", k))
  cat(sprintf("Odlehlé hodnoty (počet: %d): %s\n", length(odlehle), paste(round(odlehle, 2), collapse=", ")))
  cat(sprintf("[Tab. 1 - Původní] n=%d | min=%.2f | Q1=%.2f | med=%.2f | mean=%.2f | Q3=%.2f | max=%.2f | sd=%.2f | skew=%.2f | kurt=%.2f\n",
              st_puvodni[[k]]$n, st_puvodni[[k]]$min, st_puvodni[[k]]$q1, st_puvodni[[k]]$med, 
              st_puvodni[[k]]$mean, st_puvodni[[k]]$q3, st_puvodni[[k]]$max, st_puvodni[[k]]$sd, 
              st_puvodni[[k]]$skew, st_puvodni[[k]]$kurt))
  
  cat(sprintf("[Tab. 2 - Očištěná] n=%d | min=%.2f | Q1=%.2f | med=%.2f | mean=%.2f | Q3=%.2f | max=%.2f | sd=%.2f | skew=%.2f | kurt=%.2f\n",
              st_ciste[[k]]$n, st_ciste[[k]]$min, st_ciste[[k]]$q1, st_ciste[[k]]$med, 
              st_ciste[[k]]$mean, st_ciste[[k]]$q3, st_ciste[[k]]$max, st_ciste[[k]]$sd, 
              st_ciste[[k]]$skew, st_ciste[[k]]$kurt))
}

cat("\n====================================================================\n")
cat(" TEXTOVÉ ČÁSTI A INTERVALY SPOLEHLIVOSTI (Pravidlo 3σ / 95% či 99.7%)\n")
cat("====================================================================\n")

for (k in karty) {
  st <- st_ciste[[k]]
  m <- st$mean
  sd_v <- st$sd
  
  cat(sprintf("\n>>> Karta: %s <<<\n", k))
  cat(sprintf("  Průměr: %.2f (na 1 des.m: %.1f)\n", m, m))
  cat(sprintf("  Směr. odchylka: %.2f\n", sd_v))
  cat(sprintf("  Medián: %.2f\n", st$med))
  cat(sprintf("  IQR rozmezí (Q1 až Q3): %.2f až %.2f\n", st$q1, st$q3))
  
  # Pravidlo 3 sigma (pro normální rozdělení)
  cat(sprintf("  Pravidlo 3σ (m ± 3*sd): od %.2f do %.2f\n", m - 3*sd_v, m + 3*sd_v))
  # Pravidlo 2 sigma (m ± 2*sd pro přibližně 95 %)
  cat(sprintf("  Pravidlo 2σ (m ± 2*sd): od %.2f do %.2f\n", m - 2*sd_v, m + 2*sd_v))
}