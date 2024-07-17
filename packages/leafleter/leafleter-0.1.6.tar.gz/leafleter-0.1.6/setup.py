import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="leafleter",
    version="0.1.6",
    author="Mateusz Konieczny",
    author_email="matkoniecz@tutanota.com",
    description="Helper script to generate leaflet map websites.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matkoniecz/leafleter_python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 
