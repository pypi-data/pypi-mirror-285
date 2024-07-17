from setuptools import find_packages, setup


setup(
    name="time-limitation-module",
    version="1.0.0",
    author="leooyang",
    author_email="leooyang@futunn.com",
    description="time limitation module",
    python_requires="==3.7.5",
    packages=find_packages(exclude=["tests"]),
    install_requires=["pydantic==1.10.7", "cmlb_api_client==0.3.1"],
)
