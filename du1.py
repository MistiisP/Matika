import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import math

soubor = "FPS_data.xlsx"
df = pd.read_excel(soubor)

karty = ["Nvidia RTX 3070 Ti", "AMD Radeon RX 6800 XT"]
data_puvodni = {}
data_ciste = {}
odlehle_info = {}

for k in karty:
    col_release = f"{k} average FPS release (FPS)"
    col_patched = f"{k} average FPS patched (FPS)"
    
    # Výpočet nárůstu FPS: patched - release
    s = (df[col_patched] - df[col_release]).dropna()
    data_puvodni[k] = s
    
    # Výpočet kvartilů (R default type=7 odpovídá method='linear')
    q1 = np.percentile(s, 25, method='linear')
    q3 = np.percentile(s, 75, method='linear')
    iqr = q3 - q1
    dolni_hradba = q1 - 1.5 * iqr
    horni_hradba = q3 + 1.5 * iqr
    
    ciste = s[(s >= dolni_hradba) & (s <= horni_hradba)]
    odlehle = s[(s < dolni_hradba) | (s > horni_hradba)]
    
    data_ciste[k] = ciste
    odlehle_info[k] = (dolni_hradba, horni_hradba, odlehle.values)

def spocitej_radek(s):
    n = len(s)
    minimum = np.min(s)
    q1 = np.percentile(s, 25, method='linear')
    median = np.percentile(s, 50, method='linear')
    prumer = np.mean(s)
    q3 = np.percentile(s, 75, method='linear')
    maximum = np.max(s)
    std = np.std(s, ddof=1)
    
    # V Rku: moments::skewness a moments::kurtosis - 3 odpovídá bias=True
    # V Rku: e1071::skewness(type=2) odpovídá bias=False
    sik_moments = stats.skew(s, bias=True)
    sik_e1071 = stats.skew(s, bias=False)
    spic_moments = stats.kurtosis(s, bias=True)   # excess kurtosis (kolem 0)
    spic_e1071 = stats.kurtosis(s, bias=False)    # excess kurtosis (kolem 0)
    
    return {
        'n': n, 'min': minimum, 'q1': q1, 'med': median, 'mean': prumer,
        'q3': q3, 'max': maximum, 'std': std,
        'sik_m': sik_moments, 'sik_e': sik_e1071,
        'spic_m': spic_moments, 'spic_e': spic_e1071
    }

st_puv = {k: spocitej_radek(data_puvodni[k]) for k in karty}
st_cis = {k: spocitej_radek(data_ciste[k]) for k in karty}

def vypis_tabulku(st, nazev, offset=0):
    k1, k2 = karty[0], karty[1]
    print(f"\n{'='*75}\n{nazev}\n{'='*75}")
    print(f"{'Ukazatel':<22} | {k1:<24} | {k2:<24}")
    print("-" * 75)
    radky = [
        ("rozsah souboru", f"{st[k1]['n']} (Odp.{1+offset})", f"{st[k2]['n']} (Odp.{2+offset})"),
        ("minimum", f"{st[k1]['min']:.2f} (nebo {st[k1]['min']:.1f})", f"{st[k2]['min']:.2f} (nebo {st[k2]['min']:.1f})"),
        ("dolní kvartil", f"{st[k1]['q1']:.2f} (nebo {st[k1]['q1']:.1f})", f"{st[k2]['q1']:.2f} (nebo {st[k2]['q1']:.1f})"),
        ("medián", f"{st[k1]['med']:.2f} (nebo {st[k1]['med']:.1f})", f"{st[k2]['med']:.2f} (nebo {st[k2]['med']:.1f})"),
        ("průměr", f"{st[k1]['mean']:.2f} (nebo {st[k1]['mean']:.1f})", f"{st[k2]['mean']:.2f} (nebo {st[k2]['mean']:.1f})"),
        ("horní kvartil", f"{st[k1]['q3']:.2f} (nebo {st[k1]['q3']:.1f})", f"{st[k2]['q3']:.2f} (nebo {st[k2]['q3']:.1f})"),
        ("maximum", f"{st[k1]['max']:.2f} (nebo {st[k1]['max']:.1f})", f"{st[k2]['max']:.2f} (nebo {st[k2]['max']:.1f})"),
        ("směrod. odchylka", f"{st[k1]['std']:.2f} (nebo {st[k1]['std']:.3f})", f"{st[k2]['std']:.2f} (nebo {st[k2]['std']:.3f})"),
        ("šikmost (e1071/mom)", f"{st[k1]['sik_e']:.2f} / {st[k1]['sik_m']:.2f}", f"{st[k2]['sik_e']:.2f} / {st[k2]['sik_m']:.2f}"),
        ("špičatost (kolem 0)", f"{st[k1]['spic_e']:.2f} / {st[k1]['spic_m']:.2f}", f"{st[k2]['spic_e']:.2f} / {st[k2]['spic_m']:.2f}"),
    ]
    for r in radky:
        print(f"{r[0]:<22} | {r[1]:<24} | {r[2]:<24}")

vypis_tabulku(st_puv, "TAB. 1: PŮVODNÍ DATA (Odpovědi 1 až 20)", offset=0)

print("\n--- ODLEHLÁ POZOROVÁNÍ (pro Odpověď 42) ---")
for k in karty:
    dh, hh, odl = odlehle_info[k]
    print(f"{k}: Dolní hradba = {dh:.2f}, Horní hradba = {hh:.2f} | Počet odlehlých = {len(odl)} -> hodnoty: {odl}")

vypis_tabulku(st_cis, "TAB. 2: PO ODSTRANĚNÍ ODLEHLÝCH POZOROVÁNÍ (Odpovědi 21 až 40)", offset=20)

print(f"\n{'='*75}\nTEXTOVÁ ČÁST PRO NVIDIA RTX 3070 (Odpovědi 41 až 50)\n{'='*75}")
s3070 = st_cis[karty[0]]
print(f"Odpověď 41 (původní rozsah n) : {st_puv[karty[0]]['n']}")
print(f"Odpověď 42 (odlehlé hodnoty)  : Počet odlehlých je {len(odlehle_info[karty[0]][2])} (hodnoty: {odlehle_info[karty[0]][2]})")
print(f"Odpověď 43 (nový rozsah n)    : {s3070['n']}")
print(f"Odpověď 44 až 45 (min až max) : {s3070['min']:.2f} až {s3070['max']:.2f} (na 1 des. místo: {s3070['min']:.1f} až {s3070['max']:.1f})")
print(f"Odpověď 46 (průměr)           : {s3070['mean']:.2f} (na 1 des. místo: {s3070['mean']:.1f})")
print(f"Odpověď 47 (směr. odchylka)   : {s3070['std']:.2f} (na 1 des. místo: {s3070['std']:.1f})")
print(f"Odpověď 48 (medián - polovina): {s3070['med']:.2f} (na 1 des. místo: {s3070['med']:.1f})")
print(f"Odpověď 49 až 50 (Q1 až Q3)   : {s3070['q1']:.2f} až {s3070['q3']:.2f} (na 1 des. místo: {s3070['q1']:.1f} až {s3070['q3']:.1f})")

print(f"\n{'='*75}\nOVĚŘENÍ NORMALITY A PRAVIDLO 2/3 SIGMA (Odpovědi 51 až 68)\n{'='*75}")
for idx, k in enumerate(karty):
    st_k = st_cis[k]
    m, sd = st_k['mean'], st_k['std']
    _, p_val = stats.shapiro(data_ciste[k])
    je_norm = ( -2 < st_k['sik_e'] < 2 ) and ( -2 < st_k['spic_e'] < 2 ) and (p_val > 0.05)
    
    start_odp = 51 if idx == 0 else 60
    print(f"\n>>> {k} (Odpovědi {start_odp} až {start_odp+8}) <<<")
    print(f"  Šikmost = {st_k['sik_e']:.2f}, Špičatost = {st_k['spic_e']:.2f}, Shapiro p-hodnota = {p_val:.4f}")
    print(f"  Verdikt normality: {'LZE předpokládat normální rozdělení (odpovídá / leží / leží / leží / lze)' if je_norm else 'NELZE předpokládat normální rozdělení'}")
    print(f"  Pravidlo 1 sigma (68 % hodnot): ({m - 1*sd:.2f} ; {m + 1*sd:.2f}) | na 1 des.m.: ({m - 1*sd:.1f} ; {m + 1*sd:.1f})")
    print(f"  Pravidlo 2 sigma (95 % hodnot): ({m - 2*sd:.2f} ; {m + 2*sd:.2f}) | na 1 des.m.: ({m - 2*sd:.1f} ; {m + 2*sd:.1f})")
    print(f"  Pravidlo 3 sigma (99,7% hodnot): ({m - 3*sd:.2f} ; {m + 3*sd:.2f}) | na 1 des.m.: ({m - 3*sd:.1f} ; {m + 3*sd:.1f})")
