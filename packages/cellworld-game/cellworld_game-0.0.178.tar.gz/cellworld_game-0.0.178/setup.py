from setuptools import setup

setup(name='cellworld_game',
      description='Simulation environment for the cellworld research platform',
      url='https://github.com/germanespinosa/cellworld_game',
      author='German Espinosa',
      author_email='germanespinosa@gmail.com',
      long_description=open('./cellworld_game/README.md').read() + '\n---\n<small>Package created with Easy-pack</small>\n',
      long_description_content_type='text/markdown',
      packages=['cellworld_game'],
      install_requires=['cellworld', 'pygame', 'shapely', 'pulsekit'],
      license='MIT',
      include_package_data=True,
      version='0.0.178',
      zip_safe=False)
