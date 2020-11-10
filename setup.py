from setuptools import setup

setup(name = 'LB_mbs',
      version = '0.1',
      description = '',
      url = '',
      author = 'Nicoletta Krachmalnicoff',
      author_email = 'nkrach@sissa.it',
      license = 'MIT',
      packages = ['lb_mbs'],
      package_dir = {'lb_mbs': 'lb_mbs'},
      zip_safe = False,
      entry_points = {
        'console_scripts': [
            'litebird_mbs = lb_mbs.pipeline:__main__'
        ]
      })
