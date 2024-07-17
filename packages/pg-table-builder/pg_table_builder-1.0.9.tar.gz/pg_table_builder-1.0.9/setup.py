from setuptools import setup


def readme():
    return 'https://github.com/byBenPuls/table-builder-pg/'


setup(
  name='pg_table_builder',
  version='1.0.9',
  author='Ben Puls',
  author_email='discordben7@gmail.com',
  description='Table builder for postgresql',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/byBenPuls/table-builder-pg',
  packages=['pg_table_builder'],
  install_requires=[],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='postgresql',
  project_urls={
    'GitHub': 'https://github.com/byBenPuls/table-builder-pg'
  },
  python_requires='>=3.9'
)