# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import setuptools

path = os.path.abspath(os.path.dirname(__file__))
exec(open(os.path.join(path, 'geotk/version.py')).read())

with open("README.md", "r") as fp:
    long_description = fp.read()

setuptools.setup(
    name = "geotk",
    version=__version__,
    author="Ian Mackinnon",
    author_email="imackinnon@gmail.com",
    description="Conversion tools for 2D file formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ianmackinnon/geotk",
    keywords='geometry obj csv convert',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=["numpy", "beautifulsoup4", "lxml"],
    python_requires='>=3',
    scripts=["scripts/obj2svg", "scripts/svg2obj", ],
    setup_requires=["pytest-runner"],
    tests_requires=["pytest", "tox", "coverage", "pytest-cov"],
)
