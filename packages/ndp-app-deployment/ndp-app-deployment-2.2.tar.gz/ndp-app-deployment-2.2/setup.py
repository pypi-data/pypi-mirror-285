import setuptools
  
with open("README.md", "r") as fh:
    long_description = fh.read()
  
setuptools.setup(
    # Here is the module name.
    name="ndp-app-deployment",
  
    # version of the module
    version="2.2",
  
    # Name of Author
    author="Harshal Shah",

    #License
    license="Proprietary",
  
    # your Email address
    author_email="harshal.shah@zetaris.com",
  
    # #Small Description about module
    description="Version Control Mechanism for Zetaris Platform (https://www.zetaris.com/)",
  
    # long_description=long_description,
  
    # Specifying that we are using markdown file for description
    long_description=long_description,
    long_description_content_type="text/markdown",
  
    # Any link to reach this module, ***if*** you have any webpage or github profile
    url="https://github.com/zetaris/versioncontrol",
    packages=setuptools.find_packages(),
  
  
    # if module has dependecies i.e. if your package rely on other package at pypi.org
    # then you must add there, in order to download every requirement of package
  
    install_requires=["pandas","jaydebeapi","numpy","pycryptodomex","getpass4","pyyaml","sqlalchemy"],
  
    # classifiers like program is suitable for python3, just leave as it is.
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)