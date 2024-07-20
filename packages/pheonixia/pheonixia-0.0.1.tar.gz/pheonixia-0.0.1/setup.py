import pathlib
from setuptools import find_packages, setup

with open("requirements.txt", "r", encoding="utf-8") as f:
    required = f.read().splitlines()

setup(
    name="pheonixia",
    version="0.0.1",
    description="a repository for Phoenix-IA models",
    long_description=pathlib.Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    Homepage="https://github.com/not-lain/phoenixia",
    url="https://github.com/not-lain/phoenixia",
    Issues="https://github.com/not-lain/phoenixia/issues",
    authors=[{"name": "hafedh hichri", "email": "hhichri60@gmail.com"}],
    license="Apache 2.0 License",
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    classifiers=["Topic :: Utilities", "Programming Language :: Python :: 3.9"],
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=required,
)
