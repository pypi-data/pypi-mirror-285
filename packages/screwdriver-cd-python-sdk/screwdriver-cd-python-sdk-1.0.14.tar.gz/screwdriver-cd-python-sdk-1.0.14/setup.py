from setuptools import find_packages, setup

setup(
    name="screwdriver-cd-python-sdk",
    version="1.0.14",
    description="Screwdriver CD Python Software Development Kit (SDK) for managing resources in Screwdriver",
    url="https://github.com/QubitPi/screwdriver-cd-python-sdk",
    author="Jiaqi liu",
    author_email="jack20220723@gmail.com",
    license="Apache-2.0",
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[

    ],
    zip_safe=False,
    include_package_data=True,
    setup_requires=["setuptools-pep8", "isort"]
)
