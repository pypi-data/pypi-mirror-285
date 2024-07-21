import setuptools
import pytz

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="quickremi",
    version="1.0.14",
    author="Aru Raghuvanshi",
    author_email="sixdigitco@gmail.com",
    description="A wrapper of REMI library to build UI front-ends purely using Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["quickremi"],
    install_requires=["remi", "pytz"],
    python_requires=">=3.7"
)
