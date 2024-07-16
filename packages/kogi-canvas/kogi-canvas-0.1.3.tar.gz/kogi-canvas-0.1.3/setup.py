from setuptools import setup, find_packages

'''
python3 -m unittest
vim setup.py
rm -rf dist/
python3 setup.py sdist bdist_wheel
twine upload --repository pypi dist/*
'''

def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(name="kogi-canvas",
      version="0.1.3",
      license='Apache',
      author='Kimio Kuramitsu',
      description="Canvas from KOGI",
      url="https://github.com/kuramitsulab/kogi-canvas",
      packages=['kogi_canvas'],
      # package_dir={"": "src"},
      package_data={'kogi_canvas': ['./*.*']},
      install_requires=_requires_from_file('requirements.txt'),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: Apache Software License',
          'Framework :: IPython',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Intended Audience :: Education',
      ],
      )
