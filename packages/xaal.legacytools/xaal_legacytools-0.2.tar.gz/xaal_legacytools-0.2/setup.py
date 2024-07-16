from setuptools import setup,find_packages

with open('README.rst') as f:
    long_description = f.read()

VERSION = "0.1"

setup(
    name='xaal.legacytools',
    version=VERSION,
    license='GPL License',
    author='Jerome Kerdreux',
    author_email='Jerome.Kerdreux@imt-atlantique.fr',
    #url='',
    description=('xAAL devices tools'),
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
          'xaal-isalive-legacy   = xaal.legacytools.isalive:main',
          'xaal-info-legacy      = xaal.legacytools.info:main',
          'xaal-dumper-legacy    = xaal.legacytools.dumper:main',
          'xaal-tail-legacy      = xaal.legacytools.tail:main',
          'xaal-walker-legacy    = xaal.legacytools.walker:main',
          'xaal-keygen-legacy    = xaal.legacytools.keygen:main',
          'xaal-log-legacy       = xaal.legacytools.log:main',
          'xaal-querydb-legacy   = xaal.legacytools.querydb:main',
          'xaal-pkgrun-legacy    = xaal.legacytools.pkgrun:main',
          'xaal-uuidgen-legacy   = xaal.legacytools.uuidgen:main',
          'xaal-inspector-legacy = xaal.legacytools.inspector:main',
      ],
    },
    
    install_requires=[
        'xaal.lib',
    ]
)
