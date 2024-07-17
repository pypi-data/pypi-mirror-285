from setuptools import setup, find_namespace_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

install_requires = list(filter(None, (this_directory / "requirements.txt").read_text().splitlines()))

setup(
    name='emonoda-plugin-confetti-hass',
    version="1.0.0",
    url="https://github.com/ASMfreaK/emonoda-plugin-confetti-hass",
    license="GPLv3",
    author="Pletenev Pavel",
    author_email="cpp.create@gmail.com",
    description="Home Assistant confetti plugin for emonoda",
    platforms="any",

    packages=find_namespace_packages(where='src/', include=['emonoda.plugins.confetti.hass']),
    package_dir={'': 'src'},
    package_data={
            "emonoda.plugins.confetti.hass": ["templates/*.mako"],
    },

    long_description=long_description,
    long_description_content_type='text/markdown',

    install_requires=install_requires,

    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        # "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: File Sharing",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
        "Operating System :: OS Independent",
        "Intended Audience :: System Administrators",
        "Intended Audience :: End Users/Desktop",
    ],
)
