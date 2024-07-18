from setuptools import setup, find_packages

setup(
    name="spider-cli",
    version="0.1.4",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'requests',
        'jmespath'
    ],
    entry_points={
        'console_scripts': [
            'spider=usl.cli:cli',
        ],
    },
    author='Andrew Polykandriotis',
    author_email='mail@minakilabs.com',
    description='SPIDER: Secure Proxy Infrastructure for Data Extraction and Retrieval',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/minakilabs-official/spider-cli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
