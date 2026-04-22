from setuptools import setup, find_packages


with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="critiplot",
    version="2.1.1",
    packages=find_packages(),

    install_requires=[
        "numpy>=2.0,<=2.2.2",
        "pandas>=2.0,<=2.3.2",
        "matplotlib>=3.5,<=3.9.2",
        "seaborn>=0.12,<=0.13.2",
        "pyarrow>=10.0,<=21.0.0",
        "openpyxl>=3.0,<=3.1.5"

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