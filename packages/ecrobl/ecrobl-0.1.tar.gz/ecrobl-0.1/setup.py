from setuptools import setup, find_packages

setup(
    name='ecrobl',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'ecrobl = ecrobl.__main__:main',
        ],
    },
)
