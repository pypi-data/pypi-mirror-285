from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='fastapi_security_middleware',
    author="kaiqui",
    author_email="kaiqui82@gmail.com",
    description="Simple security middleware for FastAPI",
    version="0.1.3",
    setup_requires=['setuptools_scm'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kaiqui/fastapi_security_middleware",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'fastapi',
        'starlette',
        'httpx',
        'pyyaml',
        'loguru'
    ],
    python_requires='>=3.9'
)
