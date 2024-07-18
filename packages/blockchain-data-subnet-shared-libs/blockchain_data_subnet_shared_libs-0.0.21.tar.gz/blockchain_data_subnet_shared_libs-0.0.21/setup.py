from setuptools import setup, find_packages

setup(
    name='blockchain-data-subnet-shared-libs',
    version='0.0.21',
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here
        'pydantic',
    ],
    author='Dmytro Savenkov',
    author_email='dmytro.savenkov@chain-insights.ai',
    description='All shared libs that all components, executables, and services of blockchain data subnet are based on',
    url='https://github.com/blockchain-insights/blockchain-data-subnet-shared-libs',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
