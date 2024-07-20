from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()


setup(
    name='LIB_ADTECH',
    version='1.0.10',
    license='MIT License',
    author='Alan, Fabiano e Yan',
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords='driverWait, librarySelenium, Adlib',
    description=u'Funcoes uteis para desenvolvimento web.',
    packages=['Adlib'],
    install_requires=['requests'],
)
