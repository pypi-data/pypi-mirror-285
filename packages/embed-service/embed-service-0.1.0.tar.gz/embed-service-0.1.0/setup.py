from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="embed-service",  
    version="0.1.0",  
    description="A simple command-line tool for testing srv-embed-service.",
    author="Rafael Silva",
    author_email="rtsilva@bi4all.pt",
    url="https://github.com/BI4ALL/embed-service",  # Let's create this REPO 
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "embed = embed.__main__:main",
        ],
    },
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
