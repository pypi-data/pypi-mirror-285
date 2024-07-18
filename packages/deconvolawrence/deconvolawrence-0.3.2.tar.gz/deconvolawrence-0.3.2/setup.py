import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="deconvolawrence",

    version="0.3.2",

    author="Lawrence Collins",
    author_email="cm19ljc@leeds.ac.uk",
    description="Automated deconvolution of mass spectra datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lawrencecollins/deconvolawrence",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    setup_requires=['wheel'],
    install_requires=['unidec', 'seaborn'],

    package_data={'':['*.dll']},

)
