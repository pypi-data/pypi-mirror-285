from setuptools import setup, find_packages

setup(
    name="gdreq",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    author="NumbersTada",
    author_email="tadaktatak61@gmail.com",
    description="Library for sending requests to the Geometry Dash servers.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
