from setuptools import setup, find_packages

setup(
    name='deeppostal',
    version='0.0.0',
    description='A deep learning postal address parser',
    author='igospatial',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    python_requires='>=3.11',
    install_requires=[
    ],
)
