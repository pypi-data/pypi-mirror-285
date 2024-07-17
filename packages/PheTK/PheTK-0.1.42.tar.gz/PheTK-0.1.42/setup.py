from setuptools import setup, find_packages

# Read contents of the README.md file
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='PheTK',
    version='0.1.42',
    # version='0.2.1rc5',
    python_requires='>=3.7',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    package_data={
        '': ['*.*'],
        'PheTK': ['phecode/*'],
    },
    url='https://github.com/nhgritctran/PheTK',
    license='GPL-3.0',
    author='Tam Tran',
    author_email='PheTK@mail.nih.gov',
    description='The Phenotype Toolkit',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        "adjusttext",
        "connectorx",
        "google-cloud-bigquery",
        "hail",
        "lifelines",
        "lxml",
        "matplotlib",
        "numpy",
        "pandas",
        "polars<=0.20.26",
        "pyarrow",
        "statsmodels",
        "tqdm"
    ]
)
