from enum import Enum


class UntisFileStundenplan(Enum):
    UNTERRICHT_NUMMER = 1
    KLASSE = 2
    LEHRER = 3
    FACH = 4
    RAUM = 5
    TAG = 6
    STUNDE = 7
    STUNDENLAENGE = 8


class UntisFileKlassen(Enum):
    """
    Enum for the columns of the Klasse Untis-DIF-file (GPU003.TXT).
    See https://platform.untis.at/HTML/WebHelp/de/untis/index.html
    -> search for "export dif" -> Export/Import DIF-Dateien.
    Or see https://help.untis.at/hc/de/article_attachments/4407687247762.
    """
    NAME = 1
    LANGNAME = 2
    STATISTIK = 3
    RAUM = 4
    KENNZEICHEN = 5
    FREI = 6
    MIN_STUNDEN_PRO_TAG = 7
    MAX_STUNDEN_PRO_TAG = 8
    MIN_MITTAGSPAUSE = 9
    MAX_MITTAGSPAUSE = 10
    HAUPTFACH_FOLGE = 11
    HAUPTFACH_HINT = 12
    KLASSENGRUPPE = 13
    SCHULSTUFE = 14
    ABTEILUNG = 15
    FAKTOR = 16
    STUDENTEN_WEIBLICH = 17
    STUDENTEN_MAENNLICH = 18
    SCHULFORM = 19
    UNTERRICHTSBEGINN = 20
    UNTERRICHTSENDE = 21
    SONDERTEXT = 22
    BESCHREIBUNG = 23
    FARBE_VORDERGRUND = 24
    FARBE_HINTERGRUND = 25
    STATISTIK_2 = 26
    NAME_VORJAHR = 27
    FAKTOR_EXPORT = 28
    ALIAS = 29
    KLASSENLEHRER = 30
    HAUPTKLASSE = 31
    STUDENTEN_INTERGESCHLECHTLICH = 32


class UntisFileLehrer(Enum):
    """
    Enum for the columns of the Lehrer Untis-DIF-file (GPU004.TXT).
    See https://platform.untis.at/HTML/WebHelp/de/untis/index.html
    -> search for "export dif" -> Export/Import DIF-Dateien.
    Or see https://help.untis.at/hc/de/article_attachments/4407687247762.
    """
    NAME = 1
    LANGNAME = 2
    STATISTIK_1 = 3
    PERSONALNUMMER = 4
    STAMMRAUM = 5
    KENNZEICHEN = 6
    FREI = 7
    MIN_STUNDEN_PRO_TAG = 8
    MAX_STUNDEN_PRO_TAG = 9
    MIN_HOHLSTUNDEN = 10
    MAX_HOHLSTUNDEN = 11
    MIN_MITTAGSPAUSE = 12
    MAX_MITTAGSPAUSE = 13
    MAX_STUNDEN_FOLGE = 14
    WOCHEN_SOLL = 15
    WOCHEN_WERT = 16
    ABTEILUNG_1 = 17
    WERT_FAKTOR = 18
    ABTEILUNG_2 = 19
    ABTEILUNG_3 = 20
    STATUS = 21
    JAHRES_SOLL = 22
    TEXT = 23
    BESCHREIBUNG = 24
    FARBE_VORDERGRUND = 25
    FARBE_HINTERGRUND = 26
    STATISTIK_2 = 27
    BERECHNETER_FAKTOR = 28
    VORNAME = 29
    TITEL = 30
    GESCHLECHT = 31
    STAMMSCHULE = 32
    EMAIL = 33
    SPERRVERMERK = 34
    WOCHEN_SOLL_MAXIMAL = 35
    ALIAS = 36
    PERSONALNUMMER_2 = 37
    STUNDENSATZ = 38
    TELEFONNUMMER = 39
    MOBILTELEFONNUMMER = 40
    GEBURTSDATUM = 41
    NAME_EXTERNES_ELEMENT = 42
    TEXT_2 = 43
    EINTRITTS_DATUM = 44
    AUSTRITTS_DATUM = 45


class UntisFileRaeume(Enum):
    """
    Enum for the columns of the Räume Untis-DIF-file (GPU005.TXT).
    See https://platform.untis.at/HTML/WebHelp/de/untis/index.html
    -> search for "export dif" -> Export/Import DIF-Dateien.
    Or see https://help.untis.at/hc/de/article_attachments/4407687247762.
    """
    NAME = 1
    LANGNAME = 2
    AUSWEICHRAUM = 3
    KENNZEICHEN = 4
    FREI = 5
    DISLOZ_KENNZEICHEN = 6
    RAUM_GEWICHT = 7
    KAPAZITAET = 8
    ABTEILUNG = 9
    GANG_1 = 10
    GANG_2 = 11
    SONDERTEXT = 12
    BESCHREIBUNG = 13
    FARBE_VORDERGRUND = 14
    FARBE_HINTERGRUND = 15
    STATISTIK_1 = 16
    STATISTIK_2 = 17


class UntisFileFaecher(Enum):
    """
    Enum for the columns of the Fächer Untis-DIF-file (GPU006.TXT).
    See https://platform.untis.at/HTML/WebHelp/de/untis/index.html
    -> search for "export dif" -> Export/Import DIF-Dateien.
    Or see https://help.untis.at/hc/de/article_attachments/4407687247762.
    """
    NAME = 1
    LANGNAME = 2
    STATISTIK_1 = 3
    RAUM = 4
    KENNZEICHEN = 5
    FREI = 6
    MIN_STUNDEN_PRO_WOCHE = 7
    MAX_STUNDEN_PRO_WOCHE = 8
    MIN_STUNDEN_NACHMITTAG = 9
    MAX_STUNDEN_NACHMITTAG = 10
    FACHFOLGE_KLASSE = 11
    FACHFOLGE_LEHRER = 12
    FACHGRUPPE = 13
    FAKTOR = 14
    FAKTOR_ = 15
    TEXT = 16
    BESCHREIBUNG = 17
    FARBE_VORDERGRUND = 18
    FARBE_HINTERGRUND = 19
    STATISTIK_2 = 20
    ALIAS = 21


class UntisFileUnterricht(Enum):
    """
    Enum for the columns of the Unterricht Untis-DIF-file (GPU002.TXT).
    See https://platform.untis.at/HTML/WebHelp/de/untis/index.html
    -> search for "export dif" -> Export/Import DIF-Dateien.
    Or see https://help.untis.at/hc/de/article_attachments/4407687247762.
    """
    UNTERRICHT_NUMMER = 1
    WOCHENSTUNDEN = 2
    WOCHENSTD_KLA = 3
    WOCHENSTD_LE = 4
    KLASSE = 5
    LEHRER = 6
    FACH = 7
    FACHRAUM = 8
    STATISTIK_1 = 9
    STUDENTENZAHL = 10
    WOCHENWERT = 11
    GRUPPE = 12
    ZEILENTEXT = 13
    ZEILENWERT = 14
    DATUM_VON = 15
    DATUM_BIS = 16
    JAHRESWERT = 17
    TEXT = 18
    TEILUNGS_NUMMER = 19
    STAMMRAUM = 20
    BESCHREIBUNG = 21
    FARBE_VORDERGRUND = 22
    FARBE_HINTERGRUND = 23
    KENNZEICHEN = 24
    FACHFOLGE_KLASSEN = 25
    FACHFOLGE_LEHRER = 26
    KLASSEN_KOLLISIONS_KENNZEICHEN = 27
    DOPPELSTUNDEN_MIN = 28
    DOPPELSTUNDEN_MAX = 29
    BLOCKGROESSE = 30
    STD_IM_RAUM = 31
    PRIORITAET = 32
    STATISTIK_1_LEHRER = 33
    STUDENTEN_MAENNLICH = 34
    STUDENTEN_WEIBLICH = 35
    WERT_FAKTOR = 36
    ZWEITE_BLOCKGROESSE = 37
    DRITTE_BLOCKGROESSE = 38
    ZEILENTEXT_2 = 39
    EIGENWERT_OHNE_FAKTOREN = 40
    EIGENWERT_IN_1_100000 = 41
    SCHUELERGRUPPE = 42
    WOCHENSTUNDEN_IN_JAHRES_PERIODEN_PLANUNG = 43
    JAHRESSTUNDEN = 44
    ZEILEN_UNTERRICHTSGRUPPE = 45
    STUDENTEN_INTERGESCHLECHTLICH = 46


class UntisFileZeitwuensche(Enum):
    """
    Enum for the columns of the Zeitwünsche Untis-DIF-file (GPU016.TXT).
    See https://platform.untis.at/HTML/WebHelp/de/untis/index.html
    -> search for "export dif" -> Export/Import DIF-Dateien.
    """
    ART_DES_ELEMENTS = 1
    KURZNAME_DES_ELEMENTS = 2
    TAG = 3
    STUNDE = 4
    ZEITWUNSCH = 5
