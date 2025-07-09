import pytest

from lambda_python.tools.lambda_config import *

def test_parse_values_hex():
    s = '0x000001DEADFACE00AABBCCDDEEFF0000000000000000'
    data = parse_values([s])
    assert data == bytes.fromhex('000001DEADFACE00AABBCCDDEEFF0000000000000000')


def test_parse_values_string():
    s = 'HelloWorld'
    data = parse_values([s])
    assert data == s.encode('utf-8')

def test_parse_values_multiple():
    s = ['0x1','0xDEADFACE']
    data = parse_values(s)
    assert data == bytes.fromhex('00000001DEADFACE')

