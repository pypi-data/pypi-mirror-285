from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rickrollprinter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'pygame',
    ],
    author="Juan Andrés Young Hoyos",
    author_email="juanandresyounghoyos@gmail.com",
    description="A Python package that prints Rickroll lyrics and plays the song.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jayounghoyos/rickrollprinter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
