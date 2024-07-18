from setuptools import find_namespace_packages, setup


def get_long_description() -> str:
    with open("README.md") as fh:
        return fh.read()


setup(
    name="metaflow-card-hf-dataset",
    version="0.0.4",
    description="A metaflow card that renders HTML inputs.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Outerbounds",
    author_email="hello@outerbounds.co",
    license="Apache Software License 2.0",
    packages=find_namespace_packages(include=["metaflow_extensions.*"]),
)
