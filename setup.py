from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name = "pg2mongo",
    version = "1.0",
    author = "Sathiya Sarathi",
    author_email = "sathyasarathi90@gmail.com",
    description = "A postgres to MongoDB Migration App.",
    license = "BSD",
    url = "https://github.com/datawrangl3r/pg2mongo",
    packages=['pg2mongo'],
    install_requires=[
	"asteval==0.9.8",
	"psycopg2==2.7.3.1",
	"pymongo==3.5.1",
	"PyYAML==3.12"],
    classifiers=[
        "License :: Apache License 2.0",
    ],
    include_package_data=True
)
