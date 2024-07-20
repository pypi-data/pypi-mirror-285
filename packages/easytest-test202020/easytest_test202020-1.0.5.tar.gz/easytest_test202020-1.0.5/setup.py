import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easytest_test202020",
    version="1.0.5",
    author="ZZL",
    url='http://easytest_test202020.com',
    author_email="xxx@qq.com",
    description="xxx",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)