import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="videosdk",
    version="0.0.5",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="videosdk",
    author_email="sdk@videosdk.live",
    license="MIT",
    packages=setuptools.find_packages(exclude=["example"]),
)
