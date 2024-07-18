from src import cacheasy
import os
import pytest
import shutil


@pytest.fixture
def env_file_path():
    env_file_path = '.env'
    yield env_file_path
    os.remove(env_file_path)


@pytest.fixture()
def my_cool_x_cached_file_name():
    x = 5
    cache_file_path = 'my_cool_x'
    cacheasy.write_to_cache(x, cache_file_path)
    yield cache_file_path
    cacheasy.remove_from_cache(cache_file_path)


def test_cache_folder():
    assert cacheasy.get_cache_folderpath() == 'cache'


def test_cache_folder_with_env(env_file_path):

    with open(env_file_path, 'w') as env_file:
        env_file.write('cache_folderpath = ok/cache')
    assert cacheasy.get_cache_folderpath() == os.path.join('ok', 'cache')


def test_cache_filepath():
    assert cacheasy.get_cache_filepath('a') == os.path.join('cache', 'a')


def test_write_cache():
    x = 5
    cache_file_path = 'my_cool_x'
    cacheasy.write_to_cache(x, cache_file_path)
    assert os.path.isfile(os.path.join('cache', cache_file_path))
    cacheasy.remove_from_cache(cache_file_path)
    assert not cacheasy.file_in_cache(cache_file_path)


def test_write_cache_with_env(env_file_path):
    with open(env_file_path, 'w') as env_file:
        env_file.write('cache_folderpath = a/b/c')
    x = 5
    cache_file_path = 'my_cool_x'
    cacheasy.write_to_cache(x, cache_file_path)
    assert os.path.isfile(os.path.join('a', 'b', 'c', cache_file_path))
    cacheasy.remove_from_cache(cache_file_path)
    assert not cacheasy.file_in_cache(cache_file_path)

    shutil.rmtree('a')


def test_read(my_cool_x_cached_file_name):
    y = cacheasy.read_from_cache(my_cool_x_cached_file_name)
    assert y == 5


def test_clear(my_cool_x_cached_file_name):
    cacheasy.clear_cache()
    assert not os.path.isdir(cacheasy.get_cache_folderpath())
