from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='hercules',
    version='0.1.0',
    author="johnson2427",
    author_email="blakeejohnson39@gmail.com",
    description="Web Scraping ResultsDb",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/johnson2427/hercules",
    packages=["hercules"],  # needs a folder with __init__()
    # py_modules=["resultsdb_main"],  # use if you only have modules
    # package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "pandas",
        "scrapy",
        "scrapy_selenium",
        "pymongo",
        "selenium",
        "requests"
    ],
    extras_require={
        "dev": [
            "pytest>=3.7",
        ]
    }
)
