from setuptools import setup, find_packages

setup(
    name='apiverve_emaildisposablechecker',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools'
    ],
    description='Email Disposable Checker is a simple tool for checking if an email address is disposable. It returns if the email address is disposable or not.',
    author='APIVerve',
    author_email='hello@apiverve.com',
    url='https://apiverve.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
