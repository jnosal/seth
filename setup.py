from distutils.core import setup

requires = [
    'sqlalchemy>=0.9',
    'pyramid>=1.5',
    'zope.sqlalchemy',
]


setup(
    name = 'seth',
    packages = ['seth'],
    install_requires = requires,
    version = '0.1',
    description = 'Smart and practical set of utilities for Pyramid framework',
    author = 'jnosal',
    author_email = 'jacek.nosal@outlook.com',
    url = 'https://github.com/jnosal/seth',
    keywords = ['sqlalchemy', 'pyramid'],
    classifiers = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Framework :: Pyramid',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)