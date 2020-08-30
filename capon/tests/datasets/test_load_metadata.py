import logging; logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.INFO)

from capon.datasets import load_metadata


def test():
    load_metadata()


