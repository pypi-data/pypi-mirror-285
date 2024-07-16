from setuptools import setup, find_packages

setup(
        name="majordomo_ai",
        version="0.1.4",
        packages=find_packages(),
        install_requires=['Requests==2.32.3', 'SQLAlchemy==2.0.30', 'SQLAlchemy_Utils==0.41.2']
    )
