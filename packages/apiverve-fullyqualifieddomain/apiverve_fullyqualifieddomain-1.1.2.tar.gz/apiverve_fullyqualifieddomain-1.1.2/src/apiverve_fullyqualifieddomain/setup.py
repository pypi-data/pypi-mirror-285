from setuptools import setup, find_packages

setup(
    name='apiverve_fullyqualifieddomain',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools'
    ],
    description='Fully Qualified Domain Name is a simple tool for getting the fully qualified domain name (FQDN) of an IP. It returns the fully qualified domain name of the ip provided.',
    author='APIVerve',
    author_email='hello@apiverve.com',
    url='https://apiverve.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
