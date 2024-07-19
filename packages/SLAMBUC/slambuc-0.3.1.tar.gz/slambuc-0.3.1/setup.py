# Copyright 2023 Janos Czentye
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import pathlib

import setuptools

setuptools.setup(
    name="SLAMBUC",
    # version=slambuc.__version__,
    description="Serverless Layout Adaptation with Memory-Bounds and User Constraints",
    long_description=(pathlib.Path(__file__).parent / "README.md").read_text(),
    long_description_content_type='text/markdown',
    author="Janos Czentye",
    author_email="czentye@tmit.bme.hu",
    project_urls={"Repository": "https://github.com/hsnlab/SLAMBUC",
                  "Homepage": "https://github.com/hsnlab/SLAMBUC/wiki",
                  "Issue Tracker": "https://github.com/hsnlab/SLAMBUC/issues"},
    packages=setuptools.find_packages(include=['slambuc', 'slambuc.*'],
                                      exclude=['tests', 'validation']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires='>=3.10',
    license="Apache 2.0",
    keywords="cloud serverless ilp dp tree",
    install_requires=[
        'networkx~=3.3',
        'numpy~=1.26.4',
        'PuLP~=2.9.0',
        'matplotlib~=3.9.1',
        'pandas~=2.2.2',
        'scipy~=1.14.0',
        'cspy~=1.0.3',
    ],
    extras_require={'tests': ['pytest~=8.2.2',
                              'pygraphviz~=1.13',
                              'tabulate~=0.9.0',
                              'docplex~=2.27.239'],
                    'validation': ['tabulate~=0.9.0',
                                   'Click~=8.1.7',
                                   'psutil~=6.0.0']},
    package_data={'*': ['*.pkl',
                        '*.csv']},
    include_package_data=True,
    zip_safe=False
)
