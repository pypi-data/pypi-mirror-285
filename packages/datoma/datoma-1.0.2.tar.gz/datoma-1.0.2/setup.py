from setuptools import setup, find_packages


setup(
    name='Datoma',
    version='1.0.2',
    license='MIT',
    author="Datoma",
    author_email='releases@datoma.cloud',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://datoma.readthedocs.io/en/latest/index.html#',
    keywords='Datoma, Metabolomics, Science, Data, Analysis',
    install_requires=[
          'requests',
            'boto3',
            'requests-aws4auth',
            'gql',
            'awscrt',
            'botocore',
            'pyyaml',
            'websockets',
            'requests_toolbelt',
            'pycognito',
            'pwinput',
            'jsonpickle',
      ],
)