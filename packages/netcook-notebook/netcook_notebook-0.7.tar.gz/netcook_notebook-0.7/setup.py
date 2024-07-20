from setuptools import setup, find_packages

setup(
    name='netcook_notebook',
    version='0.7',
    packages=find_packages(),
    install_requires=[
        'requests',
        'tabulate',
        'beautifulsoup4',
        'googletrans==4.0.0-rc1',
        'pyunpack',
        'rarfile',
        'IPython',
        'pandas',

    ],
    entry_points={
        'console_scripts': [
            'netcook_notebook=netcook_notebook.netcook:checked_cookies',
        ],
    },
    author='M. DICKY ALFANSYAH',
    author_email='hupbyu36@gmail.com',
    description='A package to check Netflix cookies status.',
    long_description='A package to check Netflix cookies status.',
    long_description_content_type='text/plain',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
