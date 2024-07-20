from setuptools import setup, find_packages

setup(
    name='shxd',
    version='0.1',
    packages=find_packages(include=['shxd', 'shxd.*']),
    entry_points={
        'console_scripts': [
            'sx=shxd.__main__:main',
        ],
    },
    install_requires=[
        'requests',
        'pygments',
        'colorama',
        
    ],
    python_requires='>=3.6',
    author='Pedro Luis Dias',
    author_email='luisp.diias@gmail.com',
    description='A CLI to extend shell functionality for developers.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/luiisp/shxd',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
