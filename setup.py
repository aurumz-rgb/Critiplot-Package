from setuptools import setup, find_packages


with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="critiplot",
    version="2.1.0",
    packages=find_packages(),

    install_requires=[
        "numpy>=2.0,<3.0",
        "pandas>=2.0,<3.0",
        "matplotlib>=3.5,<4.0",
        "seaborn>=0.12,<1.0",
        "pyarrow>=10.0,<22.0",
        "openpyxl>=3.0,<4.0"
    ],
    author="Vihaan Sahu",
    author_email="pteroisvolitans12@gmail.com",
    description="Visualize risk-of-bias in systematic reviews and meta-analyses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aurumz-rgb/Critiplot-Package",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)