#!/usr/bin/python2.6

# Standard library
import os
import sys

# Set up Paver
import paver
import paver.doctools
import paver.misctasks
from paver.path import path
from paver.easy import *
import paver.setuputils
paver.setuputils.install_distutils_tasks()
try:
    from sphinxcontrib import paverutils
except:
    paverutils = None


PROJECT = 'inspyred'
VERSION = '1.0'

# The sphinx templates expect the VERSION in the shell environment
os.environ['VERSION'] = VERSION

# Read the long description to give to setup
README = path('README').text()

# Scan the input for package information
# to grab any data files (text, images, etc.) 
# associated with sub-packages.
PACKAGE_DATA = paver.setuputils.find_package_data(PROJECT, 
                                                  package=PROJECT,
                                                  only_in_packages=False
                                                  )

options(
    setup=Bunch(
        name = PROJECT,
        version = VERSION,
        description='A framework for creating bio-inspired computational intelligence algorithms in Python.',
        long_description=README,
        author='Aaron Garrett',
        author_email='aaron.lee.garrett@gmail.com',
        url='http://%s.github.com' % PROJECT,
        download_url='https://github.com/{0}/{0}/downloads/{0}-{1}.tar.gz'.format(PROJECT, VERSION),
        license='GPLv3+',
        platforms=('Any'),
        keywords=('python', 'optimization', 'evolutionary computation', 'genetic algorithm', 
                  'particle swarm', 'estimation of distribution', 'differential evolution',
                  'nsga', 'paes', 'island model', 'multiobjective', 'ant colony'),

        classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Artificial Intelligence'
          ],
        
        packages = [PROJECT, '%s.ec' % PROJECT, '%s.ec.variators' % PROJECT, '%s.swarm' % PROJECT],
        package_data=PACKAGE_DATA,
    ),
    
    sdist = Bunch(
    ),
    
    sphinx = Bunch(
        sourcedir='docs',
        docroot = '.',
        builder = 'html',
        doctrees='docs/_build/doctrees',
        confdir = 'docs',
    ),

    html = Bunch(
        builddir='docs',
        outdir='html',
        templates='pkg',
    ),

    # Some of the files include [[[ as part of a nested list data structure,
    # so change the tags cog looks for to something less likely to appear.
    cog=Bunch(
        beginspec='{{{cog',
        endspec='}}}',
        endoutput='{{{end}}}',
    ),
    
    minilib=Bunch(
        extra_files=['doctools']
    ),
)

def run_script(input_file, script_name, interpreter='python'):
    """Run a script in the context of the input_file's directory, 
    return the text output formatted to be included as an rst
    literal text block.
    """
    from paver.easy import sh
    from paver.path import path
    rundir = path(input_file).dirname()
    output_text = sh('cd %(rundir)s && %(interpreter)s %(script_name)s 2>&1' % vars(), capture=True)
    response = '\n::\n\n\t$ %(interpreter)s %(script_name)s\n\t' % vars()
    response += '\n\t'.join(output_text.splitlines())
    while not response.endswith('\n\n'):
        response += '\n'
    return response
    
    
# Stuff run_script() into the builtins so we don't have to
# import it in all of the cog blocks where we want to use it.
__builtins__['run_script'] = run_script


def remake_directories(*dirnames):
    """Remove the directories and recreate them.
    """
    for d in dirnames:
        d = path(d)
        if d.exists():
            d.rmtree()
        d.mkdir()
    return

@task
@needs(['cog'])
def html(options):
    if paverutils is None:
        raise RuntimeError('Could not find sphinxcontrib.paverutils, will not be able to build HTML output.')
    paverutils.html(options)
    return

@task
@needs(['generate_setup', 'minilib', 
        'html_clean', 
        'setuptools.command.sdist'
        ])
def sdist(options):
    """Create a source distribution.
    """
    pass

@task
def html_clean(options):
    """Remove sphinx output directories before building the HTML.
    """
    remake_directories(options.sphinx.doctrees, options.html.outdir)
    html(options)
    return

