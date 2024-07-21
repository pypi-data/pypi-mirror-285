from setuptools import setup, find_packages

setup(
    name="FAImageGen",
    version="0.1.0",
    description="Python SDK for ImageGen",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Saliou Kane",
    author_email="saliou@fotographer.ai",
    url="https://github.com/FotographerAI/ImageGen-sdk/",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
