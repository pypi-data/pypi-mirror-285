from setuptools import setup, find_packages

setup(
    name='apiverve_partsofspeech',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools'
    ],
    description='Parts Of Speech is a simple tool for extracting nouns, verbs, adjectives, adverbs, etc. from text. It returns the extracted words based on the part of speech specified.',
    author='APIVerve',
    author_email='hello@apiverve.com',
    url='https://apiverve.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
