import setuptools
import os

def get_version():
    version_file = 'py3dic/__init__.py'
    with open(version_file, 'r') as file:
        for line in file:
            if line.startswith('__version__'):
                # Extract the version number
                version = line.split('=')[1].strip().strip('\'"')
                return version
    raise RuntimeError('Cannot find version information')

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = [
    'scipy',
    'numpy',
    'matplotlib',
    'seaborn',
    'pandas',
    'openpyxl',
    'ipykernel',
    'jupyter',
    'opencv-python'
 ]

test_requirements = [
    'pytest',
    # 'pytest-pep8',
    # 'pytest-cov',
]


setuptools.setup(
    name="py3dic",
    version=get_version(),
    author="N. Papadakis",# Replace with your own username
    author_email="npapnet@gmail.com",
    description="A package Digital Image Correlation (DIC) analysis in Python 3.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    tests_require=test_requirements,
    python_requires='>=3.10',
    project_urls={
        'Documentation': 'https://npapnet.github.io/py3dic/',
        'Source': 'https://github.com/npapnet/py3dic'
    },
    
)