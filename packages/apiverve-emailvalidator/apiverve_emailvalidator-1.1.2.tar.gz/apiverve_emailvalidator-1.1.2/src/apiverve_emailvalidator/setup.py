from setuptools import setup, find_packages

setup(
    name='apiverve_emailvalidator',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools'
    ],
    description='Email Validator is a simple tool for validating if an email address is valid or not. It checks the email address format and the domain records to see if the email address is valid.',
    author='APIVerve',
    author_email='hello@apiverve.com',
    url='https://apiverve.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
