from setuptools import setup, find_packages

requirements = []
with open("requirements.txt", "r") as fh:
    for line in fh:
        requirements.append(line.strip())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ironflock",
    version="1.0.0",
    description="Publishing data to a IronFlock Fleet Storage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RecordEvolution/ironflock-python",
    author="Record Evolution GmbH",
    author_email="marko.petzold@record-evolution.de",
    packages=find_packages(),
    license="MIT",
    python_requires=">=3.6",
    install_requires=requirements,
    classifiers=[],
)
