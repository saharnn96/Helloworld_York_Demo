from setuptools import setup, find_packages

setup(
    name='lidarocclusion',
    version='0.0.1',
    description='a pip-installable package example',
    license='',
    packages=find_packages(include=["lidarocclusion", "lidarocclusion.*"]),
    author='Thomas Wright',
    author_email='thomas.wright@ece.au.dk',
    keywords=[],
    url='https://github.com/twright/Lidar-Occlusion'
)