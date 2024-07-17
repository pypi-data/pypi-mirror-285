from setuptools import setup, find_packages

setup(
    name='codenrock',
    version='0.5',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'tuspy',
        'argparse',
    ],
    entry_points={
        'console_scripts': [
            'codenrock=codenrock.cli:main',
        ],
    },
)
