from setuptools import find_packages, setup


setup(
    name="time-limitation-module",
    version="2.0.1",
    author="leooyang",
    author_email="leooyang@futunn.com",
    description="time limitation module",
    python_requires="==3.7.5",
    packages=find_packages(exclude=["tests"]),
    install_requires=open("requirements.txt").readlines(),
)
