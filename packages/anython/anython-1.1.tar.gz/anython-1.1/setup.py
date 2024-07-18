from setuptools import setup, find_packages

setup(
    name='anython',
    version='1.1',
    author='defzaid',
    description='no dec',
    packages=find_packages(),
    install_requires=[
        'anython>=1.0',
        'kivy>=2.3.0', 
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)