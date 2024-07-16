from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='chinese-pdnode',
    version='1.0.1',
    packages=find_packages(),
    install_requires=[
        'jieba',
    ],
    author='Bret',
    author_email='Bret@pdnode.com',
    description='A Python library for Chinese text processing',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bretren/chinese',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
