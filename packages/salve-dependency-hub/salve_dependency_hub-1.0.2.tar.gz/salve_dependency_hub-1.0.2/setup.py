# pip install -r requirements.txt --break-system-packages; pip uninstall salve_dependency_hub -y --break-system-packages; pip install . --break-system-packages --no-build-isolation; python3 -m pytest .
from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()


setup(
    name="salve_dependency_hub",
    version="1.0.2",
    description="Provides Tree Sitter highlighting languages in one centralized place for usage with Salve IPC",
    author="Moosems",
    author_email="moosems.j@gmail.com",
    url="https://github.com/Moosems/salve",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=open("requirements.txt", "r+")
    .read()
    .splitlines(keepends=False),
    python_requires=">=3.11",  # In accordance with
    license="MIT license",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: Implementation",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Typing :: Typed",
    ],
    packages=["salve_dependency_hub", "salve_dependency_hub.languages"],
)
