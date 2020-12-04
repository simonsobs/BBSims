from setuptools import setup

setup(name = 'bbsims',
      version = '0.1',
      description = '',
      url = '',
      author = 'Nicoletta Krachmalnicoff',
      author_email = 'nkrach@sissa.it',
      license = 'MIT',
      packages = ['bbsims'],
      package_dir = {'bbsims': 'bbsims'},
      zip_safe = False,
      entry_points = {
        'console_scripts': [
            'so_bbsims = bbsims.pipeline:__main__'
        ]
      })
