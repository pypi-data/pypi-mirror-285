from setuptools import setup, find_packages

setup(
    name="rickrollprinter",
    version="0.1.3",  
    packages=find_packages(),
    install_requires=[
        'pygame',
    ],
    include_package_data=True,
    package_data={
        'rickrollprinter': ['never_gonna_give_you_up.mp3'],
    },
    author="Juan Andrés Young Hoyos",
    author_email="juanandresyounghoyos@gmail.com",
    description="A Python package that prints Rickroll lyrics and plays the song.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jayounghoyos/rickrollprinter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)