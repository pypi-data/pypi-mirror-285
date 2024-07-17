from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

with open("LICENSE", encoding="utf-8") as f:
    license = f.read()

reqs = ""
try:
    with open("requirements.txt", encoding="utf-8") as f:
        reqs = f.read()
except:
    print("fuck")

pkgs = [p for p in find_packages() if p.startswith("xingyun")]

setup(
    name="xingyun",
    version="0.0.8-post11",
    url="http://github.com/FFTYYY/XingYun",
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="MIT",
    author = "Yongyi Yang",
	author_email = "yongyi@umich.edu",
    python_requires = ">=3.10",
    packages = pkgs,
    install_requires = reqs.strip().split("\n"),

    include_package_data = True , 
)