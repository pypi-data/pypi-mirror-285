from setuptools import setup, find_packages

setup(
    name="fabricScalability",
    version="0.1",
    packages=find_packages(),
    install_requires=["azure-identity","azure-mgmt-resource"],  # Agrega las dependencias si las tienes
)


# python setup.py sdist
