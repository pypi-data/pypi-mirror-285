from setuptools import setup, find_packages

# Read the contents of your README file
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='IntelliMaint',
    version='0.12',
    author='IPTLP0032',
    author_email='iptgithub@intellipredikt.com',
    description='A prognostics package by IntelliPredikt Technologies',
    long_description=long_description, 
    long_description_content_type='text/markdown',  
    install_requires=[
        'scikit-learn', 'GPy', 'minisom', 'scipy', 'matplotlib', 'numpy>=1.16.1', 'mplcursors', 'fpdf2', 'tensorflow>=2.10,<2.12', 'keras>=2.10,<2.11', 'pandas>=1.0.0,<1.3.0', 'seaborn', 'imbalanced-learn',
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'IntelliMaint': [
            'grand/datasets/*',
            'grand/group_anomaly/*',
            'grand/individual_anomaly/*',
            'grand/*'
        ],
        'IntelliMaint.examples.data.battery_data': ['*'],
        'IntelliMaint.examples.data.bearing_data': ['*'],
        'IntelliMaint.examples.data.phm08_data.csv': ['*']
    },
    python_requires='>=3.5',   
)
