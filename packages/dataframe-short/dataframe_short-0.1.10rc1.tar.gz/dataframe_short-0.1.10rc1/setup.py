from setuptools import setup, find_packages

setup(
    author= "Dear Norathee",
    author_email="noratee5@hotmail.com",
    description="package build on top of pandas and add more convient functionality. Make your code short and easy to read",
    name="dataframe_short",
    version="0.1.10rc1",
    packages=find_packages(),
    license="MIT",
    url = "https://github.com/DearNorathee/dataframe_short",
    install_requires=["pandas",
                      "os_toolkit >= 0.1.2",
                      "py_string_tool >= 0.1.4",
                      "datatable",
                      "polars",
                      "python_wizard >= 0.1.3",
                      "pyxlsb",
                      "inspect_py>=0.1.2"
                      ],
    
 
)