from setuptools import setup

setup(name = 'sobb_mapsims',
      version = '0.1',
      description = '',
      url = '',
      author = 'Nicoletta Krachmalnicoff',
      author_email = 'nkrach@sissa.it',
      license = 'MIT',
      packages = ['sobb_mapsims'],
      package_dir = {'sobb_mapsims': 'sobb_mapsims'},
      zip_safe = False,
      entry_points = {
        'console_scripts': [
            'sobb_mapsims = sobb_mapsims.pipeline:__main__'
        ]
      })
