from setuptools import setup, find_packages

setup(
    name="critiplot",
    version="1.2.2",
    packages=find_packages(),
    install_requires=[
        "numpy==2.2.2",
        "pandas==2.3.2",
        "matplotlib==3.9.2",
        "seaborn==0.13.2",
        "pyarrow==21.0.0",
        "openpyxl==3.1.5"
    ],
    author="Vihaan Sahu",
    author_email="pterois.volitans12@gmail.com",
    description="Visualize risk-of-bias in systematic reviews and meta-analyses",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/aurumz-rgb/Critiplot-Package",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
