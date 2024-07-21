from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()
setup(
    name="stack_gen",
    version="0.0.17",
    author="Devoteam digital lab",
    author_email="valdo.negou.tawembe@devoteamgcloud.com",
    license="MIT",
    description="A CLI tool to generate code base from any cookiecutter template",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    # py_modules=["my_tool", "app"],
    packages=find_packages(),
    install_requires=[requirements],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points="""
        [console_scripts]
        sg=stack_gen.main:main
    """,
)
