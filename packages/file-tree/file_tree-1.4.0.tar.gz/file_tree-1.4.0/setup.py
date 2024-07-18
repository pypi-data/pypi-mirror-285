"""Install file-tree package."""
import setuptools

setuptools.setup(
    name="file-tree",
    version="1.4.0",
    url="https://git.fmrib.ox.ac.uk/fsl/file-tree",
    author="Michiel Cottaar",
    author_email="MichielCottaar@protonmail.com",
    description="Describe structure directory for pipeline",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src", exclude=("tests*", "*.egg-info")),
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "xarray",
        "pandas",
        "parse",
        "rich",
        'importlib_metadata; python_version < "3.10"',
    ],
    project_urls={
        "Documentation": "https://open.win.ox.ac.uk/pages/fsl/file-tree/",
    },
    entry_points={
        "console_scripts": ["file-tree=file_tree.app:run"],
    },
    extras_require = {
        "app": ["textual"],
    },
    include_package_data=True,
    license="MIT",
    license_file="LICENSE",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
)
