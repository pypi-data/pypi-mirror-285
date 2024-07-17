from setuptools import setup, find_packages

setup(
    name='dj-fast',
    version='0.1.3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'django',
        'inquirer',
        'pytz',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'dj-fast=djfast.cli:cli',
        ],
    },
    author='Sander Hegeman',
    author_email='me@heysander.com',
    description='A fast and easy Django project setup tool.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/dj-fast',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
