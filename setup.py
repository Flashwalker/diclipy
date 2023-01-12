from setuptools import setup, find_packages

setup(
    name='diclipy',
    version='0.1.6',
    packages=find_packages(),
    include_package_data=True,
    author='uzver',
    author_email='uzver@protonmail.ch',
    url='https://notabug.org/uzver/diclipy',
    license='GNU/GPLv3+',
    description='CLI script for posting/reading/commenting on Diaspora* pod written around Diaspy API',
    long_description = open('README.rst').read(),
    keywords='diaspora diaspy cli social blog federative network fediverse',
    install_requires=['diaspy-api','clap-api'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Utilities'
    ],
    entry_points = {
        'console_scripts': ['diclipy=diclipy.diclipy:main'],
    }
)
