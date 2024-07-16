from setuptools import setup, find_packages

version = "0.7.4.0"

with open("requirements.txt") as f:
    required_packages = f.read().splitlines()


EXTRAS_REQUIRE = {
    "dependency-injector": ["dependency-injector"],
}

setup(
    name="alphaz-next",
    version=version,
    packages=find_packages(),
    install_requires=required_packages,
    extras_require=EXTRAS_REQUIRE,
    license="MIT",
    author="Maxime MARTIN",
    author_email="maxime.martin02@hotmail.fr",
    description="A project to make a lib to start FASTAPI quickly",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/STDef200mm/alphaz-next",
    download_url="https://github.com/STDef200mm/alphaz-next/archive/refs/tags/%s.tar.gz"
    % version,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    package_data={"alphaz_next": ["py.typed"]},
    include_package_data=True,
)
