from sporestack import utils


def test_random_token() -> None:
    assert utils.random_token() != utils.random_token()
    assert len(utils.random_token()) == 32
    assert utils.random_token().startswith("ss_t_")


def test_hash() -> None:
    assert utils.checksum("ss_m_1deadbeefcafedeadbeef1") == "0892"
