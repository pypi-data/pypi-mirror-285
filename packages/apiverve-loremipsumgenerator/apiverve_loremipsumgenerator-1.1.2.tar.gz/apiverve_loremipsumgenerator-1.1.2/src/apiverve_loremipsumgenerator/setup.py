from setuptools import setup, find_packages

setup(
    name='apiverve_loremipsumgenerator',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools'
    ],
    description='Lorem Ipsum Generator is a simple tool for generating lorem ipsum text. It returns the generated text.',
    author='APIVerve',
    author_email='hello@apiverve.com',
    url='https://apiverve.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
