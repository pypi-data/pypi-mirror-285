import codecs
import os

from setuptools import find_packages, setup

# # these things are needed for the README.md show on pypi
# here = os.path.abspath(os.path.dirname(__file__))

# with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
#     long_description = "\n" + fh.read()


VERSION = '0.0.2'
DESCRIPTION = 'Someones leetspeak that supports Windows, MacOS, and Linux'
LONG_DESCRIPTION = 'Someones leetspeak. Supporting Windows, MacOS, and Linux. It has support for hotkeys'

# Setting up
setup(
    name="aidedp_ml",
    version=VERSION,
    author="xiaobai",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        'getch; platform_system=="Unix"',
        'getch; platform_system=="MacOS"',
    ],
    keywords=['python', 'mac', 'windows'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)