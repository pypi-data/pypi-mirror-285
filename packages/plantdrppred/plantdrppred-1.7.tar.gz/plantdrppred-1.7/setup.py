from setuptools import setup, find_packages
from setuptools import  find_namespace_packages
# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='plantdrppred',
    version='1.7',
    description='A tool to predict Plant Diesease Resistance Protein',
    author='Gajendra P.S. Raghava',
    author_email='raghava@iiitd.ac.in',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license_files = ('LICENSE',),
    url='https://github.com/raghavagps/plantdrppred', 
    packages=find_namespace_packages(where="src"),
    package_dir={'':'src'},
    package_data={'plantdrppred.blast_binaries':['**/*'], 
    'plantdrppred.blastdb':['*'],
    'plantdrppred.model':['*'],
    'plantdrppred.possum':['*']},
    entry_points={ 'console_scripts' : ['plantdrppred = plantdrppred.python_scripts.plantdrppred:main']},
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        'numpy', 'pandas', 'scikit-learn>=1.3.0,<=1.3.2', 'argparse', 'biopython', 'requests'  # Add any Python dependencies here
    ]
)
