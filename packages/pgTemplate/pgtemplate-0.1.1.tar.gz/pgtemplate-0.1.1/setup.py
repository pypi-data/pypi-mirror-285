from setuptools import setup, find_packages

setup(
    name="pgTemplate",
    version="0.1.1",
    author="Promiteus",
    author_email="sbdt.israel@gmail.com",
    description="",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my_package",
    # packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
    install_requires=[
        'psycopg2'
    ]
)