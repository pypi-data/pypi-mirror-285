import pytest

from iccore import network

def test_get_request():

    url = "bad_url"

    with pytest.raises(ValueError):
        network.make_get_request(url)
