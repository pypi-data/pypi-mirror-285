from setuptools import setup, find_packages

setup(
    name='geo2zip',
    version='0.1.2',
    author='Javier Lopez',
    author_email='jlopex@gmail.com',
    description='Geo2Zip is a Python package that provides a fast and efficient way to find the closest US ZIP code for a given latitude and longitude. It uses a KDTree for quick nearest-neighbor lookup, making it suitable for geospatial queries.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jlopex/geo2zip',
    python_requires='>=3.7',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    install_requires=[
        'scipy',
    ],
    extras_require={
        'dev': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'geo2zip=geo2zip.main:main',
        ],
    },
    package_data={
        'geo2zip': ['data/geo2zip.csv'],
    },
    include_package_data=True,
)

