from distutils.core import  setup
import setuptools
packages = ['jhspypackage']# 唯一的包名，自己取名
setup(name='jhspypackage',
	version='1.0',
	author='jianghu',
    packages=packages, 
    package_dir={'requests': 'requests'},)

