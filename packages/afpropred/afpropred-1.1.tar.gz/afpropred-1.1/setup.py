from setuptools import setup, find_packages
from setuptools import  find_namespace_packages
# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='afpropred',
    version='1.1',
    description='A tool to predict anti-freezing proteins',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license_files = ('LICENSE',),
    url='https://github.com/raghavagps/afpropred', 
    packages=find_namespace_packages(where="src"),
    package_dir={'':'src'},
    package_data={'afpropred.blast_binaries':['**/*'], 
    'afpropred.blast_db':['*'],
    'afpropred.model':['*']},
    entry_points={ 'console_scripts' : ['afpropred = afpropred.python_scripts.afpropred:main']},
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        'numpy', 'pandas', 'scikit-learn>=1.3.0', 'argparse', 'biopython', 'requests'  # Add any Python dependencies here
    ]
)
