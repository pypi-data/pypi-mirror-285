from setuptools import setup, find_packages

setup(
    name='bdbotstest',
    version='1.0.1',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'bdbotstest=bdbotstest:welcome',
        ],
    },
    author='BDBOTSTEST',
    author_email='bdbotstest@admin.com',
    description='A bdbots test module',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nafismuhtadi929/bdbotstest',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)