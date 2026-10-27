"""
Tests de adlam_translit.py

Lancer :  python3 -m unittest -v
"""

import unittest

from adlam_translit import adlam_to_latin, latin_to_adlam

# Marques combinantes Adlam
VOWEL_LENGTHENER = chr(0x1E945)
GEMINATION_MARK = chr(0x1E946)


class CasReels(unittest.TestCase):
    """Cas relevés à la main, avec le résultat attendu écrit en dur."""

    def test_ulluundu_adlam_vers_latin(self):
        # u, l, gémination, u, allongement, n, d, u -> aucune marque après le n
        adlam = "𞤵𞤤𞥆𞤵𞥅𞤲𞤣𞤵"
        self.assertEqual(adlam_to_latin(adlam), "ulluundu")

    def test_ulluundu_latin_vers_adlam(self):
        adlam = "𞤵𞤤𞥆𞤵𞥅𞤲𞤣𞤵"
        self.assertEqual(latin_to_adlam("ulluundu"), adlam)

    def test_mots_simples_avec_majuscule(self):
        self.assertEqual(adlam_to_latin("𞤀𞤣𞤤𞤢𞤥"), "Adlam")
        self.assertEqual(adlam_to_latin("𞤆𞤵𞤤𞤢𞤪"), "Pular")


class MarquesEtMajuscules(unittest.TestCase):
    def test_voyelle_longue_apres_majuscule(self):
        # majuscule A + allongement -> "Aa" (et non "A" tout seul)
        self.assertEqual(adlam_to_latin(chr(0x1E900) + VOWEL_LENGTHENER), "Aa")

    def test_gemination_apres_majuscule(self):
        # majuscule L + gémination + a -> "Lla" (et non "LLa")
        self.assertEqual(
            adlam_to_latin(chr(0x1E902) + GEMINATION_MARK + chr(0x1E922)), "Lla"
        )

    def test_latin_double_devient_marque(self):
        self.assertEqual(latin_to_adlam("ii"), chr(0x1E92D) + VOWEL_LENGTHENER)
        self.assertEqual(latin_to_adlam("lla"), chr(0x1E924) + GEMINATION_MARK + chr(0x1E922))  # voyelle après : marque

    def test_marque_en_debut_de_texte_ne_plante_pas(self):
        self.assertEqual(adlam_to_latin(GEMINATION_MARK), "")
        self.assertEqual(adlam_to_latin(VOWEL_LENGTHENER + "𞤢"), "a")

    def test_voyelle_longue_apres_consonne_est_ignoree(self):
        # l'allongement ne s'applique qu'aux voyelles
        self.assertEqual(adlam_to_latin("𞤤" + VOWEL_LENGTHENER), "l")


class LettresSpeciales(unittest.TestCase):
    def test_implosives(self):
        self.assertEqual(latin_to_adlam("ɓ"), chr(0x1E929))
        self.assertEqual(latin_to_adlam("ɗ"), chr(0x1E92F))
        self.assertEqual(latin_to_adlam("ƴ"), chr(0x1E930))
        self.assertEqual(adlam_to_latin(chr(0x1E929)), "ɓ")

    def test_implosive_majuscule(self):
        self.assertEqual(latin_to_adlam("Ɓ"), chr(0x1E907))
        self.assertEqual(adlam_to_latin(chr(0x1E907)), "Ɓ")

    def test_digrammes_lettres_uniques(self):
        self.assertEqual(latin_to_adlam("gb"), chr(0x1E940))
        self.assertEqual(latin_to_adlam("kp"), chr(0x1E942))
        self.assertEqual(latin_to_adlam("sh"), chr(0x1E943))
        self.assertEqual(adlam_to_latin(chr(0x1E940)), "gb")


class GroupesPrenasalises(unittest.TestCase):
    """ng et nd s'écrivent lettre par lettre ; ŋ est une lettre distincte de ng."""

    N, G, D, ENG = chr(0x1E932), chr(0x1E93A), chr(0x1E923), chr(0x1E93D)

    def test_ng_est_n_puis_g(self):
        self.assertEqual(latin_to_adlam("ng"), self.N + self.G)
        self.assertNotEqual(latin_to_adlam("ng"), self.ENG)

    def test_nd_est_n_puis_d(self):
        self.assertEqual(latin_to_adlam("nd"), self.N + self.D)

    def test_eng_reste_une_lettre_distincte(self):
        self.assertEqual(latin_to_adlam("ŋ"), self.ENG)
        self.assertEqual(adlam_to_latin(self.ENG), "ŋ")
        # n + g en Adlam ne devient jamais ŋ
        self.assertEqual(adlam_to_latin(self.N + self.G), "ng")

    def test_nh_nest_plus_un_alias_de_eng(self):
        self.assertEqual(latin_to_adlam("nh"), self.N + chr(0x1E938))  # n + h

    def test_ngaari_aller_retour(self):
        self.assertEqual(adlam_to_latin(latin_to_adlam("ngaari")), "ngaari")


class LettreNya(unittest.TestCase):
    """La lettre NYA s'écrit ñ en latin (et non plus ɲ ou ny)."""

    def test_ntilde_adlam_latin(self):
        self.assertEqual(latin_to_adlam("ñ"), chr(0x1E93B))
        self.assertEqual(latin_to_adlam("Ñ"), chr(0x1E919))
        self.assertEqual(adlam_to_latin(chr(0x1E93B)), "ñ")
        self.assertEqual(adlam_to_latin(chr(0x1E919)), "Ñ")

    def test_ny_equivaut_a_ntilde(self):
        self.assertEqual(latin_to_adlam("ny"), chr(0x1E93B))
        self.assertEqual(latin_to_adlam("Ny"), chr(0x1E919))
        self.assertEqual(latin_to_adlam("NY"), chr(0x1E919))
        self.assertEqual(latin_to_adlam("nyaamde"), latin_to_adlam("ñaamde"))

    def test_nya_revient_toujours_en_ntilde(self):
        self.assertEqual(adlam_to_latin(latin_to_adlam("nyaamde")), "ñaamde")

    def test_ancienne_graphie_api_toujours_acceptee(self):
        self.assertEqual(latin_to_adlam("ɲ"), chr(0x1E93B))
        self.assertEqual(latin_to_adlam("Ɲ"), chr(0x1E919))

    def test_ntilde_aller_retour(self):
        self.assertEqual(adlam_to_latin(latin_to_adlam("ñaamde")), "ñaamde")


class AllerRetour(unittest.TestCase):
    MOTS = [
        "pular",
        "ulluundu",
        "ɓoggo",
        "Ɓoggo",
        "ɗum",
        "jam",
        "Adlam",
        "on belike e jam",
        "haa",
        "Aabaa",
        "kuuɓal",
        "ngaari",
        "ŋ",
    ]

    def test_latin_adlam_latin(self):
        for mot in self.MOTS:
            with self.subTest(mot=mot):
                self.assertEqual(adlam_to_latin(latin_to_adlam(mot)), mot)

    def test_chiffres_et_ponctuation(self):
        for texte in ["2026", "0123456789", "jam?", "jam!"]:
            with self.subTest(texte=texte):
                self.assertEqual(adlam_to_latin(latin_to_adlam(texte)), texte)


class Robustesse(unittest.TestCase):
    def test_chaine_vide(self):
        self.assertEqual(adlam_to_latin(""), "")
        self.assertEqual(latin_to_adlam(""), "")

    def test_espaces_et_retours_a_la_ligne_conserves(self):
        self.assertEqual(adlam_to_latin("𞤢 𞤢\n𞤢"), "a a\na")
        self.assertEqual(latin_to_adlam("a a\na"), "𞤢 𞤢\n𞤢")

    def test_caracteres_inconnus_conserves(self):
        self.assertEqual(latin_to_adlam("é"), "é")
        self.assertEqual(adlam_to_latin("é"), "é")


class ConsonneDoubleSelonLeContexte(unittest.TestCase):
    """Gémination seulement si une voyelle suit la consonne doublée."""

    def test_devant_voyelle_marque(self):
        self.assertEqual(latin_to_adlam("ullu"), "\U0001E935\U0001E924\U0001E946\U0001E935")

    def test_devant_consonne_deux_lettres(self):
        # winnden : « nn » suivi de « d » -> deux lettres, pas de marque
        self.assertEqual(latin_to_adlam("winnden"),
                         "\U0001E931\U0001E92D\U0001E932\U0001E932\U0001E923\U0001E92B\U0001E932")
        self.assertNotIn(chr(0x1E946), latin_to_adlam("Winnden"))

    def test_fin_de_mot_deux_lettres(self):
        self.assertNotIn(chr(0x1E946), latin_to_adlam("gall"))

    def test_majuscule_conservee(self):
        self.assertEqual(adlam_to_latin(latin_to_adlam("Winnden")), "Winnden")

    def test_voyelles_toujours_allongees(self):
        self.assertIn(chr(0x1E945), latin_to_adlam("uu"))


class ExceptionAllah(unittest.TestCase):
    """Dans « Allah », les deux « l » restent : pas de marque de gémination."""

    def test_allah_garde_deux_lettres(self):
        for mot in ("Allah", "allah", "ALLAH"):
            self.assertNotIn(chr(0x1E946), latin_to_adlam(mot), mot)

    def test_allah_en_phrase(self):
        self.assertNotIn(chr(0x1E946), latin_to_adlam("Ko Allah, jam."))

    def test_retour_en_latin(self):
        self.assertEqual(adlam_to_latin(latin_to_adlam("Allah")), "Allah")

    def test_autres_mots_inchanges(self):
        self.assertIn(chr(0x1E946), latin_to_adlam("addu"))
        self.assertIn(chr(0x1E946), latin_to_adlam("ullu"))
        self.assertIn(chr(0x1E946), latin_to_adlam("Allaaji"))  # autre mot : la règle normale s'applique


class ExceptionAllahExemples(unittest.TestCase):
    def test_allah_garde_les_deux_l(self):
        self.assertEqual(latin_to_adlam("allah"), "\U0001E922\U0001E924\U0001E924\U0001E922\U0001E938")
        self.assertNotIn(chr(0x1E946), latin_to_adlam("Allah"))

    def test_exemples_de_la_regle(self):
        self.assertEqual(latin_to_adlam("addu"), "\U0001E922\U0001E923\U0001E946\U0001E935")
        self.assertEqual(latin_to_adlam("jannde"),
                         "𞤶𞤢𞤲𞤲𞤣𞤫")

    def test_l_exception_ne_touche_pas_les_autres_mots(self):
        self.assertIn(chr(0x1E946), latin_to_adlam("ullu"))
        self.assertIn(chr(0x1E946), latin_to_adlam("allaa"))   # autre mot : règle normale


class ExceptionAllahou(unittest.TestCase):
    def test_allahou_garde_deux_lettres(self):
        for mot in ("allahou", "Allahou"):
            self.assertNotIn(chr(0x1E946), latin_to_adlam(mot), mot)


if __name__ == "__main__":
    unittest.main()
