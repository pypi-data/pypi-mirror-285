from setuptools import setup, find_packages

setup(
    name="fcapacity_management",
    version="2.4",
    packages=find_packages(),
    install_requires=["azure-identity","azure-mgmt-resource"],  # Agrega las dependencias si las tienes
)


# python setup.py sdist
