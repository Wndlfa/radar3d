"""Testes do classificador de licença (o diferencial — precisa ser confiável)."""

from radar3d.domain.licenses import LicenseTier, classify_license


def test_cults_commercial_is_green():
    v = classify_license("cults3d", "Cults Commercial Use")
    assert v.tier is LicenseTier.VENDA_PERMITIDA


def test_personal_use_is_red():
    v = classify_license("cults3d", "Personal use only")
    assert v.tier is LicenseTier.SOMENTE_PESSOAL


def test_cults_real_license_names():
    # Nomes reais retornados pela API do Cults3D.
    assert classify_license("cults3d", "CULTS PU - Private Use").tier is LicenseTier.SOMENTE_PESSOAL
    assert classify_license("cults3d", "CULTS CU - Commercial Use").tier is LicenseTier.VENDA_PERMITIDA


def test_subscription_is_yellow():
    v = classify_license("printables", "Commercial with subscription")
    assert v.tier is LicenseTier.EXIGE_LICENCA


def test_cc_nc_is_red():
    v = classify_license("thingiverse", "CC BY-NC 4.0")
    assert v.tier is LicenseTier.SOMENTE_PESSOAL


def test_thingiverse_real_license_names():
    red = classify_license(
        "thingiverse", "Creative Commons - Attribution - Non-Commercial"
    )
    assert red.tier is LicenseTier.SOMENTE_PESSOAL
    green = classify_license("thingiverse", "Creative Commons - Attribution")
    assert green.tier is LicenseTier.VENDA_PERMITIDA
    assert classify_license("thingiverse", "Public Domain").tier is LicenseTier.VENDA_PERMITIDA


def test_myminifactory_licenses():
    assert (
        classify_license("myminifactory", "Creative Commons Noncommercial").tier
        is LicenseTier.SOMENTE_PESSOAL
    )
    assert (
        classify_license("myminifactory", "Commercial use allowed").tier
        is LicenseTier.VENDA_PERMITIDA
    )


def test_empty_is_conservative_gray():
    v = classify_license("cults3d", "")
    assert v.tier is LicenseTier.NAO_IDENTIFICADA


def test_unknown_falls_back_to_gray_not_green():
    # R6: na dúvida, nunca a faixa mais permissiva.
    v = classify_license("cults3d", "some weird custom text")
    assert v.tier is LicenseTier.NAO_IDENTIFICADA


def test_ip_flag_in_license_text():
    v = classify_license("cults3d", "Commercial use — Pikachu figurine")
    assert v.possible_protected_ip is True


def test_ip_flag_in_title():
    # O IP aparece no TÍTULO, não na licença (caso real "Lugia Controller Stand").
    v = classify_license("cults3d", "CULTS PU - Private Use", title="Lugia Controller Stand")
    assert v.possible_protected_ip is True
    v2 = classify_license("cults3d", "CULTS PU - Private Use", title="Master Chief Stand")
    assert v2.possible_protected_ip is True


def test_no_false_positive_generic_title():
    v = classify_license("cults3d", "CULTS CU - Commercial Use", title="Universal Controller Stand")
    assert v.possible_protected_ip is False
