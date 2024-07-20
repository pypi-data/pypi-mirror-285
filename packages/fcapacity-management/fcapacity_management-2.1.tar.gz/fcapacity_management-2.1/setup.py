from setuptools import setup, find_packages

setup(
    name="fcapacity_management",
    version="2.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["azure-identity","azure-mgmt-resource"],  # Agrega las dependencias si las tienes
)


# python setup.py sdist
