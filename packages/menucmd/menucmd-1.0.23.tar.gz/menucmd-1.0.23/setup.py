from setuptools import setup, find_packages


setup(
    name="menucmd",
    version="1.0.23",
    packages=find_packages(),
    include_package_data=True,
    author="Casey Litmer",
    #package_dir={"":"src"}, #check for real dir
    author_email="litmerc@msn.com",
    description="Command line menu interface",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Casey-Litmer/menucmd",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        # List your dependencies here
    ],
    python_requires='>=3.6',
)
