from setuptools import setup

with open("readme_pachage.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='cara_api',
    version='1.4',
    packages=["cara_api"],
    install_requires=["requests", "reds-simple-logger"],
    author="Red_Wolf2467",
    author_email="support@pyropixle.com",
    description="Allows you to interact with the Cara API.",
    long_description=long_description,  # Setze die lange Beschreibung
    long_description_content_type="text/markdown",
    python_requires='>=3.8'
)