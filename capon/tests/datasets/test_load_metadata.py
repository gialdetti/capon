import logging

logging.basicConfig(format="[%(asctime)s] %(message)s", level=logging.INFO)

from capon.datasets import load_metadata


def test():
    metadata = load_metadata()
    metadata["sector"].value_counts()
    metadata["industry"].value_counts()
    metadata["updated_at"].value_counts().sort_index()
