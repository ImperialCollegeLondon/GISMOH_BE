from setuptools import setup, find_packages

requirements = ['tornado', 'pika']

setup(
    name = 'GISMOH',
    version = '2.0',
    packages = find_packages(),
    install_requires = requirements,
    test_suite = "tests.test_all.run",
    author = 'Chris Powell, Department of Infectious Disease Epidemiology, Imperial College London',
    author_email = 'c.powell@imperial.ac.uk',
    description = 'GISMOH',
    long_description = '''
       Generic Information System for the Managment of Outbreaks in Hospitals
    ''',
    license = 'Apache 2.0',
    url = 'http://www.wgst.net/',
    download_url = '',
    include_package_data = True,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache 2.0 License',
        'Operating System :: Windows',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points = '''
   '''
)
