import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pdistx",
    author="3D Ninjas GmbH",
    author_email="niklas@3dninjas.io",
    description="A toolset for distributing Python projects in a convenient way.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/3dninjas/pdistx",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    license="GPLv3",
    python_requires=">=3.9",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "pdistx=pdistx.__main__:main",
            "pvendor=pvendor.__main__:main",
            "pvariant=pvariant.__main__:main",
            "ppack=ppack.__main__:main",
        ],
    },
)
