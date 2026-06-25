import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    

__version__ = "0.0.0"

REPO_NAME = "Kidney-Disease-Classification"
AUTHOR_USER_NAME = "ChristinaGoo"
SRC_REPO = "cnnClassifier"
AUTHOR_EMAIL = ""


setuptools.setup(
    name=SRC_REPO,
    version=__version__,
    author = AUTHOR_USER_NAME,
    description = "A small package for CNN Classifier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues"
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src")
)