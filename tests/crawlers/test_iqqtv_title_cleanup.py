import pytest

from mdcx.crawlers.iqqtv import assert_web_number_suffix_site_matches, getWebNumber, remove_web_number_suffix


def test_iqqtv_title_cleanup_drops_prefixed_uncensored_suffix():
    title = "One more time, One more fuck caribbeancom_060626_001"

    assert getWebNumber(title, "060626_001") == "060626_001"
    assert remove_web_number_suffix(title, "060626_001") == "One more time, One more fuck"


def test_iqqtv_title_cleanup_drops_plain_uncensored_suffix():
    title = "One more time, One more fuck 060626_001"

    assert remove_web_number_suffix(title, "060626_001") == "One more time, One more fuck"


def test_iqqtv_title_cleanup_keeps_non_number_suffix():
    title = "One more time, One more fuck"

    assert remove_web_number_suffix(title, "060626_001") == title


def test_iqqtv_rejects_conflicting_uncensored_site_prefix():
    title = "One more time, One more fuck caribbeancom_060626_001"

    with pytest.raises(Exception, match="caribbeancom != 1pondo"):
        assert_web_number_suffix_site_matches(title, "060626_001")


def test_iqqtv_accepts_matching_uncensored_site_prefix():
    title = "One more time, One more fuck 1pondo_060626_001"

    assert_web_number_suffix_site_matches(title, "060626_001")
