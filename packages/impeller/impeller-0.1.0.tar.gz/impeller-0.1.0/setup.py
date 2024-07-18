from setuptools import setup, find_packages

setup(
    name="impeller",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch",
        "gdown",
        "scanpy",
        "pandas",
        "numpy",
        "scikit-learn",
        "dgl"
    ],
    entry_points={
        'console_scripts': [
            'impeller=impeller.main:main',
        ],
    },
    author="Ziheng Duan",
    author_email="duanziheng1206@gmail.com",
    description="Impeller is a package for spatial transcriptomics imputation using path-based graph neural networks.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/aicb-ZhangLabs/Impeller", 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)