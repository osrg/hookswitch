from distutils.core import setup
setup(
    name='hookswitch',
    packages=['hookswitch', 'hookswitch.cli', 'hookswitch.internal'],
    version='0.0.1',
    description='A usermode packet injection library',
    author='Akihiro Suda',
    author_email='suda.akihiro@lab.ntt.co.jp',
    url='https://github.com/osrg/hookswitch',
    download_url='https://github.com/osrg/hookswitch/tarball/v0.0.1',
    license='Apache License 2.0',
    scripts=[
        'bin/hookswitch-nfq',
        'bin/hookswitch-of13',
        'bin/hookswitch-example-controller',
    ],
    install_requires=[
        'hexdump',
        'python-prctl',  # FIXME: prctl is only available for Linux
        'pyzmq',
        'ryu',  # ryu automatically installs: abc, eventlet, six, ..
    ],
    keywords=['fault', 'injection', 'testing',
              'openvswitch', 'netfilter', 'ryu'],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Networking'
    ],
)
