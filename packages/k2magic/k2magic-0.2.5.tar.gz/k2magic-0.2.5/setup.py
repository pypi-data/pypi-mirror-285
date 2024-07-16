import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
requirements = []

with open(os.path.join(here, 'QUICKSTART.md'), encoding='utf-8') as f:
    readme = f.read()

with open(os.path.join(here, os.path.join(here, 'requirements.txt')), encoding='utf-8') as f:
    for line in f.readlines():
        requirements.append(line.replace('\n', ''))

setup(
    name='k2magic',
    version='0.2.5',
    author='K2data',
    author_email='admin@k2data.com.cn',
    description='K2data内部的数据分析工具包',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://www.k2data.com.cn',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    license='MIT License',
)