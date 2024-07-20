import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="benchnirs",
    version="1.2.7",
    author="Johann Benerradi",
    author_email="johann.benerradi@gmail.com",
    description="Benchmarking framework for machine learning with fNIRS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/HanBnrd/benchnirs",
    license="GNU GPLv3+",
    packages=setuptools.find_packages(),
    install_requires=[
        "lazy_loader",
        "tqdm",
        "numpy<2",
        "pandas",
        "scipy",
        "mne",
        "matplotlib",
        "seaborn",
        "scikit-learn",
        "torch",
        "nirsimple"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
