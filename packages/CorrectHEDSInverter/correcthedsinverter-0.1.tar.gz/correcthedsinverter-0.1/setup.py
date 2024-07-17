from setuptools import setup, find_packages

setup(
    name='CorrectHEDSInverter',              # Replace with your package name
    version='0.1',                  # Replace with your package version
    packages=find_packages(),
    install_requires=[
        'matplotlib',
        'numpy',
        'scipy',
        'n2v',
    ],
    python_requires='>=3.12',        # Specify the Python version required
    author='Anthony Osborne, Vincent Martinetto',
    author_email='aosborne3@ucmerced.edu',
    description='Contains non published functions related to the High energy density inversion for the Pribram-Jones Group',
    long_description='Long description of your package',
    long_description_content_type='text/markdown',
    url='https://github.com/Anthony904175/HEDS_Inverter',  # URL to your package repository
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
)
