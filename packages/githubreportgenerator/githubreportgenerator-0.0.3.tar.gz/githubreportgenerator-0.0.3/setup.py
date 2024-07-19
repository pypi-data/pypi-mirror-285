from setuptools import setup, find_packages

VERSION = '0.0.3'
DESCRIPTION = 'A Dotnet Github Markdown Coverage Report Generator'
LONG_DESCRIPTION = 'Create a Github Markdown Coverage Report using a JSON Summary from reportgenerator'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="githubreportgenerator",
        version=VERSION,
        author="Joshua Cade Barber",
        author_email="foundernq@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that
        # needs to be installed along with your package. Eg: 'caer'
        entry_points={
        'console_scripts': [
            'githubreportgenerator=githubreportgenerator.main:main',
            ],
        },

        keywords=['test coverage', 'dotnet report', 'cobertura', 'xplat', 'code coverage', 'github', 'github markdown'],
        classifiers= [
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: OS Independent",
            "Operating System :: POSIX"
        ]
)
