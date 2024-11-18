from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stacksmith",
    version="0.0.51",
    author="Jashua Gupta",
    author_email="findjashua@gmail.com",
    description="Enhanced Git workflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/findjashua/stacksmith",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
    install_requires=[
        # Add any dependencies here
    ],
    entry_points={
        "console_scripts": [
            "ss=stacksmith.cli:main",
        ],
    },
)
