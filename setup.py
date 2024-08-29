from setuptools import setup, find_packages


with open("README.md", "r") as readme_file:
    readme = readme_file.read()


base_packages = [
    "requests>=2.31.0",
    "numpy>=1.26.4",
    "pandas>=1.5.0",
    "tqdm>=4.66.3",
    "joblib",
]

plotly_packages = ["plotly>=4.7.1"]
altair_packages = ["altair"]
test_packages = ["pytest", "ipython", "tox"]
docs_packages = ["black>=24.3.0"]
dev_packages = (
    ["notebook", "matplotlib", "ipywidgets", "seaborn", "themes"]
    + ["scikit-learn>=1.5.0"]
    + altair_packages
    + docs_packages
    + test_packages
)


setup(
    name="capon",
    version="0.0.94",
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
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
