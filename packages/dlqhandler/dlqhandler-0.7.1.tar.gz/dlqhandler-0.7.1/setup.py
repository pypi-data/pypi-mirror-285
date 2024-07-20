from setuptools import setup, find_packages

setup(
    name='dlqhandler',
    version="0.7.1",
    packages=['dlqhandler', 'dlqhandler.services', 'dlqhandler.dataprovider'],
    install_requires=[
        'boto3',
        'mock'
    ],
    author="Marcelo Ferreira",
    author_email="jaytilangus@gmail.com",
    description="A library for handling DLQ messages in AWS SQS",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/seuusuario/dlq_handler_lib",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)