from setuptools import setup, find_packages

setup(
    name='universal-test-platform',
    version='0.0.64',

    package_dir  = {'': 'src'},
    package_data = {'utp': ['*','**/*.jar']},
    include_package_data=True,
    packages     = find_packages('src'),
    install_requires=['Click', 'pyyaml', 'robotlibcore-temp', 'robotframework-appiumlibrary', 'robotframework-seleniumlibrary', 'requests', 'tqdm' ],
    entry_points={
        'console_scripts': [
            'utp = utp.utp:cli',
            'utpi = utp.utpi:internal_cli'
        ]
    }
)