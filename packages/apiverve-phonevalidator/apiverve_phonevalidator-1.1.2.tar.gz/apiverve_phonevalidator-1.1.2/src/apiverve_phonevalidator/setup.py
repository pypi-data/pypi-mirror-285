from setuptools import setup, find_packages

setup(
    name='apiverve_phonevalidator',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools'
    ],
    description='Phone Number Validator is a simple tool for validating if a phone number is valid or not. It checks the phone number format and the country code to see if the phone number is valid.',
    author='APIVerve',
    author_email='hello@apiverve.com',
    url='https://apiverve.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
