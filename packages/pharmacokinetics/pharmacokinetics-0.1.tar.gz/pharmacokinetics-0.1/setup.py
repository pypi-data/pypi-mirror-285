import setuptools
import pharmacokinetics

with open("README.md", "r") as f:
    readme = f.read()

setuptools.setup(
    name="pharmacokinetics",
    version=pharmacokinetics.__version__,
    description=pharmacokinetics.__description__,
    long_description=readme,
    long_description_content_type="text/markdown",
    author=pharmacokinetics.__author__,
    url="https://github.com/xyzpw/pharmacokinetics-module/",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    keywords=[
        "pharmacokinetics",
        "pharmacodynamics",
        "pharmacology",
        "pharmacy",
        "chemistry",
    ],
    license="MIT",
)
