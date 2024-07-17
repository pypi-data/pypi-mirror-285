from setuptools import setup, find_packages

setup(
    name="kurumii",
    version="1.4.8.6.4",
    packages=find_packages(),
    install_requires=[
        "pytube",
        "moviepy",
        "requests"
        ],
    author="Kurumii",
    description="A handy litle tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown"
)