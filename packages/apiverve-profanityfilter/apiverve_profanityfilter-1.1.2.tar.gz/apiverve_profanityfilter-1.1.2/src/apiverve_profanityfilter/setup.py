from setuptools import setup, find_packages

setup(
    name='apiverve_profanityfilter',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'setuptools'
    ],
    description='Profanity Filter is a simple tool for filtering out profanity words from a text. It returns the text with the profanity words replaced by placeholders.',
    author='APIVerve',
    author_email='hello@apiverve.com',
    url='https://apiverve.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
