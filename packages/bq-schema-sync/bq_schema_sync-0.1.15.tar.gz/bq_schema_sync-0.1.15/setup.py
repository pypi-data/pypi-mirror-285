from setuptools import setup, find_packages

try:
    from semantic_release.version import get_version
    version = get_version()
except ImportError:
    version = '0.1.15'

setup(
    name='bq-schema-sync',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'google-cloud-bigquery>=2.0.0',
        'google-api-core>=1.22.0',
        'pyyaml>=5.0',
    ],
    entry_points={
        'console_scripts': [
            'bq-schema-sync=bq_schema_sync.cli:main',
        ],
    },
    description='A tool to synchronize BigQuery table schemas with local definitions',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Victor Hasim Elexpe Ahamri',
    url='https://github.com/victorelexpe/bq-schema-sync',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Database',
    ],
    python_requires='>=3.8',
    keywords='bigquery schema sync gcp google-cloud',
    project_urls={
        'Documentation': 'https://github.com/victorelexpe/bq-schema-sync#readme',
        'Source': 'https://github.com/victorelexpe/bq-schema-sync',
        'Tracker': 'https://github.com/victorelexpe/bq-schema-sync/issues',
    },
    license='MIT',
    test_suite='tests',
    tests_require=[
        'unittest',
    ],
    extras_require={
        'dev': [
            'check-manifest',
            'flake8',
            'pytest',
            'black',
            'mypy',
        ],
        'lint': [
            'flake8',
        ],
        'test': [
            'pytest',
        ],
        'type': [
            'mypy',
        ],
        'docs': [
            'Sphinx',
            'sphinx_rtd_theme',
        ],
    },
    package_data={
        'bq_schema_sync': ['schemas/*.yaml', 'schemas/*.json'],
    },
    data_files=[
        ('schemas', ['schemas/example_schema.yaml']),
    ],
)
