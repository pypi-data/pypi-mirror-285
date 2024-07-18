import os
import pickle
import shutil
import dotenv
from typing import Any


def get_cache_folderpath() -> str:
    '''
    Get the path to the cache folder
    '''
    if os.path.isfile('.env'):
        dotenv.load_dotenv(os.path.join(os.getcwd(), '.env'))
        cache_folderpath = os.path.normpath(os.environ['cache_folderpath'])
    else:
        cache_folderpath = os.path.abspath('cache')

    return cache_folderpath


def get_cache_filepath(filename: str) -> str:
    '''
    Construct the filepath for the given filename
    '''

    return os.path.join(get_cache_folderpath(), filename)


def write_to_cache(obj: Any, filename: str) -> None:
    '''
    Write the given `obj` to `filename` in the `cache` folder
    '''
    cache_folderpath = get_cache_folderpath()
    if not os.path.isdir(cache_folderpath):
        os.makedirs(cache_folderpath)

    with open(get_cache_filepath(filename), 'wb') as file:
        pickle.dump(obj, file)


def read_from_cache(filename: str) -> Any:
    '''
    Load the Python object that is stored in `filename` in the cache folder
    '''

    with open(get_cache_filepath(filename), 'rb') as file:
        obj = pickle.load(file)

    return obj


def file_in_cache(filename: str) -> bool:
    '''
    Returns True if the given filename is in cache, otherwise False
    '''
    return os.path.isfile(get_cache_filepath(filename))


def remove_from_cache(filename: str) -> None:
    '''
    Remove a file from the cache folder
    '''
    os.remove(get_cache_filepath(filename))


def clear_cache() -> None:
    '''
    Deletes the cache folder
    '''
    shutil.rmtree(get_cache_folderpath())
