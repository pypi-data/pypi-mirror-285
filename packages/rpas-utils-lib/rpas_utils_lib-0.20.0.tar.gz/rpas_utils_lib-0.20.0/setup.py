from setuptools import setup,find_packages

setup(
    use_scm_version=True,
    name="rpas_utils_lib",
    version="0.20.0",
    py_modules=['rpas_utils_lib'],
    description="This library offers some utilities for Remotely Piloted Aircraft Systems (RPAS) services",
    author="Nuran Elsayed",
    author_email="nuran@esbaar.com",
    url="https://github.com/Nuran-A-Elsayed/rpas_utils_lib",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "geopy==2.3.0",
        "httpx==0.27.0",
        "lxml==4.9.2",
        "numpy==1.24.1",
        "opencv-python==4.8.0.74",
        "pydantic==1.10.4",
        "PyExifTool==0.5.5",
        "pykml==0.2.0",
        "requests==2.32.3",
        "setuptools==70.1.0",
        "Shapely==2.0.4",
        "utm==0.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
            "mypy",
        ]
    },
)
