#!/usr/bin/env python
"""
jgtfx2console
"""

from setuptools import find_packages, setup

#from jgtfx2console import __version__ as version


#from jgtpy import __version__ as version
def read_version():
    with open("jgtfx2console/__init__.py") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.strip().split()[-1][1:-1]

version = read_version()



# INSTALL_REQUIRES = [
#     'pandas>=0.25.1',
#     'python-dotenv>=0.19.2',
#     'jgtutils>=0.1.67',
#     'tlid'

# ]

# EXTRAS_DEV_LINT = [
#     "flake8>=3.6.0,<3.7.0",
#     "isort>=4.3.4,<4.4.0",
# ]

# EXTRAS_DEV_TEST = [
#     "coverage",
#     "pytest>=3.10",
# ]

# EXTRAS_DEV_DOCS = [
#     "readme_renderer",
#     "sphinx",
#     "sphinx_rtd_theme>=0.4.0",
# ]

setup(
    name='jgtfx2console',
    version=version,
    description='JGTrading get data from fxconnect Dataframes',
    long_description=open('README.rst').read(),
    author='GUillaume Isabelle',
    author_email='jgi@jgwill.com',
    url='https://github.com/jgwill/jgtfx2console',
    packages=find_packages(),
    #packages=find_packages(include=['jgtfx2console', 'jgtfx2console.forexconnect', 'jgtfx2console.forexconnect.lib', 'jgtfx2console.forexconnect.lib.windows', 'jgtfx2console.forexconnect.lib.linux','jgtfx2console/**'], exclude=['*test*']),
    include_package_data=True,
    #install_requires=INSTALL_REQUIRES,
    # entry_points={
    #     'console_scripts': ['fxcli2console=jgtfx2console.fxcli2console:main'],
    # },
    # extras_require={
    #     'dev': (EXTRAS_DEV_LINT + EXTRAS_DEV_TEST + EXTRAS_DEV_DOCS),
    #     'dev-lint': EXTRAS_DEV_LINT,
    #     'dev-test': EXTRAS_DEV_TEST,
    #     'dev-docs': EXTRAS_DEV_DOCS,
    # },
    #license='MIT',
    #keywords='data',
    classifiers=[
        "Development Status :: 5 - Production/Stable", 
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent", 
        "Topic :: Software Development :: Libraries :: Python Modules", 
        "Programming Language :: Python :: 3.7.16", 
    ],
)
