import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyscriptpacker",
    author="3D Ninjas GmbH",
    author_email="niklas@3dninjas.io",
    description="Convert Python packages into a single file.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/3dninjas/pyscriptpacker2",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    license="GPLv3",
    python_requires=">=2.7",
)
