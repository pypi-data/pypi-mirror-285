from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='myfilesize',
    version='1.0.0',
    packages=find_packages(),
    description='A package to find small and large files in a directory',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='MrFidal',
    author_email='mrfidal@proton.me',
    url='https://github.com/Bytebreach/myfilesize',  
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
