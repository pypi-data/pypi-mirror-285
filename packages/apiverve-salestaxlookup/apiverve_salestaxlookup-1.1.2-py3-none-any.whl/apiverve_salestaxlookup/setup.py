from setuptools import setup, find_packages

setup(
    name='apiverve_salestaxlookup',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools'
    ],
    description='Sales Tax Lookup is a simple tool for looking up the sales tax rate of a location. It returns the sales tax rate.',
    author='APIVerve',
    author_email='hello@apiverve.com',
    url='https://apiverve.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
