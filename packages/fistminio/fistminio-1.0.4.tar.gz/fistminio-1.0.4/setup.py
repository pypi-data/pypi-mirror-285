import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fistminio",
    description="FIST MinIO Client SDK for Python",
    author="ccyy",
    author_email="1805878415@qq.com",
    version="1.0.4",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # package_dir={"fistminio": "fistminio"},
    packages=setuptools.find_packages(),
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    
    install_requires=[
        'minio==7.2.3',
        'pyyaml',
        'cryptography',
        'tqdm',
    ],
    python_requires=">=3.7",
)