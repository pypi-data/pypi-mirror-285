"""Describe our module distribution to Distutils."""

# Import future modules
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Import third-party modules
from setuptools import find_packages
from setuptools import setup
import os
from codecs import open

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "arthub_login_widgets", "__version__.py"), "r", "utf-8") as f:
    exec(f.read(), about)

resource_files = []
for root, _, files in os.walk(os.path.join(here, 'arthub_login_widgets', 'resources', 'client')):
    for file in files:
        resource_files.append(os.path.relpath(os.path.join(root, file), 'arthub_login_widgets'))

setup(
    name="arthub_login_widgets",
    version=about["__version__"],
    author="Joey Ding",
    author_email="joeyding@tencent.com",
    url="https://git.woa.com/lightbox/internal/arthub_login_widgets",
    package_dir={"": "."},
    packages=find_packages("."),
    description="A Qt Widget for login ArtHub.",
    entry_points={},
    include_package_data=True,
    package_data={"arthub_login_widgets": ["*.png", "*.qss"] + resource_files},
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "arthub_api>=1.9.2",
        "platformdirs==2.0.2",
        "pyyaml==5.3",
        "Qt.py"
    ]
)
