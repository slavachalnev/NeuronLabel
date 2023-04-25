from setuptools import setup, find_packages

setup(
    name='neuronlabel',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'datasets',
        'numpy',
        'torch',
        'tqdm',
        'transformer_lens',
    ],
    # Include data files, like index.html and app src directory
    package_data={
        'neuronlabel': ['index.html', 'app/*'],
    },
)
