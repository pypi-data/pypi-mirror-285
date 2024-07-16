from setuptools import setup, find_packages
import os


def find_pyc_files(package_dir):
    pyc_files = []
    for root, _, files in os.walk(package_dir):
        for file in files:
            if file.endswith(".pyc"):
                pyc_files.append(os.path.relpath(os.path.join(root, file), package_dir))
    return pyc_files


package_data = {"bullpenfi": find_pyc_files("bullpenfi")}

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="bullpenfi",
    version="0.1.10",
    author="Hongjun Wu",
    author_email="your-email@example.com",
    description="A description of your package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bullpenfi",
    packages=find_packages(),
    package_data=package_data,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["requests", "numpy"],
)
