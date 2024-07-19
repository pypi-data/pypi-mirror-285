from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='pymathutilslib-v001',
    version='0.0.1',
    license='MIT License',
    author='Ismael Nascimento',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='ismaelnjr@icloud.com.br',
    keywords='module example',
    description=u'Teste de como criar um modulo python',
    packages=['pymathutilslib'],
    install_requires=[''],)