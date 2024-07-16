# setup.py
from setuptools import setup, find_packages

setup(
    name="incp_v1",
    version="0.1.0",
    packages=find_packages(),
    install_requires=['pandas'],
    entry_points={
        'console_scripts': [
            'incp=incp.incp:main',
        ],
    },
    author="Aviral Srivastava",
    author_email="aviralsrivastava284@gmail.com",
    description="Get the Employee Data and incp Data",
    long_description_content_type='text/markdown',
    url="https://github.com/A284viral/incp_v1",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)