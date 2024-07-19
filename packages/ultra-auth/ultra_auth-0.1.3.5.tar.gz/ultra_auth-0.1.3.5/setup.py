from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="ultra_auth",
    version="0.1.3.5",
    author="Shane Barbetta",
    author_email="shane@barbetta.me",
    description="A compact auth client for UltraDNS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sbarbvett/ultra_auth",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.25.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
