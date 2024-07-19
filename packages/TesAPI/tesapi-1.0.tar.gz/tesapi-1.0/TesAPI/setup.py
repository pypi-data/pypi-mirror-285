from setuptools import setup, find_packages

setup(
    name='TesAPI',
    version='1.0',
    author='Tes_Npe',
    author_email='antoshaspr@vk.com',
    description='Client For TesAPI',
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
    install_requires=[
        'requests'
    ]
)