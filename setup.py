
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fi:
    requirements = [v.rstrip("\n") for v in fi.readlines()]

setuptools.setup(
    name="wallfit",                     # This is the name of the package
    version="0.0.1",                        # The initial release version
    author="Dovydas Rudys",                     # Full name of the author
    description="Make any wallpaper fit your screen",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=["wallfit"],    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    install_requires=requirements           # Install other dependencies if any
)