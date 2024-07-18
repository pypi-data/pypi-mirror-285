from setuptools import find_packages, setup

setup(
    name="derek-git",
    version="0.0.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click",
        "GitPython",
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "derek-git = cli.main:cli",
        ],
    },
)
