from setuptools import setup, find_packages

setup(
    name="kavian",
    version="0.1.0",
    author="Adam Torres Encarnacion",
    author_email="art5809@psu.edu",
    description="Extends Pandas and Scikit with tools for Advanced Statistical Analysis",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AdamPSU/Kavian",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy', 'pandas', 'scikit-learn'
    ],
)