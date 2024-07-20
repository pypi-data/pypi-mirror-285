#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:et:ai:sts=4

from distutils.core import setup

setup(
    name='nemu3',
    version='0.4',
    description='A lightweight network emulator embedded in a small '
                'python library.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Networking',
    ],
    author='Martina Ferrari, Alina Quereilhac, Tom Niget',
    author_email='tina@tina.pm, aquereilhac@gmail.com, tom.niget@nexedi.com',
    url='https://lab.nexedi.com/nexedi/nemu3',
    license='GPLv2',
    platforms='Linux',
    packages=['nemu'],
    install_requires=['unshare', 'six', 'attrs'],
    package_dir={'': 'src'},
    python_requires='>=3.11',
)
