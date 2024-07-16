from setuptools import setup, find_packages


setup(
    name='sysbro',
    version='0.0.3',
    packages=find_packages(),
    install_requires=[
        'psutil',
        'psycopg2-binary',
        'redis',
        'tqdm',
        'click'
    ],
    entry_points={
        'console_scripts': [
            'sysbro = sysbro.main:cli',
        ],
    },
)
