"""A setuptools based setup module."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python3-cyberfusion-cluster-cli",
    version="1.11.5.1.2",
    description="CLI for Core API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    author="William Edwards",
    author_email="wedwards@cyberfusion.nl",
    url="https://vcs.cyberfusion.nl/core/python3-cyberfusion-core-cli",
    platforms=["linux"],
    packages=[
        "cyberfusion.CoreCli",
        "cyberfusion.ClusterCli",
    ],
    data_files=[],
    package_dir={"": "src"},
    install_requires=[
        "python3-cyberfusion-common",
        "python3-cyberfusion-cluster-apicli>=3.0",
        "python3-cyberfusion-cluster-support>=1.49.6",
        "click==8.1.7",
        "plotext==5.2.8",
        "requests==2.25.1",
        "rich==13.3.1",
        "typer==0.12.3",
    ],
    extras_require={"borg": ["cryptography==42.0.8"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["cyberfusion", "core", "cli"],
    license="MIT",
    entry_points={
        "console_scripts": [
            "corectl=cyberfusion.CoreCli.main:app",
            "clusterctl=cyberfusion.ClusterCli:main",
        ]
    },
)
