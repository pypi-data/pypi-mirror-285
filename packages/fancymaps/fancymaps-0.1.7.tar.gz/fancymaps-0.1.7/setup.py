from setuptools import setup

setup(
   name='fancymaps',
   version='v0.1.7',
   description='Visually appealing diverging colormaps',
   long_description_content_type = 'text/markdown',
   packages=['fancymaps'],
   package_dir={'fancymaps': 'src'},
   install_requires=['matplotlib>=3.2', 'setuptools>=30.3.0'],
)

