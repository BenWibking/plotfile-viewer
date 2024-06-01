import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

# Get the long description
with open('./README.md') as f:
    long_description = f.read()
# Get the package requirements from the requirements.txt file
with open('./requirements.txt') as f:
    install_requires = [line.strip('\n') for line in f.readlines()]

# Read the version number, by executing the file plotfile_viewer/__version__.py
# This defines the variable __version__
with open('./plotfile_viewer/__version__.py') as f:
    exec( f.read() )

# Define a custom class to run the py.test with `python setup.py test`
class PyTest(TestCommand):

    def run_tests(self):
        import pytest
        errcode = pytest.main([])
        sys.exit(errcode)

# Main setup command
setup(name='plotfile-viewer',
      version=__version__,
      description='Visualization tools for AMReX files',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/BenWibking/plotfile-viewer.git',
      maintainer='Ben Wibking',
      maintainer_email='ben@wibking.com',
      license='BSD-3-Clause',
      packages=find_packages('.'),
      package_data={'plotfile_viewer': ['notebook_starter/*.ipynb']},
      scripts=['plotfile_viewer/notebook_starter/plotfile_notebook'],
      tests_require=['pytest', 'jupyter'],
      install_requires=install_requires,
      extras_require = {
        'all': ["ipympl", "ipywidgets", "matplotlib", "numba", "pyamrex", "wget"],
        'GUI':  ["ipywidgets", "ipympl", "matplotlib"],
        'plot': ["matplotlib"],
        'tutorials': ["ipywidgets", "ipympl", "matplotlib", "wget"],
        'numba': ["numba"],
        'pyamrex': ["pyamrex"]
        },
      cmdclass={'test': PyTest},
      platforms='any',
      python_requires='>=3.8',
      classifiers=[
          'Programming Language :: Python',
          'Development Status :: 4 - Beta',
          'Natural Language :: English',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'Operating System :: OS Independent',
          'Topic :: Scientific/Engineering :: Physics',
          'Topic :: Scientific/Engineering :: Visualization',
          'Topic :: Database :: Front-Ends',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11'],
      )
