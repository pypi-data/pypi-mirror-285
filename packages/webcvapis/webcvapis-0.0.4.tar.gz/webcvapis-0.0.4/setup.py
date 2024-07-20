import setuptools

setuptools.setup(
    name = "webcvapis",
    version = "0.0.4",
    description = "WebCV APIs",
    long_description = open("README.md", "r", encoding="utf-8").read(),
    author = "qaqFei",
    author_email = "qaq_fei@163.com",
    url = "https://github.com/qaqFei/webcvapis",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows"
    ],
    install_requires = ["pywebview"],
    license = "MIT License",
    python_requires = ">=3.12.0"
)