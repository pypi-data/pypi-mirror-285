from setuptools import setup, find_packages

authors = [
    "NgocAn <anlam9614@gmail.com>",
    "NguyenDuyKhang <nguyenduykhang29112k2@gmail.com>"
]

setup(
    name="FiinQuant",
    version="0.5",
    packages=find_packages(),
    description="A simple indicator library for stock tickers",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author=", ".join(authors),
    install_requires=['requests', 'pandas', 'numpy', 'signalrcore'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
