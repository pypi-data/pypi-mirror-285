import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="ErrorHook",
    version="2.2.3",
    author="cc1287",
    author_email="bilibili_cc1287@126.com",
    description="Hook your Error.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/cc1287/error-hook",
    packages=setuptools.find_packages(),
    package_data={'TrajCompress': ['ErrorHook/hash.file']},
    install_requires=['datetime'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
    ),
)