from setuptools import setup, find_packages

setup(
    name="TesRSA",
    version="1.0",
    author="Tes",
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
    install_requires=[
        "cryptography"
    ]
)