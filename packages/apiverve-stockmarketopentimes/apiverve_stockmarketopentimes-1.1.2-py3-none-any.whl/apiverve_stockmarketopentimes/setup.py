from setuptools import setup, find_packages

setup(
    name='apiverve_stockmarketopentimes',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools'
    ],
    description='Stock Market Open Times is a simple tool for getting the open times of the stock market. It returns the open times of the stock market for each day of the week.',
    author='APIVerve',
    author_email='hello@apiverve.com',
    url='https://apiverve.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
