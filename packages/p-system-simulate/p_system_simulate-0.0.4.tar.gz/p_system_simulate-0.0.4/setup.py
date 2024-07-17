import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = '0.0.4'
PACKAGE_NAME = 'p_system_simulate'
AUTHOR = 'Pablo García López' 
AUTHOR_EMAIL = 'pablogl2002@gmail.com' 
URL = 'https://github.com/pablogl2002' 

DESCRIPTION = 'Library to simulate P Systems'
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding='utf-8')

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages(),
    include_package_data=True
)