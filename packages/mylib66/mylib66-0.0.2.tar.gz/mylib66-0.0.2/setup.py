import setuptools

VERSION = '0.0.2'
DESCRIPTION = 'Personal library'
with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    REQUIREMENTS = fh.read()

setuptools.setup(
        name="mylib66",
        version=VERSION,
        author="Chazz Yu",
        author_email="<cklibrary2@qq.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        packages=setuptools.find_packages(),
        install_requires=REQUIREMENTS,
        url="https://github.com/xziyu6/mylib66.git",
        keywords=['python', 'personal'],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)