from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="amtm_signaldetect",
    version="0.0.1",
    description="Periodic Signal Detection via the Adaptive Multitaper Method (aMTM)",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/hsalinasGIT/amtm_signaldetect",
    author="Hector A Salinas",
    author_email="has4551@mavs.uta.edu",
    keywords="periodic signal detection",
    license="MIT",
    packages=["amtm_signaldetect"],
    install_requires=["multitaper", "scipy", "numpy", "matplotlib"],
    include_package_data=True,
)