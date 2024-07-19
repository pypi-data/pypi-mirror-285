from setuptools import setup

setup(name='LeafSync',
      author='German Espinosa',
      author_email='germanespinosa@gmail.com',
      long_description=open('./LeafSync/README.md').read() + '\n---\n<small>Package created with Easy-pack</small>\n',
      long_description_content_type='text/markdown',
      packages=['LeafSync'],
      license='MIT',
      include_package_data=True,
      version='0.0.0',
      zip_safe=False)
