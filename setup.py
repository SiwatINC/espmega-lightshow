from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='espmega_lightshow',
    version='4.1',
    license='Apache 2.0',
    author="Siwat Sirichai",
    author_email='siwat@siwatinc.com',
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={
        '': ['*.png', '*.ico'],
    },
    include_package_data=True,
    url='https://github.com/SiwatINC/espmega-lightshow',
    keywords='light mqtt espmega',
    install_requires=[
          'espmega',
          'pillow'
      ],

)