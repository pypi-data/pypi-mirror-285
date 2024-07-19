from setuptools import setup, find_packages

setup(
    name='google-url-bulk-indexing',
    version='1.0.4',
    packages=find_packages(),
    install_requires=[
        'google-auth',
        'google-auth-oauthlib',
        'requests',
        'pandas',
        'openpyxl',
    ],
    entry_points={
        'console_scripts': [
            'google-bulk-url-indexing = indexing.main:main',
        ],
    },
    author='Around With Us',
    author_email='mscrabe@gmail.com',
    description='A package to submit Bulk URLs for Google Indexing using an Excel file',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
