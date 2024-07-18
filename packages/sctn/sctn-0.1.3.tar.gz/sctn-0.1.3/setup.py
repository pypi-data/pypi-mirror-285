from setuptools import setup, find_packages, glob

VERSION = "0.1.3"
DESCRIPTION = "Spiking Continues Time Neuron"
LONG_DESCRIPTION = "A Spiking Neural Network implementation using "


def parse_requirements(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        lines = [line.strip() for line in lines if line and not line.startswith("#")]
        return lines


requirements = parse_requirements("requirements.txt")

# Separate git dependencies from regular ones
install_requires = [req for req in requirements if not req.startswith("git+")]
dependency_links = [req for req in requirements if req.startswith("git+")]
# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="sctn",
    version=VERSION,
    author="Yakir Hadad",
    author_email="yakir4123@email.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=install_requires,
    keywords=["python", "snn", "ai"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
    ],
    dependency_links=dependency_links,
    data_files=glob.glob("sctn\\resonators_params\\parameters\\*.json"),
)
