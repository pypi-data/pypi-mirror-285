from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description_readme = f.read()

with open("version.txt", "r") as version_file:
    version = version_file.read().strip()

setup(
    name="py_output_compare",
    version=version,
    description="a script that help compare output of 2 python script, I apply this to help grading student code compare to teacher",
    long_description=description_readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    author="meangpu",
    license="MIT",
    url="https://github.com/meangpu/py_output_compare",
    entry_points={"console_scripts": ["mep = py_output_compare.hello:print_hello"]},
)
