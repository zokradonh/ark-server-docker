from setuptools import setup

setup(
    name='omni-config-changer',
    version='0.1.0',
    description='Change all simple kinds of config files. For use in containers.',
    url='https://github.com/zokradonh/omni-config-changer',
    author='zokradonh',
    author_email='az@zok.xyz',
    license='MIT',
    packages=['occ'],
    install_requires=[],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.9',
    ],
)