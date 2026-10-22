# =====================================================================
# BLOK 2: SPUSTIT, KDYŽ ZADÁNÍ ZAČÍNÁ VELKÝM F(x) (DISTRIBUČNÍ FUNKCE)
# =====================================================================
import sympy as sp

x, c = sp.symbols('x c', real=True)

# === ZDE UPRAVTE PODLE ZADÁNÍ ===
predpis_F = c * (1 - sp.cos(x))      # Vnitřek funkce F(x)
od = 0                         # Spodní hranice intervalu
do = sp.pi / 2                 # Horní hranice intervalu

procento_w = 0.40              # Procento z úlohy 2 (např. X je větší než w je 60 % -> 0.60)
body_kontroly = [-3, sp.pi / 4, 3]     # Body ze závorky v úloze 3: x ∈ {...}
hranice = sp.pi / 3            # Číslo z úlohy 4 (např. bude nejvýše pi/3)
p_kvantil = 0.60               # Procento z úlohy 5 (např. 60% kvantil -> 0.60)
# ================================
# Tahák: mocnina: x**2 | zlomek: 1/3 nebo sp.pi/2 | odmocnina: sp.sqrt(x)
#        3. odmocnina: x**(1/3) | sp.sin(x) | sp.cos(x) | sp.exp(x) | sp.log(x)

# 1. Konstanta c (na horní hranici "do" musí být F(x) rovna 1)
c_hodnota = sp.solve(sp.Eq(predpis_F.subs(x, do), 1), c)[0]
print(f"1. Konstanta c = {float(c_hodnota):.4f} (přesně: {c_hodnota})")

F_x = predpis_F.subs(c, c_hodnota)

# 2. Hodnota w, pro kterou P(X > w) = procento_w (tedy F(w) = 1 - procento_w)
reseni_w = sp.solve(sp.Eq(F_x, 1 - procento_w), x)
platne_w = [round(float(r.evalf()), 3) for r in reseni_w if r.is_real and float(od) - 1e-5 <= float(r.evalf()) <= float(do) + 1e-5]
print(f"\n2. Hodnota w (kde P(X > w) je {procento_w*100:.0f}%) = {platne_w}")

# 3. Hustota pravděpodobnosti f(x) (derivace F(x)) a kontrola 3 bodů
f_x = sp.diff(F_x, x)
print(f"\n3. Kontrola bodů hustoty f(x) [předpis je {f_x}, mimo interval je 0]:")
for b in body_kontroly:
    if float(b) < float(od) or float(b) > float(do): 
        hodnota = 0.0 # Mimo interval je hustota vždy 0!
    else: 
        hodnota = float(f_x.subs(x, b))
    print(f"   f({b}) = {hodnota:.3f}")

# 4. Pravděpodobnost (dosazuje se rovnou do F(x))
if float(hranice) <= float(od): p_mensi = 0.0
elif float(hranice) >= float(do): p_mensi = 1.0
else: p_mensi = float(F_x.subs(x, hranice))

print(f"\n4. Pravděpodobnost pro hranici {hranice}:")
print(f"   P(X <= {hranice}) [nejvýše / nepřekročí] = {p_mensi:.3f}")
print(f"   P(X > {hranice})  [větší než / překročí] = {1 - p_mensi:.3f}")

# 5. Střední hodnota E(X), směrodatná odchylka a kvantil
ex = float(sp.integrate(x * f_x, (x, od, do)))
ex2 = float(sp.integrate(x**2 * f_x, (x, od, do)))
std = float(sp.sqrt(ex2 - ex**2))
print(f"\n5. Střední hodnota E(X) = {ex:.3f} (na 2 místa: {ex:.2f})")
print(f"   Směrodatná odchylka  = {std:.3f} (na 2 místa: {std:.2f})")

reseni_kv = sp.solve(sp.Eq(F_x, p_kvantil), x)
platne_kv = [round(float(r.evalf()), 3) for r in reseni_kv if r.is_real and float(od) - 1e-5 <= float(r.evalf()) <= float(do) + 1e-5]
print(f"   Kvantil pro {p_kvantil*100:.0f}% (v {p_kvantil*100:.0f}% případů NEPŘEKROČÍ) = {platne_kv}")





# =====================================================================
# BLOK 1: SPUSTIT, KDYŽ ZADÁNÍ ZAČÍNÁ MALÝM f(x) (HUSTOTA)
# =====================================================================
x, c, t = sp.symbols('x c t', real=True)

# === ZDE UPRAVTE PODLE ZADÁNÍ ===
predpis = c * (5*x - x**2)       # Vnitřek funkce f(x)
od = 0                       # Spodní hranice intervalu
do = 5                        # Horní hranice intervalu

body_kontroly = [-6, 1, 6] # Body ze závorky v úloze 3: x ∈ {...}
hranice = 2                # Číslo z úlohy 4 (např. překročí hodnotu -0.5)
p_kvantil = 0.80              # Procento z úlohy 5 (např. 80% -> 0.80)
# ================================
# Tahák: mocnina: x**2 | zlomek: 1/3 nebo sp.pi/2 | odmocnina: sp.sqrt(x)
#        3. odmocnina: x**(1/3) | sp.sin(x) | sp.cos(x) | sp.exp(x) | sp.log(x)

# 1. Konstanta c (integrál z hustoty musí být 1)
c_hodnota = sp.solve(sp.Eq(sp.integrate(predpis, (x, od, do)), 1), c)[0]
print(f"1. Konstanta c = {float(c_hodnota):.4f} (na 3 místa: {float(c_hodnota):.3f})")

# 2. Minimální a maximální hodnota
print(f"2. Minimální hodnota = {float(od)} | Maximální hodnota = {float(do)}")

# 3. Distribuční funkce F(x) a kontrola 3 bodů (hlídá 0 a 1 mimo interval!)
f_x = predpis.subs(c, c_hodnota)
F_x = sp.integrate(f_x.subs(x, t), (t, od, x))
print(f"\n3. Kontrola bodů distribuční funkce F(x):")
for b in body_kontroly:
    if float(b) <= float(od): hodnota = 0.0
    elif float(b) >= float(do): hodnota = 1.0
    else: hodnota = float(F_x.subs(x, b))
    print(f"   F({b}) = {hodnota:.3f}")

# 4. Pravděpodobnost v intervalu
p_vetsi = sp.integrate(f_x, (x, hranice, do))
p_mensi = sp.integrate(f_x, (x, od, hranice))
print(f"\n4. Pravděpodobnost pro hranici {hranice}:")
print(f"   P(X > {hranice}) [překročí / větší než]    = {float(p_vetsi):.3f}")
print(f"   P(X < {hranice}) [nepřekročí / nejvýše]    = {float(p_mensi):.3f}")

# 5. Střední hodnota E(X), směrodatná odchylka a kvantil
ex = float(sp.integrate(x * f_x, (x, od, do)))
ex2 = float(sp.integrate(x**2 * f_x, (x, od, do)))
std = float(sp.sqrt(ex2 - ex**2))
print(f"\n5. Střední hodnota E(X) = {ex:.2f} (na 3 místa: {ex:.3f})")
print(f"   Směrodatná odchylka  = {std:.2f} (na 3 místa: {std:.3f})")

reseni_kv = sp.solve(sp.Eq(F_x, p_kvantil), x)
platne_kv = [round(float(r.evalf()), 3) for r in reseni_kv if r.is_real and float(od) - 1e-5 <= float(r.evalf()) <= float(do) + 1e-5]
print(f"   Kvantil pro {p_kvantil*100:.0f}% (v {p_kvantil*100:.0f}% případů NEPŘEKROČÍ) = {platne_kv}")