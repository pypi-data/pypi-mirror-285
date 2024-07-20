from setuptools import setup, find_packages

setup(
    name='laserlib',
    version='0.1',
    packages=find_packages(),
    license='MIT',
    description='A library for communication with laser model produced by Micro photons(Shanghai)Technology Co., Ltd.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Jacky Zhang',
    author_email='jackyzhang26@outlook.com',
    url='https://github.com/JackyZhang26/laserlib',
    install_requires=[
        'pyserial',
    ],
)