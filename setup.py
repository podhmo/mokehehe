from setuptools import setup, find_packages
requires = [
    "pyramid", 
    "sqlalchemy", 
    "pyramid_layout"
    ]

setup(name='mokehehe',
      version='0.0.1',
      description='utility for portable model definition of sqlalchemy models',
      long_description="", 
      author='podhmo',
      package_dir={'': '.'},
      packages=find_packages('.'),
      install_requires = requires,
      test_suite="mokehehe.tests", 
      entry_points = """
      """,
      )
