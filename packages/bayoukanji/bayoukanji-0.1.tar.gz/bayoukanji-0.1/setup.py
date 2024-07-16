from setuptools import setup, find_packages

setup(
    name='bayoukanji',
    version='0.1',
    packages=find_packages(),
    description='Pacote config para projeto Bayou',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Douglas',
    author_email='douglas@meizter.com',
    url='https://github.com/DouglasBMart/bayoukanji.git', 
    install_requires=[
        'requests',
        'pandas',
        's3fs',
        'boto3',
        'pyarrow'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

