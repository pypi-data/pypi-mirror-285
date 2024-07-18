from setuptools import setup, find_packages

setup(
    name="manufacture",
    version="0.5.9",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'manufacture = manufacture.manufacture:main',
        ],
    },
    author="Spandan Chavan",
    author_email="spandanchavan727477@gmail.com",
    description="A simple command-line tool to create and manage files.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Spandan7724/manufacture.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
