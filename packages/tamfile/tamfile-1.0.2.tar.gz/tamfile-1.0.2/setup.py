from setuptools import setup, find_packages

setup(
    name="tamfile",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[],
    author="TheTNTTeam",
    author_email="bestwebsitetrustmebro@proton.me",
    description="Library for creating and reading TAM (Text and Media) files.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Thetntteam/tamfilelib/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
