# this was in /home/santod/my_project

from setuptools import setup

version_number = input("Input the new version number you are going to use: ")

if not version_number:
    raise ValueError("Version number is required")

print(f"Using version: {version_number}")

setup(
    name='barbara_updater',
    version=version_number,
    author='santod',
    description='weather observer',
    py_modules=['barbara3']  # List of your Python files
)

