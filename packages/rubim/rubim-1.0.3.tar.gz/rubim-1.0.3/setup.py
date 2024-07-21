from setuptools import setup

setup(
    name = 'rubim',
    version = '1.0.3',
    author = 'MMDreza',
    author_email = 'vedaetext@gmail.com',
    description = 'Rubino API',
    license = "MIT",
    long_description = open('README.rst').read(),
    python_requires = "~=3.7",
    long_description_content_type = 'text/x-rst',
    url = 'https://rubika.ir/rubim_py',
    packages = ['rubim'],
    install_requires = ["requests"],

    keywords = [
        "Rubim_library",
        "Rubim",
        "Rubika",
        "Rubino",
        "rubim",
        "RUBIM",
        "rubika",
        "rubino"
    ],

    classifiers = [
    	"Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ]
)