## -*- coding: utf-8; mode: python; -*-
# -*- coding: utf-8; -*-
"""
Tasks for ${name}
"""

import os
import shutil

from invoke import task


here = os.path.abspath(os.path.dirname(__file__))
exec(open(os.path.join(here, '${pkg_name}', '_version.py')).read())


@task
def release(c):
    """
    Release a new version of ${name}
    """
    # rebuild local tar.gz file for distribution
    if os.path.exists('${egg_name}.egg-info'):
        shutil.rmtree('${egg_name}.egg-info')
    c.run('python -m build --sdist')

    # filename of built package
    filename = '${pypi_name}-{}.tar.gz'.format(__version__)

    # TODO: uncomment and update these details, to upload to private PyPI
    #c.run('scp dist/{} rattail@pypi.example.com:/srv/pypi/${folder}/'.format(filename))

    # TODO: or, uncomment this to upload to *public* PyPI
    #c.run('twine upload dist/{}'.format(filename))
