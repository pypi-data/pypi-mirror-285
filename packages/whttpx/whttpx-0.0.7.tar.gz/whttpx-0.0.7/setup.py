from setuptools import find_packages, setup

with open('./README.md', 'r', encoding='utf-8') as fh:
  readme = fh.read()

setup(
  name='whttpx',
  version='0.0.7',
  description='Obtiene las variables de entorno, para tener mantenimientos eficientes',
  long_description=readme,
  long_description_content_type='text/markdown',
  author='Pedro Jesús Pérez Hernández',
  author_email='pedrojesus.perez@welldex.mx',
  url='https://gitwell.gwldx.com:2443/python_libraries/httpx_client',
  install_requires=[
    'httpx',
    'wellog',
    'envOS',
    ],
  license='MIT',
  packages=find_packages(),
  include_package_data=True
)