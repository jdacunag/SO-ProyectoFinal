from setuptools import setup, find_packages

setup(
    name="secure-backup",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "dask>=2023.5.0",
        "distributed>=2023.5.0",
        "cryptography>=37.0.0",
        "tqdm>=4.64.0", 
        "python-dotenv>=0.20.0",
        "argparse>=1.4.0",
    ],
    entry_points={
        'console_scripts': [
            'secure-backup=src.main:main',
        ],
    },
    author=".",
    author_email="tu@email.com",
    description="Sistema de Backup Seguro con algoritmos de compresión clásicos y paralelismo",
    keywords="backup, compresión, encriptación, paralelismo, dask",
    python_requires=">=3.13",
)