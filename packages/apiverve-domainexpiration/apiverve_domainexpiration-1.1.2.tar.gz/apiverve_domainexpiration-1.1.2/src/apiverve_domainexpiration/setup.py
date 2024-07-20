from setuptools import setup, find_packages

setup(
    name='apiverve_domainexpiration',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools'
    ],
    description='Domain Expiration Checker is a simple tool for checking the expiration date and age of a domain. It returns the expiration date and age of the domain provided.',
    author='APIVerve',
    author_email='hello@apiverve.com',
    url='https://apiverve.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
