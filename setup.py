import os
import os.path

from setuptools import setup, find_packages
import versioneer

# Default description in markdown
LONG_DESCRIPTION = open('README.md').read()

PKG_NAME     = 'tessdb-alarm'
AUTHOR       = 'Rafael Gonzalez'
AUTHOR_EMAIL = 'rafael08@ucm.es'
DESCRIPTION  = 'TESS-W database alarm tool',
LICENSE      = 'MIT'
KEYWORDS     = ['Light Pollution','Astronomy']
URL          = 'https://github.com/STARS4ALL/tessdb-alarm'
DEPENDENCIES = [
    "python-decouple"
]

CLASSIFIERS  = [
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.8',
    'Topic :: Scientific/Engineering :: Astronomy',
    'Topic :: Scientific/Engineering :: Atmospheric Science',
    'Framework :: Twisted',
    'Natural Language :: English',
    'Development Status :: 4 - Beta',
]


PACKAGE_DATA = {
    'dbalarm': [
        'sql/*.sql',
        'sql/initial/*.sql',
        'sql/updates/*.sql',
    ],
}

SCRIPTS = [
    "scripts/dbalarm",
]

DATA_FILES  = []

setup(
    name             = PKG_NAME,
    version          = versioneer.get_version(),
    cmdclass         = versioneer.get_cmdclass(),
    author           = AUTHOR,
    author_email     = AUTHOR_EMAIL,
    description      = DESCRIPTION,
    long_description_content_type = "text/markdown",
    long_description = LONG_DESCRIPTION,
    license          = LICENSE,
    keywords         = KEYWORDS,
    url              = URL,
    classifiers      = CLASSIFIERS,
    packages         = find_packages("src"),
    package_dir      = {"": "src"},
    install_requires = DEPENDENCIES,
    scripts          = SCRIPTS,
    package_data     = PACKAGE_DATA,
    data_files       = DATA_FILES,
)
