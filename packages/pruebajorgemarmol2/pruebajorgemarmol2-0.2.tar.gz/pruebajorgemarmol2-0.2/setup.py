from setuptools import setup, find_packages

setup(
    name="pruebajorgemarmol2",
    version="0.2",
    packages=find_packages(),
    install_requires=["azure-identity","azure-mgmt-resource"],  # Agrega las dependencias si las tienes
)


# python setup.py sdist
