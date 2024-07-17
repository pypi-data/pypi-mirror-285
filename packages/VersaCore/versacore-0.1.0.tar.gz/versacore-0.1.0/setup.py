from setuptools import setup, find_packages

setup(
    name='VersaCore',
    version='0.1.0',
    description='VersaCore Library',
    author='Jansen Tang',
    author_email='jansen.tang@ai-sherpa.io',
    url='https://github.com/AI-Sherpa/VersaCore',
    packages=find_packages(include=['versacore', 'versacore.*']),
    install_requires=[
        'requests>=2.25.1',
        'openai>=0.5.0',
        'Flask>=2.0.1',
        'beautifulsoup4>=4.9.3',
        'selenium>=4.1.0'
    ],
    tests_require=[
        'pytest>=6.2.4',
    ],
    entry_points={
        'console_scripts': [
            # Define your command-line scripts here
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
