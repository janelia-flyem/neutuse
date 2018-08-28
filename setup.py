from setuptools import setup, find_packages

setup(
    name = "neutuse",
    version = "0.1.1",
    packages = find_packages(exclude = ["*.pyc"] ),
    include_package_data = True,
    zip_safe = False,
    install_requires = ['Flask','Requests'],
    entry_points = {
    
        'console_scripts':['neutuse=neutuse:main']
    }
)
