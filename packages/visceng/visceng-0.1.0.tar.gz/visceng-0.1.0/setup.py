from setuptools import setup, find_packages

setup(
    name="visceng",
    version="0.1.0",
    author="N3rdL0rd",
    author_email="n3rdl0rd@proton.me",
    description="A fast 2D game engine for Python focused on normal-mapped lighting, optimized rendering, a simple API, and easy modding.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/N3rdL0rd/visceng",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyglet",
        "pdoc3",
        "black",
        "pyinstaller",
        "setuptools",
        "wheel",
        "twine",
    ],
)
