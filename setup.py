from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = [
    "numpy>=1.17.3",
    "pandas>=1.0.3",
    "requests>=2.22.0",
    "plotly>=4.7.1",
    "tqdm",
]

setup(
    name="capon",
    version="0.0.6",
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
    install_requires=requirements,
    include_package_data=True,
    # package_data={'datasets': ['capon/resources/*']},
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
