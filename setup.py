from setuptools import setup

setup(
    name='wdimgfix',
    version='0.1',
    py_modules=['wdimgfix'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        wdimgfix=wdimgfix:cli
    ''',
)

