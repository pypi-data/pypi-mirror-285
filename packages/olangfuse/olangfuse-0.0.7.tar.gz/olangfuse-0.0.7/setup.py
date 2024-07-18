from setuptools import setup, find_packages

from olangfuse import get_version

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="olangfuse",
    version=get_version(),
    packages=find_packages(
        include=['olangfuse', 'olangfuse.*']
    ),
    url="",
    license="MIT",
    install_requires=requirements,
    package_dir={'olangfuse': 'olangfuse'},
    author="Trinh Do Duy Hung",
    author_email="trinhhungsss492@gmail.com",
    description="A wrapper for Langfuse to manage Trace with full CRUD operations.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
