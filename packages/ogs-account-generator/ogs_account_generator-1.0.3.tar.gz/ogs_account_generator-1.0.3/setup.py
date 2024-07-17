from setuptools import setup, find_packages

setup(
    name='ogs-account-generator',
    version='1.0.3',
    packages=find_packages(),
    install_requires=[
        'selenium',
        # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'ogs-account-generator = ogs_account_generator.main:main',  # Replace with your entry point
        ],
    },
    author='changcheng967',
    author_email='changcheng6541@gmail.com',
    description='Automated account generator for Online-Go.com',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/changcheng967/Online-Go.com-Account-Generator',  # Link to your GitHub repository
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
