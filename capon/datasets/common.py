import logging
import os


RESOURCES_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../resources'))
logging.info(f'RESOURCES_ROOT_PATH = "{RESOURCES_ROOT_PATH}"')


def get_resource_path(path):
    return os.path.normpath(f'{RESOURCES_ROOT_PATH}/{path}')