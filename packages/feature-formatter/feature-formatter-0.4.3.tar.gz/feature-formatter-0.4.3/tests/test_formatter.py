import os

import pytest

from featureformatter import AudioFormatter, ObjectFormatter


def test_stress(en_phone_formatter):
    assert en_phone_formatter.get_phone_stress("AH0") is False
    assert en_phone_formatter.get_phone_stress("AH") is None
    assert en_phone_formatter.get_phone_stress("AH1") is True
    assert en_phone_formatter.get_phone_stress("AH", return_detail=True) is None
    assert en_phone_formatter.get_phone_stress("AH0_I", return_detail=True) == 0
    assert en_phone_formatter.get_phone_stress("AH1", return_detail=True) == 1
    assert en_phone_formatter.get_phone_stress("AH2", return_detail=True) == 2


def test_normal_case(
    en_formatter_upper,
    de_formatter_upper,
    en_formatter_normal,
    de_formatter_normal,
    fr_formatter_normal,
    es_formatter_normal,
):
    he = en_formatter_upper.format_text("hello")
    assert he[0] == "HELLO"
    assert len(he[1]) == 0

    he = de_formatter_upper.format_text("hello")
    assert he[0] == "HELLO"
    assert len(he[1]) == 0

    he = en_formatter_normal.format_text("Hello")
    assert he[0] == "Hello"
    assert len(he[1]) == 0

    he = de_formatter_normal.format_text("Hello")
    assert he[0] == "Hello"
    assert len(he[1]) == 0

    he = fr_formatter_normal.format_text("Hello")
    assert he[0] == "Hello"
    assert len(he[1]) == 0

    he = es_formatter_normal.format_text("Hello")
    assert he[0] == "Hello"
    assert len(he[1]) == 0


def test_text_change(
    en_formatter_upper, de_formatter_normal, fr_formatter_normal, es_formatter_normal
):
    en_result = en_formatter_upper.format_text("__123, $5 200-seat")
    assert en_result[0] == "ONE HUNDRED AND TWENTY THREE FIVE DOLLARS TWO HUNDRED SEAT"
    assert len(en_result[1]) == 3

    de_result = de_formatter_normal.format_text("__123, $5")
    assert len(de_result[0].split()) == 3
    assert len(de_result[1]) == 2

    fr_result = fr_formatter_normal.format_text("__123, $5")
    assert fr_result[0] == "cent vingt trois cinq dollars"
    assert len(fr_result[1]) == 2

    es_result = es_formatter_normal.format_text("__123, $5")
    assert es_result[0] == "ciento veintitrés cinco dólares"
    assert len(es_result[1]) == 2


def test_percent_and(
    en_formatter_upper, de_formatter_normal, fr_formatter_normal, es_formatter_normal
):
    en_result = en_formatter_upper.format_text("4% &five")
    assert en_result[0] == "FOUR PERCENT AND FIVE"
    assert len(en_result[1]) == 2

    en_result = en_formatter_upper.format_text("4% & ")
    assert en_result[0] == "FOUR PERCENT AND"
    assert len(en_result[1]) == 2

    de_result = de_formatter_normal.format_text("4% &vier")
    assert de_result[0] == "vier Prozent und vier"
    assert len(de_result[1]) == 2

    fr_result = fr_formatter_normal.format_text("4% &vier")
    assert fr_result[0] == "quatre pourcent et vier"
    assert len(fr_result[1]) == 2

    es_result = es_formatter_normal.format_text("4% &vier")
    assert es_result[0] == "cuatro porciento y vier"
    assert len(es_result[1]) == 2


def test_year_formatter(
    en_formatter_upper, de_formatter_normal, fr_formatter_normal, es_formatter_normal
):
    en_result = en_formatter_upper.format_text("in year 1977, he died")
    assert en_result[0] == "IN YEAR NINETEEN SEVENTY SEVEN HE DIED"

    en_result = en_formatter_upper.format_text("1977, he died")
    assert en_result[0] == "NINETEEN SEVENTY SEVEN HE DIED"

    en_result = en_formatter_upper.format_text("in 2200, he died")
    assert en_result[0] == "IN TWENTY TWO HUNDRED HE DIED"

    en_result = en_formatter_upper.format_text("2200, he died")
    assert en_result[0] == "TWO THOUSAND TWO HUNDRED HE DIED"

    de_result = de_formatter_normal.format_text("im 2005, he died")
    assert de_result[0].startswith("im zweitausendfünf")

    en_result = en_formatter_upper.format_text("2005, he died")
    assert en_result[0] == "TWO THOUSAND AND FIVE HE DIED"

    en_result = en_formatter_upper.format_text("in 1900s, 1990s")
    assert en_result[0] == "IN NINETEEN HUNDREDS NINETEEN NINETIES"

    de_result = de_formatter_normal.format_text("1900s")
    assert de_result[0] == "neunzehnhundert"

    de_result = de_formatter_normal.format_text("1000, he died")
    assert de_result[0].startswith("eintausend")

    fr_result = fr_formatter_normal.format_text("1000, he died")
    assert fr_result[0].startswith("mille")

    es_result = es_formatter_normal.format_text("1000, he died")
    assert es_result[0].startswith("mil")


def test_special_char(
    en_formatter_upper, de_formatter_normal, fr_formatter_normal, es_formatter_normal
):
    en_result = en_formatter_upper.format_text("über straß")
    assert en_result[0].startswith("BER STRA")

    de_result = de_formatter_normal.format_text("über straß")
    assert de_result[0].startswith("über straß")

    fr_result = fr_formatter_normal.format_text("gîte épître relève, zèle")
    assert fr_result[0].startswith("gîte épître relève zèle")

    es_result = es_formatter_normal.format_text("ecólogo afección qtünqué, zèle")
    assert es_result[0].startswith("ecólogo afección qtünqué zèle")


def test_kmh(en_formatter_upper, de_formatter_normal, fr_formatter_normal):
    en_result = en_formatter_upper.format_text("150 km/h")
    assert en_result[0] == "ONE HUNDRED AND FIFTY KILOMETERS PER HOUR"

    en_result = en_formatter_upper.format_text("150km/h")
    assert en_result[0] == "ONE HUNDRED AND FIFTY KILOMETERS PER HOUR"

    de_result = de_formatter_normal.format_text("150km/h")
    assert de_result[0] == "einhundertfünfzig Kilometer pro Stunde"


def test_abbr(en_formatter_upper, de_formatter_normal):
    en_result = en_formatter_upper.format_text("he wakes up at one A.m.")
    assert en_result[0] == "HE WAKES UP AT ONE AM"
    assert en_result[1]["A.m."] == "AM"

    en_result = en_formatter_upper.format_text("he wakes up at one a.m")
    assert en_result[0] == "HE WAKES UP AT ONE A M"
    assert len(en_result[1]) == 0

    en_result = en_formatter_upper.format_text("Mr Zhou and Mr.Bob and MRHello")
    assert en_result[0] == "MISTER ZHOU AND MISTER BOB AND MRHELLO"
    assert len(en_result[1]) == 2

    en_result = en_formatter_upper.format_text("he is TV etc.")
    assert en_result[0] == "HE IS T V ET CETERA"
    assert len(en_result[1]) == 2

    en_result = en_formatter_upper.format_text("This is No. 7")
    assert en_result[0] == "THIS IS NUMBER SEVEN"
    assert len(en_result[1]) == 2

    en_result = en_formatter_upper.format_text("This is No.7")
    assert en_result[0] == "THIS IS NUMBER SEVEN"
    assert len(en_result[1]) == 2

    en_result = en_formatter_upper.format_text("No. I am ok")
    assert en_result[0] == "NO I AM OK"
    assert len(en_result[1]) == 0

    en_result = en_formatter_upper.format_text("No.I am ok")
    assert en_result[0] == "NO I AM OK"
    assert len(en_result[1]) == 0

    de_result = de_formatter_normal.format_text("z.B. I am ok")
    assert de_result[0] == "zum Beispiel I am ok"

    de_result = de_formatter_normal.format_text("z.b. I am ok")
    assert de_result[0] == "z b I am ok"

    de_result = de_formatter_normal.format_text("z.B.I am ok")
    assert de_result[0] == "z B I am ok"


def test_nordic(ru_formatter_lower):
    ru_result = ru_formatter_lower.format_text("Я в порядке")
    assert ru_result[0] == "я в порядке"


def test_phone_formatter(
    en_phone_formatter, de_phone_formatter, fr_phone_formatter, es_phone_formatter
):
    en_result = en_phone_formatter.get_phone_root("AE1_I")
    assert en_result == "AE"

    en_result = en_phone_formatter.get_phone_stress("AE1_I")
    assert en_result == 1

    de_result = de_phone_formatter.get_phone_root("AE:_I")
    assert de_result == "AE:"

    de_result = de_phone_formatter.get_phone_stress("AE:_I")
    assert de_result is None

    en_result = en_phone_formatter.is_vowel("AE")
    assert en_result is True

    de_result = de_phone_formatter.is_vowel("AE:_I")
    assert de_result is False

    de_result = de_phone_formatter.is_vowel("ae")
    assert de_result is False

    fr_result = fr_phone_formatter.is_vowel("ae")
    assert fr_result is False

    fr_result = fr_phone_formatter.is_vowel("A")
    assert fr_result is True

    es_result = es_phone_formatter.is_vowel("a")
    assert es_result is True


def test_audio_formatter():
    audio_file = os.path.join(os.path.dirname(__file__), "test.wav")
    noise_file = os.path.join(os.path.dirname(__file__), "cut_10_52.wav")

    assert int(AudioFormatter.rms_file(audio_file)) == 7107

    start, end = AudioFormatter.trim_noise(noise_file, overwrite=False)
    assert round(start, 1) == 0.7
    assert round(end, 1) == 0.9

    assert AudioFormatter.wav_size_to_dur(audio_file) == 0.785


def test_object_formatter():
    res = ObjectFormatter.round_float(
        {"a": 0.123123123123, "b": 0.9999999, "c": [0.00000001, 0.123123123]}
    )
    assert res["a"] == 0.123
    assert res["b"] == 0.999
    assert res["c"] == [0.001, 0.123]
