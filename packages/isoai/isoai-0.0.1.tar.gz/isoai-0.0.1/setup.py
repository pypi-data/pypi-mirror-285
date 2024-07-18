from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="isoai",  
    version="0.0.1",  
    author="Jazmia Henry",
    author_email="isojaz@isoai.co",
    description="Compress, Trace and Deploy Your Models with Iso!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iso-ai/bitmodal",  
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        # List your dependencies here
        "torch>=1.7.1",
        # Any other dependencies
    ],
)
