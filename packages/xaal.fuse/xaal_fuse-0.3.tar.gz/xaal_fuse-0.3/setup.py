from setuptools import setup,find_packages

with open('README.rst') as f:
    long_description = f.read()

VERSION = "0.1"

setup(
    name='xaal.fuse',
    version=VERSION,
    license='GPL License',
    author='Jerome Kerdreux',
    author_email='Jerome.Kerdreux@imt-atlantique.fr',
    #url='',
    description=('xAAL Fuse filesystem'),
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['xaal', 'tools'],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,

  entry_points = {
      'console_scripts': [
          'xaal-mount = xaal.fuse.mount:main',
      ],
    },
    
    install_requires=[
        'xaal.lib',
        'fuse-python',
        'rapidjson'
    ]
)
