from setuptools import setup, find_packages

setup(
    name='ogs-account-generator',
    version='1.0.0',
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
    author='Your Name',
    author_email='your.email@example.com',
    description='Automated account generator for Online-Go.com',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/changcheng967/ogs-account-generator',  # Link to your GitHub repository
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
