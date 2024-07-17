from setuptools import setup, find_packages

VERSION = '0.0.3'
DESCRIPTION = 'Utilities for Polimi MUFASA users'
LONG_DESCRIPTION = ''

# Setting up
setup(
    name="mufasa-polimi",
    version=VERSION,
    author="Alberto Rota",
    author_email="<alberto1.rota@polimi.it>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    keywords=['python', 'slurm', 'hpc'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix"
    ]
)