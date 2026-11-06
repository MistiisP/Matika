import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from pathlib import Path

soubor = "FPS_data.xlsx"
df = pd.read_excel(soubor)

karty = ["Nvidia RTX 3070 Ti", "AMD Radeon RX 6800 XT"]
zkratky = {
    "Nvidia RTX 3070 Ti": "Nvidia RTX 3070",
    "AMD Radeon RX 6800 XT": "AMD Radeon RX 6800",
}
vystup = Path("PS DU1 grafy")
vystup.mkdir(exist_ok=True)
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
        ("minimum", f"{st[k1]['min']:.3f}", f"{st[k2]['min']:.3f}"),
        ("dolní kvartil", f"{st[k1]['q1']:.3f}", f"{st[k2]['q1']:.3f}"),
        ("medián", f"{st[k1]['med']:.3f}", f"{st[k2]['med']:.3f}"),
        ("průměr", f"{st[k1]['mean']:.3f}", f"{st[k2]['mean']:.3f}"),
        ("horní kvartil", f"{st[k1]['q3']:.3f}", f"{st[k2]['q3']:.3f}"),
        ("maximum", f"{st[k1]['max']:.3f}", f"{st[k2]['max']:.3f}"),
        ("směrod. odchylka", f"{st[k1]['std']:.3f}", f"{st[k2]['std']:.3f}"),
        ("šikmost (e1071/mom)", f"{st[k1]['sik_e']:.3f} / {st[k1]['sik_m']:.3f}", f"{st[k2]['sik_e']:.3f} / {st[k2]['sik_m']:.3f}"),
        ("špičatost (kolem 0)", f"{st[k1]['spic_e']:.3f} / {st[k1]['spic_m']:.3f}", f"{st[k2]['spic_e']:.3f} / {st[k2]['spic_m']:.3f}"),
    ]
    for r in radky:
        print(f"{r[0]:<22} | {r[1]:<24} | {r[2]:<24}")

vypis_tabulku(st_puv, "TAB. 1: PŮVODNÍ DATA (Odpovědi 1 až 20)", offset=0)

print("\n--- ODLEHLÁ POZOROVÁNÍ (pro Odpověď 42) ---")
for k in karty:
    dh, hh, odl = odlehle_info[k]
    odl_text = ", ".join(f"{x:.3f}" for x in odl)
    print(f"{k}: Dolní hradba = {dh:.3f}, Horní hradba = {hh:.3f} | Počet odlehlých = {len(odl)} -> hodnoty: {odl_text}")

vypis_tabulku(st_cis, "TAB. 2: PO ODSTRANĚNÍ ODLEHLÝCH POZOROVÁNÍ (Odpovědi 21 až 40)", offset=20)

print(f"\n{'='*75}\nTEXTOVÁ ČÁST PRO NVIDIA RTX 3070 (Odpovědi 41 až 50)\n{'='*75}")
s3070 = st_cis[karty[0]]
print(f"Odpověď 41 (původní rozsah n) : {st_puv[karty[0]]['n']}")
odl_3070 = ", ".join(f"{x:.3f}" for x in odlehle_info[karty[0]][2])
print(f"Odpověď 42 (odlehlé hodnoty)  : Počet odlehlých je {len(odlehle_info[karty[0]][2])} (hodnoty: {odl_3070})")
print(f"Odpověď 43 (nový rozsah n)    : {s3070['n']}")
print(f"Odpověď 44 až 45 (min až max) : {s3070['min']:.3f} až {s3070['max']:.3f}")
print(f"Odpověď 46 (průměr)           : {s3070['mean']:.3f}")
print(f"Odpověď 47 (směr. odchylka)   : {s3070['std']:.3f}")
print(f"Odpověď 48 (medián - polovina): {s3070['med']:.3f}")
print(f"Odpověď 49 až 50 (Q1 až Q3)   : {s3070['q1']:.3f} až {s3070['q3']:.3f}")

print(f"\n{'='*75}\nOVĚŘENÍ NORMALITY A PRAVIDLO 2/3 SIGMA (Odpovědi 51 až 68)\n{'='*75}")
for idx, k in enumerate(karty):
    st_k = st_cis[k]
    m, sd = st_k['mean'], st_k['std']
    _, p_val = stats.shapiro(data_ciste[k])
    je_norm = ( -2 < st_k['sik_e'] < 2 ) and ( -2 < st_k['spic_e'] < 2 ) and (p_val > 0.05)
    
    start_odp = 51 if idx == 0 else 60
    print(f"\n>>> {k} (Odpovědi {start_odp} až {start_odp+8}) <<<")
    print(f"  Šikmost = {st_k['sik_e']:.3f}, Špičatost = {st_k['spic_e']:.3f}, Shapiro p-hodnota = {p_val:.3f}")
    print(f"  Verdikt normality: {'LZE předpokládat normální rozdělení (odpovídá / leží / leží / leží / lze)' if je_norm else 'NELZE předpokládat normální rozdělení'}")
    print(f"  Pravidlo 1 sigma (68 % hodnot): ({m - sd:.3f} ; {m + sd:.3f})")
    print(f"  Pravidlo 2 sigma (95 % hodnot): ({m - 2*sd:.3f} ; {m + 2*sd:.3f})")
    print(f"  Pravidlo 3 sigma (99,7% hodnot): ({m - 3*sd:.3f} ; {m + 3*sd:.3f})")


def pridej_normalni_krivku(ax, s):
    """Doplní histogram hustotou normálního rozdělení."""
    x = np.linspace(float(s.min()), float(s.max()), 300)
    ax.plot(x, stats.norm.pdf(x, np.mean(s), np.std(s, ddof=1)),
            color="darkorange", linewidth=2, label="Normální křivka")
    ax.legend(fontsize=11)


def nastav_pismo(ax):
    """Nastaví čitelné písmo společné pro všechny grafy."""
    ax.tick_params(axis="both", labelsize=14)
    ax.xaxis.label.set_size(16)
    ax.yaxis.label.set_size(16)
    ax.title.set_size(17)


def uloz_dvojice_grafu():
    """Uloží dvojice panelů pro obě karty se sjednoceným větším písmem."""
    popisky = [zkratky[k] for k in karty]
    puvodni = [data_puvodni[k] for k in karty]
    ciste = [data_ciste[k] for k in karty]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharex=True)
    for ax, data, popisek in zip(axes, puvodni, popisky):
        ax.boxplot(data, orientation="horizontal", patch_artist=True,
                   boxprops={"facecolor": "lightsteelblue"})
        ax.set(title=popisek, xlabel="Nárůst FPS (patched − release)",
               yticks=[1], yticklabels=["Původní data"])
        nastav_pismo(ax)
    fig.suptitle("Obr. 1: Vícenásobný krabicový graf původních dat",
                 fontsize=20)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(vystup / "01_vicenasobny_boxplot_puvodni_data.png", dpi=300)
    plt.close(fig)

    if any(len(odlehle_info[k][2]) for k in karty):
        fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharex=True)
        for ax, data, popisek in zip(axes, ciste, popisky):
            ax.boxplot(data, orientation="horizontal", patch_artist=True,
                       boxprops={"facecolor": "lightseagreen"})
            ax.set(title=popisek, xlabel="Nárůst FPS (patched − release)",
                   yticks=[1], yticklabels=["Po očištění"])
            nastav_pismo(ax)
        fig.suptitle(
            "Obr. 2: Vícenásobný krabicový graf po odstranění odlehlých hodnot",
            fontsize=20)
        fig.tight_layout(rect=[0, 0, 1, 0.92])
        fig.savefig(vystup / "02_vicenasobny_boxplot_po_ocisteni.png", dpi=300)
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for ax, data, popisek in zip(axes, ciste, popisky):
        ax.hist(data, bins="auto", density=True, color="seagreen",
                edgecolor="black")
        pridej_normalni_krivku(ax, data)
        ax.set(title=popisek, xlabel="Nárůst FPS (patched − release)",
               ylabel="Hustota")
        nastav_pismo(ax)
    fig.suptitle("Obr. 3: Histogramy očištěných nárůstů FPS", fontsize=20)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(vystup / "03_dvojice_histogramu_po_ocisteni.png", dpi=300)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for ax, data, popisek in zip(axes, ciste, popisky):
        stats.probplot(data, dist="norm", plot=ax)
        ax.set(title=popisek, xlabel="Teoretické kvantily",
               ylabel="Pozorované kvantily")
        nastav_pismo(ax)
    fig.suptitle("Obr. 4: Q-Q grafy očištěných nárůstů FPS", fontsize=20)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(vystup / "04_dvojice_qq_grafu_po_ocisteni.png", dpi=300)
    plt.close(fig)


uloz_dvojice_grafu()

with (vystup / "vysledky_tisiciny.txt").open("w", encoding="utf-8") as souhrn:
    for nazev_tabulky, statistiky in (
        ("TAB. 1 - původní data", st_puv),
        ("TAB. 2 - data po odstranění odlehlých pozorování", st_cis),
    ):
        souhrn.write(f"{nazev_tabulky}\n")
        for k in karty:
            souhrn.write(f"\n{zkratky[k]}\n")
            for ukazatel, hodnota in spocitej_radek(data_puvodni[k] if statistiky is st_puv else data_ciste[k]).items():
                if ukazatel == "n":
                    souhrn.write(f"{ukazatel}: {hodnota}\n")
                else:
                    souhrn.write(f"{ukazatel}: {hodnota:.3f}\n")
    souhrn.write("\nOdlehlá pozorování a vnitřní hradby\n")
    for k in karty:
        dolni, horni, odlehle = odlehle_info[k]
        hodnoty = ", ".join(f"{x:.3f}" for x in odlehle) or "žádné"
        souhrn.write(
            f"{zkratky[k]}: dolní hradba {dolni:.3f}, horní hradba {horni:.3f}, "
            f"odlehlé hodnoty: {hodnoty}\n"
        )

print(f"\nGrafy a souhrn na tisíciny byly uloženy do složky: {vystup}")
