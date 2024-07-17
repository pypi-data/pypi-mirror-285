from setuptools import setup, find_packages

setup(
    name="MultiDataPlotting",
    version="0.5.0",
    author="Wei Wang",
    author_email="wwang487@wisc.edu",
    description="A package for plotting multiple datasets",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="http://github.com/wwang487/MultiDataPlotting",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=open("requirements.txt").read().splitlines(),
)
