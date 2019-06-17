from setuptools import find_packages, setup


version = open('Ctl/VERSION').read().strip()
requirements = open('Ctl/requirements.txt').read().split("\n")
test_requirements = open('Ctl/requirements-test.txt').read().split("\n")


setup(
    name='pymdgen',
    version=version,
    author='20C',
    author_email='code@20c.com',
    description='python code markdown documentation generator',
    long_description='',
    license='LICENSE.txt',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    url='https://github.com/20c/pymdgen',
    download_url='https://github.com/20c/pymdgen/%s' % version,

    install_requires=requirements,
    test_requires=test_requirements,

    entry_points={
        'console_scripts': [
            'pymdgen=pymdgen.cli:main',
        ],
        'markdown.extensions': [
            'pymdgen=pymdgen.md:Extension',
        ]
    },

    scripts=[
    ],

    zip_safe=True
)