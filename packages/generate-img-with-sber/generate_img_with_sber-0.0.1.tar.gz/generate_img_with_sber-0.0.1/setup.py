from setuptools import setup

setup(
  name='generate_img_with_sber',
  version='0.0.1',
  author='Ivango128',
  author_email='poplayhin2002@gmail.com',
  description='This is simple library for generating images using the Kavinsky neural network',
  long_description='This is simple library for generating images using the Kavinsky neural network',
  long_description_content_type='text/markdown',
  url='https://github.com/Ivango128/generate_img_with_sber',
  packages=['generate_img_with_sber'],
  install_requires=['requests'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='generate pictures',
  project_urls={
    'GitHub': 'https://github.com/Ivango128/generate_img_with_sber'
  },
  python_requires='>=3.6'
)