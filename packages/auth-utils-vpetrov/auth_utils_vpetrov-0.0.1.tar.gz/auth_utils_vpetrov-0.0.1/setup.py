"""
Setup file for auth_utils package
"""
from setuptools import setup, find_packages

setup(
    name='auth_utils_vpetrov',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'pydantic',
        'user_utils',
        'typing'
    ]
)
