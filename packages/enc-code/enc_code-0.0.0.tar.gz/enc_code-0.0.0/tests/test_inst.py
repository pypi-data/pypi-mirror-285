import pytest

from src import enc_code


def test_blowup():
    with pytest.raises(Exception):
        enc_code.inst.blowup()
