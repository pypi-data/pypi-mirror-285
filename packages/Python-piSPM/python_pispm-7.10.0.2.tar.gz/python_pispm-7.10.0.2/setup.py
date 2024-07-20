from setuptools import setup

setup(name='Python-piSPM',
      version='7.10.0.2',
      description='Python piSPM is a Python wrapper for Pickering Switch Path Manager.',
      url='https://www.pickeringtest.com',
      author='Pickering Interfaces',
      author_email='support@pickeringtest.com',
      readme='README.md',
      license='LICENSE.txt',
      packages=['pi_spm'],
      install_requires=[
          'future',
      ],
      zip_safe=False)
