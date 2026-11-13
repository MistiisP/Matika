"""DÚ 2: testy významnosti nárůstů FPS po odstranění odlehlých hodnot.

Nárůst FPS je definován jako patched - release. Odlehlé hodnoty jsou
odstraněny samostatně pro každou z obou porovnávaných karet pomocí
Tukeyho vnitřních hradeb (1,5 IQR).
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ALPHA = 0.05
DATA_FILE = Path(__file__).with_name("FPS_data.xlsx")


def fps_increase(data: pd.DataFrame, card: str) -> pd.Series:
    """Return cleaned FPS increases for one card."""
    release = data[f"{card} average FPS release (FPS)"]
    patched = data[f"{card} average FPS patched (FPS)"]
    increase = (patched - release).dropna()
    q1, q3 = increase.quantile([0.25, 0.75])
    iqr = q3 - q1
    return increase[(increase >= q1 - 1.5 * iqr) & (increase <= q3 + 1.5 * iqr)]


def one_sample_results(sample: pd.Series) -> dict[str, float]:
    """Calculate a two-sided 95% CI and a right-sided t-test against zero."""
    test = stats.ttest_1samp(sample, 0, alternative="greater")
    df = len(sample) - 1
    standard_error = sample.std(ddof=1) / np.sqrt(len(sample))
    lower = sample.mean() - stats.t.ppf(1 - ALPHA, df) * standard_error
    two_sided = stats.t.interval(1 - ALPHA, df, loc=sample.mean(), scale=standard_error)
    return {
        "mean": sample.mean(),
        "median": sample.median(),
        "skew": stats.skew(sample, bias=False),
        "shapiro_p": stats.shapiro(sample).pvalue,
        "p_value": test.pvalue,
        "ci_lower": two_sided[0],
        "ci_upper": two_sided[1],
        "one_sided_lower": lower,
    }


def main() -> None:
    data = pd.read_excel(DATA_FILE)
    nvidia = fps_increase(data, "Nvidia RTX 3070 Ti")
    amd = fps_increase(data, "AMD Radeon RX 6800 XT")
    nvidia_result = one_sample_results(nvidia)
    amd_result = one_sample_results(amd)

    min_shapiro = min(nvidia_result["shapiro_p"], amd_result["shapiro_p"])
    print("DATA PO ODSTRANĚNÍ ODLEHLÝCH POZOROVÁNÍ")
    print(f"Nvidia RTX 3070: n={len(nvidia)}, průměr={nvidia_result['mean']:.6f}, "
          f"medián={nvidia_result['median']:.6f}")
    print(f"AMD Radeon RX 6800: n={len(amd)}, průměr={amd_result['mean']:.6f}, "
          f"medián={amd_result['median']:.6f}")
    print(f"Shapiro-Wilk p-hodnoty: Nvidia={nvidia_result['shapiro_p']:.6f}, "
          f"AMD={amd_result['shapiro_p']:.6f}; minimum={min_shapiro:.6f}")
    print(f"Šikmost: Nvidia={nvidia_result['skew']:.6f}, AMD={amd_result['skew']:.6f}")

    print("\nJEDNOVÝBĚROVÉ TESTY H0: μ = 0 proti H1: μ > 0")
    for name, result in (("Nvidia RTX 3070", nvidia_result),
                         ("AMD Radeon RX 6800", amd_result)):
        print(
            f"{name}: 95% CI=({result['ci_lower']:.6f}; "
            f"{result['ci_upper']:.6f}) FPS, "
            f"p={result['p_value']:.6g}, "
            f"jednostranná dolní mez={result['one_sided_lower']:.6f}"
        )

    # Klasický oboustranný F-test je použit jako kontrola shody rozptylů.
    f_stat = amd.var(ddof=1) / nvidia.var(ddof=1)
    f_df1, f_df2 = len(amd) - 1, len(nvidia) - 1
    f_cdf = stats.f.cdf(f_stat, f_df1, f_df2)
    f_p = 2 * min(f_cdf, 1 - f_cdf)
    comparison = stats.ttest_ind(amd, nvidia, equal_var=True, alternative="greater")
    df = len(nvidia) + len(amd) - 2
    pooled_variance = (
        (len(nvidia) - 1) * nvidia.var(ddof=1)
        + (len(amd) - 1) * amd.var(ddof=1)
    ) / df
    difference = amd.mean() - nvidia.mean()
    standard_error = np.sqrt(pooled_variance * (1 / len(nvidia) + 1 / len(amd)))
    lower_bound = difference - stats.t.ppf(1 - ALPHA, df) * standard_error
    print("\nPOROVNÁNÍ AMD - NVIDIA")
    print(f"F-test shody rozptylů: F={f_stat:.6f}, "
          f"df=({f_df1}, {f_df2}), p={f_p:.6f}")
    print(f"AMD - Nvidia: rozdíl průměrů={difference:.6f} FPS, "
          f"rozdíl mediánů={amd.median() - nvidia.median():.6f} FPS")
    print(f"95% pravostranný interval pro μ_A - μ_N: "
          f"({lower_bound:.6f}; ∞) FPS")
    print(f"Poolovaný dvouvýběrový t-test: t={comparison.statistic:.6f}, "
          f"df={df}, p={comparison.pvalue:.6g}")


if __name__ == "__main__":
    main()