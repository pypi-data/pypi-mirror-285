from setuptools import setup, find_packages

setup(
    name="pykawa",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
        # Example: 'requests', 'numpy',
    ],
    author="Araamouch",
    description="Helpers",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/araamouch/pydaa",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)