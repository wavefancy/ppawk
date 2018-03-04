from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='ppawk',
      version='0.1',
      description='A awk like python one line processor',
      url='',
      author='Wallace Wang',
      author_email='wavefancy@gmail.com',
      license='MIT',
      packages=['ppawk'],
      zip_safe=False)
