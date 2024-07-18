from setuptools import setup, find_packages

setup(
    name="webpage2content",
    version="1.0.2",
    author="Mikhail Voloshin",
    author_email="mvol@mightydatainc.com",
    description="A simple Python package to extract text content from a webpage.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Mighty-Data-Inc/webpage2content",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "html2text",
        "openai",
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "webpage2content=webpage2content.webpage2content_impl:main",
        ],
    },
)
