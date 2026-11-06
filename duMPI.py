import sys

def pozice_bitove_masky(maska: int) -> tuple[int, ...]:
    pozice = []
    while maska:
        nejmensi_bit = maska & -maska
        pozice.append(nejmensi_bit.bit_length() - 1)
        maska ^= nejmensi_bit
    return tuple(pozice)


def formatuj_mnozinu(maska: int) -> str:
    return "{" + ",".join(map(str, pozice_bitove_masky(maska))) + "}"


def najdi_koncepty(
    masky_radku: list[int], pocet_atributu: int, podpora: float
):
    pocet_objektu = len(masky_radku)
    vsechny_atributy = (1 << pocet_atributu) - 1
    koncepty: dict[int, int] = {}

    for kandidatni_intent in range(vsechny_atributy + 1):
        rozsah = 0
        for index_objektu, radek in enumerate(masky_radku):
            if radek & kandidatni_intent == kandidatni_intent:
                rozsah |= 1 << index_objektu

        if rozsah:
            intent_konceptu = vsechny_atributy
            for index_objektu, radek in enumerate(masky_radku):
                if rozsah & (1 << index_objektu):
                    intent_konceptu &= radek
        else:
            intent_konceptu = vsechny_atributy

        koncepty[rozsah] = intent_konceptu

    vyhovujici_koncepty = [
        (rozsah, intent)
        for rozsah, intent in koncepty.items()
        if rozsah.bit_count() / pocet_objektu >= podpora
    ]
    vyhovujici_koncepty.sort(
        key=lambda koncept: (
            koncept[0].bit_count(),
            pozice_bitove_masky(koncept[0]),
        )
    )
    return vyhovujici_koncepty


def najdi_pravidla(
    masky_radku: list[int], pocet_atributu: int, podpora: float
) -> list[tuple[int, int]]:
    pocet_objektu = len(masky_radku)
    vsechny_atributy = (1 << pocet_atributu) - 1
    cache_rozsahu: dict[int, int] = {}

    def rozsah_pro_intent(intent: int) -> int:
        if intent not in cache_rozsahu:
            rozsah = 0
            for index_objektu, radek in enumerate(masky_radku):
                if radek & intent == intent:
                    rozsah |= 1 << index_objektu
            cache_rozsahu[intent] = rozsah
        return cache_rozsahu[intent]

    pravidla = []
    for leva_strana in range(1, vsechny_atributy + 1):
        rozsah_leve_strany = rozsah_pro_intent(leva_strana)
        if not rozsah_leve_strany:
            continue
        if rozsah_leve_strany.bit_count() / pocet_objektu < podpora:
            continue

        dostupna_prava_strana = vsechny_atributy ^ leva_strana
        prava_strana = dostupna_prava_strana
        while prava_strana:
            if (
                rozsah_pro_intent(leva_strana | prava_strana)
                == rozsah_leve_strany
            ):
                pravidla.append((leva_strana, prava_strana))
            prava_strana = (prava_strana - 1) & dostupna_prava_strana

    pravidla.sort(
        key=lambda pravidlo: (
            pravidlo[0].bit_count(),
            pozice_bitove_masky(pravidlo[0]),
            pravidlo[1].bit_count(),
            pozice_bitove_masky(pravidlo[1]),
        )
    )
    return pravidla


def vyres(data: str) -> str:
    radky = iter(data.splitlines())
    pocet_testu = int(next(radky))
    vystup: list[str] = []

    for _ in range(pocet_testu):
        pocet_objektu, pocet_atributu = map(int, next(radky).split())
        matice_neostrosti = [
            list(map(float, next(radky).split())) for _ in range(pocet_objektu)
        ]
        prahy_neostrosti = list(map(float, next(radky).split()))
        prahy_podpory = list(map(float, next(radky).split()))

        for prah_neostrosti, podpora in zip(prahy_neostrosti, prahy_podpory):
            masky_radku = []
            for radek in matice_neostrosti:
                maska = 0
                for index_atributu, hodnota in enumerate(radek):
                    if hodnota >= prah_neostrosti:
                        maska |= 1 << index_atributu
                masky_radku.append(maska)

            koncepty = najdi_koncepty(masky_radku, pocet_atributu, podpora)
            vystup.append(
                f"Number of concepts with support>={podpora:.2f} is: "
                f"{len(koncepty)}"
            )
            for rozsah, intent in koncepty:
                vystup.append(
                    f"({formatuj_mnozinu(rozsah)},{formatuj_mnozinu(intent)})"
                )

            pravidla = najdi_pravidla(masky_radku, pocet_atributu, podpora)
            vystup.append(
                "Number of rules with confidence=1.00 from concepts is: "
                f"{len(pravidla)}"
            )
            for leva_strana, prava_strana in pravidla:
                vystup.append(
                    f"{formatuj_mnozinu(leva_strana)}"
                    f"=>{formatuj_mnozinu(prava_strana)}"
                )

    return "\n".join(vystup) + "\n"


if __name__ == "__main__":
    sys.stdout.write(vyres(sys.stdin.read()))
