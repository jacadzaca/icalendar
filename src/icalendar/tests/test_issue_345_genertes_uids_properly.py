'''Issue #345 - Why is tools.UIDGenerator a class (that must be instantiated) instead of a module?

see https://github.com/collective/icalendar/issues/345
'''
import pytest

from icalendar.tools import UIDGenerator

@pytest.mark.parametrize('host_name, unique', [
    ('example.com', ''),
    ('test.test', ''),
    ('example.com', '123'),
    ('test.test', '123')
])
def test_uid_generator_uses_host_name(host_name, unique):
    uid = UIDGenerator.uid(host_name=host_name, unique=unique)
    assert uid.split('@')[1] == host_name

@pytest.mark.parametrize('host_name, unique', [
    ('example.com', '123'),
    ('test.test', '123')
])
def test_uid_generator_uses_unique(host_name, unique):
    uid = UIDGenerator.uid(host_name=host_name, unique=unique)
    assert uid.split('-')[1] == f'{unique}@{host_name}'

