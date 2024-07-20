from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="my_package-12389",
    version="1.0.0",
    author="Your Name",
    author_email="sashaperevozniuk01@gmail.com",
    description="A short description of my package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/perevozniuk13/my_package-12389",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
      