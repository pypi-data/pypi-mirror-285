from setuptools import setup, find_packages

setup(
    name='easyjson_custom',
    version='0.1',
    packages=find_packages(),
    install_requires=[
    ],
    author='None scripts',
    description='библиотека easyjson немного упрощает работу с json файлами',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/NoneScripts/easyjson',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='>=3.4',
)

