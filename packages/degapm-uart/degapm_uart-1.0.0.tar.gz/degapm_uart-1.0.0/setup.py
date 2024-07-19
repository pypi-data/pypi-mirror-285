from setuptools import setup, find_packages

with open("README.rst", "r") as f:
  long_description = f.read()

setup(name='degapm_uart',  
      version='1.0.0', 
      description='A2000 BP UART Debug control API',
      long_description=long_description,
      author='degastorage',
      author_email='jiaming.shi@degastorage.com',
      url='https://www.degastorage.com/',
      install_requires=[],
      license='MIT License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Topic :: Software Development :: Libraries'
      ],
      )