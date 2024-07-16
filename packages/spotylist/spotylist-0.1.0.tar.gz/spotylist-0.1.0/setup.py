from setuptools import setup, find_packages

setup(
    name='spotylist',
    version='0.1.0',
    py_modules=['spotylist'],
    install_requires=[
        'Click',
        'requests',
        'tabulate',
    ],
    entry_points={
        'console_scripts': [
            'spotylist=spotylist:cli',
        ],
    },
    author='Marin',
    author_email='your.email@example.com',
    description='Spotify in the Terminal CLI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/marinkres/spotylist',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
