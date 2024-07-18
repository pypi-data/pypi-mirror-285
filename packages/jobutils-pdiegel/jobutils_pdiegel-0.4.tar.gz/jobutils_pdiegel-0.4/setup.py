from setuptools import setup, find_packages  # type: ignore

setup(
    name="jobutils_pdiegel",
    version="0.4",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["python-dotenv"],
)
