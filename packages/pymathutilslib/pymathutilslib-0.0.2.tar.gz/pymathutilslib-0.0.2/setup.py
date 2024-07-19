from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='pymathutilslib',
    version='0.0.2',
    license='MIT License',
    author='Ismael Nascimento',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='ismaelnjr@icloud.com.br',
    keywords='module example',
    description=u'Teste de como criar um modulo python',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[''],)