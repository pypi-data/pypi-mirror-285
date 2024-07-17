from setuptools import setup, find_packages

setup(
    name='btdr-ai-sdk',
    version='0.0.1',
    description='A Python SDK for Btdr AI platform.',
    author='Luka',
    author_email='luka@bitdeer.com',
    packages=find_packages("src"),  # Automatically find and include all packages
    package_dir={"": "src"},
    install_requires=[
        'grpcio==1.64.1',
        'protobuf==5.27.2',
        'pydantic==2.8.1',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)