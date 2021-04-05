from setuptools import setup

setup(
    name='park-nyc',
    version='0.0.1dev',
    description='Unofficial ParkNYC API Python wrapper',
    long_description=open('README.md').read(),
    keywords='api parking nyc',
    license='MIT',
    author="Alexander Afanasyev",
    author_email='me@alecxe.me',
    url='https://github.com/alecxe/park-nyc',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet :: WWW/HTTP',
    ],
    packages=[
        'parknyc',
    ],
    install_requires=[
        'requests'
    ],
)
