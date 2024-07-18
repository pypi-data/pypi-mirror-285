from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))


VERSION = '0.0.1'
DESCRIPTION = 'Testing Framework'
LONG_DESCRIPTION = 'API Testing Framework that uses Jupyter Notebook to test and document the APIs behaviour '


# Setting up
setup(
    name="Framework-Callisto",
    version=VERSION,
    author="Ahmed Bada",
    author_email="<dexterhk01@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests', 'ipywidgets'],
    keywords=['python', 'Tesint', 'API', 'Jupyter', 'Notebook', 'Callisto'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ])