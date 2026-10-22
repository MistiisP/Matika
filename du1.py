import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# =====================================================================
# 1. NAČTENÍ A PŘÍPRAVA DAT
# =====================================================================
soubor = "FPS_data.xlsx"
df = pd.read_excel(soubor)

# Přesné názvy karet podle zadání
karty = ["Nvidia RTX 3070 Ti", "AMD Radeon RX 6800 XT"]
data_puvodni = {}
data_ciste = {}
odlehle_info = {}

for k in karty:
    # Názvy sloupců přesně tak, jak je vypsal tvůj Excel
    col_release = f"{k} average FPS release (FPS)"
    col_patched = f"{k} average FPS patched (FPS)"
    
    # Výpočet nárůstu FPS: patched - release a odstranění prázdných řádků
    s = (df[col_patched] - df[col_release]).dropna()
    data_puvodni[k] = s
    
    # Výpočet vnitřních hradeb pro odlehlá pozorování (1.5 * IQR)
    q1 = np.percentile(s, 25)
    q3 = np.percentile(s, 75)
    iqr = q3 - q1
    dolni_hradba = q1 - 1.5 * iqr
    horni_hradba = q3 + 1.5 * iqr
    
    # Odstranění odlehlých pozorování
    ciste = s[(s >= dolni_hradba) & (s <= horni_hradba)]
    odlehle = s[(s < dolni_hradba) | (s > horni_hradba)]
    
    data_ciste[k] = ciste
    odlehle_info[k] = (dolni_hradba, horni_hradba, odlehle.values)

# =====================================================================
# 2. VÝPIS VÝSLEDKŮ PRO LMS TEST (DO TERMINÁLU)
# =====================================================================
def vypis_statistiky(data_dict, nadpis):
    print(f"\n{'='*70}\n{nadpis}\n{'='*70}")
    for k, s in data_dict.items():
        n = len(s)
        prumer = np.mean(s)
        std = np.std(s, ddof=1)
        var = np.var(s, ddof=1)
        q25, median, q75 = np.percentile(s, [25, 50, 75])
        iqr = q75 - q25
        sikmost = stats.skew(s, bias=False)
        spicatost = stats.kurtosis(s, bias=False)
        shapiro_stat, shapiro_p = stats.shapiro(s)
        
        ci_low, ci_high = stats.t.interval(0.95, df=n-1, loc=prumer, scale=stats.sem(s))
        
        print(f"\n>>> KARTA: {k} <<<")
        print(f"  Rozsah výběru (n)           = {n}")
        print(f"  Průměr                      = {prumer:.4f}  (zaokr. na 2 m.: {prumer:.2f} | na 1 m.: {prumer:.1f})")
        print(f"  Směrodatná odchylka (s)     = {std:.4f}  (zaokr. na 2 m.: {std:.2f})")
        print(f"  Rozptyl (s^2)               = {var:.4f}")
        print(f"  Minimum                     = {np.min(s):.4f}")
        print(f"  Dolní kvartil (Q1 / 25%)    = {q25:.4f}")
        print(f"  Medián (Q2 / 50%)           = {median:.4f}  (zaokr. na 2 m.: {median:.2f} | na 1 m.: {median:.1f})")
        print(f"  Horní kvartil (Q3 / 75%)    = {q75:.4f}")
        print(f"  Maximum                     = {np.max(s):.4f}")
        print(f"  Mezikvartilové rozp. (IQR)  = {iqr:.4f}")
        print(f"  Šikmost (skewness)          = {sikmost:.4f}")
        print(f"  Špičatost (kurtosis,okolí 0)= {spicatost:.4f} (pokud chtějí okolí 3: {spicatost+3:.4f})")
        print(f"  Shapiro-Wilk p-hodnota      = {shapiro_p:.4f} ({'Normální (p > 0.05)' if shapiro_p > 0.05 else 'NENÍ normální (p < 0.05)'})")
        print(f"  95% IS pro průměr           = ({ci_low:.2f} ; {ci_high:.2f})")

vypis_statistiky(data_puvodni, "1. STATISTIKY PRO PŮVODNÍ DATA (PŘED ODSTRANĚNÍM ODLEHLÝCH)")

print("\n--- KONTROLA ODLEHLÝCH POZOROVÁNÍ (1.5 * IQR) ---")
for k in karty:
    dh, hh, odl = odlehle_info[k]
    print(f"{k}: Dolní hradba = {dh:.2f}, Horní hradba = {hh:.2f} | Počet odlehlých: {len(odl)} -> hodnoty: {odl}")

vypis_statistiky(data_ciste, "2. STATISTIKY PO ODSTRANĚNÍ ODLEHLÝCH POZOROVÁNÍ")

# =====================================================================
# 3. TVORBA GRAFŮ A ULOŽENÍ DO PDF PŘÍLOHY
# =====================================================================
fig = plt.figure(figsize=(12, 14))
fig.suptitle("Obr. 1: Analýza nárůstu výkonnostního skóre (FPS) ve hře Cyberpunk 2077\npo aplikaci patche 1.5 pro grafické karty RTX 3070 Ti a RX 6800 XT", 
             fontsize=13, fontweight='bold', y=0.98)

ax1 = plt.subplot(3, 2, 1)
bp1 = ax1.boxplot([data_puvodni[k] for k in karty], label=karty, patch_artist=True, widths=0.5)
for patch, color in zip(bp1['boxes'], ['#a6cee3', '#b2df8a']):
    patch.set_facecolor(color)
ax1.set_title("a) Krabicový graf (původní data)", fontweight='bold')
ax1.set_ylabel("Nárůst výkonu (FPS)")
ax1.grid(axis='y', linestyle='--', alpha=0.6)

ax2 = plt.subplot(3, 2, 2)
bp2 = ax2.boxplot([data_ciste[k] for k in karty], label=karty, patch_artist=True, widths=0.5)
for patch, color in zip(bp2['boxes'], ['#a6cee3', '#b2df8a']):
    patch.set_facecolor(color)
ax2.set_title("b) Krabicový graf (po odstranění odlehlých pozorování)", fontweight='bold')
ax2.set_ylabel("Nárůst výkonu (FPS)")
ax2.grid(axis='y', linestyle='--', alpha=0.6)

spolecne_min = min( data_ciste[karty[0]].min(), data_ciste[karty[1]].min() )
spolecne_max = max( data_ciste[karty[0]].max(), data_ciste[karty[1]].max() )
bins = np.linspace(spolecne_min, spolecne_max, 12)

barvy = ['#1f78b4', '#33a02c']
for i, k in enumerate(karty):
    ax_hist = plt.subplot(3, 2, 3 + i)
    ax_hist.hist(data_ciste[k], bins=bins, color=barvy[i], edgecolor='black', alpha=0.75, density=False)
    ax_hist.set_title(f"{'c' if i==0 else 'd'}) Histogram – {k}\n(bez odlehlých pozorování)", fontweight='bold')
    ax_hist.set_xlabel("Nárůst výkonu (FPS)")
    ax_hist.set_ylabel("Četnost")
    ax_hist.set_xlim(spolecne_min - 1, spolecne_max + 1)
    ax_hist.grid(axis='y', linestyle='--', alpha=0.6)

for i, k in enumerate(karty):
    ax_qq = plt.subplot(3, 2, 5 + i)
    stats.probplot(data_ciste[k], dist="norm", plot=ax_qq)
    ax_qq.set_title(f"{'e' if i==0 else 'f'}) Q-Q graf – {k}\n(bez odlehlých pozorování)", fontweight='bold')
    ax_qq.set_xlabel("Teoretické kvantily (normální rozdělení)")
    ax_qq.set_ylabel("Výběrové kvantily nárůstu (FPS)")
    ax_qq.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout(rect=[0, 0, 1, 0.94])
vystup_pdf = "DU1S_grafy.pdf"
plt.savefig(vystup_pdf, format="pdf")
print(f"\n>>> GRAF BYL ÚSPĚŠNĚ ULOŽEN DO SOUBORU: {vystup_pdf} <<<")