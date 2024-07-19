from setuptools import setup

from wilt import __version__


setup(
    name             = 'Wilt',
    version          = __version__,
    author           = 'saaj',
    author_email     = 'mail@saaj.me',
    packages         = ['wilt', 'wilt.ci', 'wilt.cq'],
    license          = 'GPL-3.0-or-later',
    description      = "Architect's collection of codebase health probes",
    long_description = open('README.rst', 'r').read(),
    keywords         = 'code-metrics code-quality continuous-integration',
    python_requires  = '>= 3.10',
    url              = 'https://heptapod.host/saajns/wilt',
    classifiers      = [
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Quality Assurance',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
    ],
    entry_points     = {'console_scripts': ['wilt = wilt.cli:main']},
    install_requires = [
        'pandas >= 2.2.2, < 3',
        'plotly >= 5.22.0, < 6',
        'requests >= 2.32.3, < 3',
        'tqdm >= 4.66.4, < 5',
    ],
)
