import pathlib
import setuptools

setuptools.setup(
    name="requence",
    version="0.1.4",
    description="Consumer implementation",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Torsten Blindert",
    python_requires=">=3.10",
    install_requires=["pika>=1.3.2", "semver>=3.0.2"],
    packages=setuptools.find_packages(),
    include_package_data=True,
)
