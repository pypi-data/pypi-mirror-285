from setuptools import setup, find_packages

setup(
    author= "Dear Norathee",
    author_email="noratee5@hotmail.com",
    description="Expansion of inspect to help analyze and automate python code",
    name="inspect_py",
    version="0.1.3rc1",
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "pandas",
        "py_string_tool>=0.1.4", 
        "python_wizard>=0.1.3", 
        "os_toolkit >= 0.1.2", ],
    url = "https://github.com/DearNorathee/inspect_py",
    
    # example
    # install_requires=['pandas>=1.0',
    # 'scipy==1.1',
    # 'matplotlib>=2.2.1,<3'],
    

)