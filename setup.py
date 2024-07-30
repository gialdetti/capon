from setuptools import setup, find_packages


with open("README.md", "r") as readme_file:
    readme = readme_file.read()


base_packages = [
    "requests>=2.22.0",
    "numpy>=1.17.3",
    "pandas>=1.0.3",
    "tqdm",
]
plotly_packages = base_packages + ["plotly>=4.7.1"]
test_packages = ["pytest", "ipython", "tox"]
docs_packages = ["black"]
dev_packages = (
    ["notebook", "matplotlib", "ipywidgets", "seaborn", "altair", "themes"]
    + ["scikit-learn"]
    + docs_packages
    + test_packages
)


setup(
    name="capon",
    version="0.0.8",
    author="Eyal Gal",
    author_email="eyalgl@gmail.com",
    description="Capital Market in Python",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords=[
        "capital markets",
        "stocks",
        "stock market",
        "finance",
        "dataset",
        "portfolio",
        "dashboard",
        "yahoo finance",
    ],
    url="https://github.com/gialdetti/capon/",
    packages=find_packages(),
    install_requires=base_packages,
    extras_require={
        "test": test_packages,
        "docs": docs_packages,
        "dev": dev_packages,
    },
    include_package_data=True,
    # package_data={'datasets': ['capon/resources/*']},
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
