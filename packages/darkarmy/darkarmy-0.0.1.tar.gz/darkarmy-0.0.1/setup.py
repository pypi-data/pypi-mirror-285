import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="darkarmy",
    version="0.0.1",
    author="Baihan Lin",
    author_email="doerlbh@gmail.com",
    description="Python library for adversarial attack simulation and defense",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/doerlbh/darkarmy",
    project_urls={
        "Bug Tracker": "https://github.com/doerlbh/darkarmy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    license="GPLv3",
    package_dir={"": "darkarmy"},
    packages=setuptools.find_packages(where="darkarmy"),
    python_requires=">=3.6",
    install_requires=["numpy>=1.16.5", "pandas"],
    test_suite="nose.collector",
    tests_require=["nose"],
    include_package_data=True,
)
