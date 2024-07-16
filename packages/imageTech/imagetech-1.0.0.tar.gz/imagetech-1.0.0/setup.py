"""Setup for the chocobo package."""

import setuptools


setuptools.setup(
    author='Sarthak, Harshit',
    author_email="sarthak6jan16@gmail.com",
    name='imageTech',
    license="MIT",
    description='Python Library to process and compare images.',
    version='1.0.0',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[
        'opencv-python',
        'pillow',
        'pytest',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ],
)