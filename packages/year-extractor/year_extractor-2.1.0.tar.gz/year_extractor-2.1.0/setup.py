from setuptools import setup, find_packages

setup(
    name='year_extractor',
    version='2.1.0',
    author='Maneesha Jayathissa',
    author_email='manishamalshani@gmail.com',
    description='A library to extract dates from text and convert them to years.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'spacy>=3.0',
        'dateparser'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
