import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="pymessagelib",
    version="0.2.5",
    description="Give structure to hexadecimal messages.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/smalbadger/pymessagelib",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Telecommunications Industry",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Education :: Testing",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Software Development :: Testing",
    ],
    packages=["pymessagelib"],
    include_package_data=True,
    author="smalbadger",
    author_email="smalbadger@gmail.com",
    install_requires=["terminaltables"],
)
