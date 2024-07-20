from setuptools import setup, find_packages

setup(
    name='apiverve_gravatarlookup',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools'
    ],
    description='Gravatar Lookup is a simple tool for looking up Gravatar profiles. It returns the Gravatar profile information of the email address provided.',
    author='APIVerve',
    author_email='hello@apiverve.com',
    url='https://apiverve.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
