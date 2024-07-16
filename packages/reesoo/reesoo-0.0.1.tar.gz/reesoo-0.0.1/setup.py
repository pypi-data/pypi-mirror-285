from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='reesoo',
  version='0.0.1',
  description='List of programs',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Riyansh Prem',
  author_email='riyansh969@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='pro', 
  packages=find_packages(),
  install_requires=[''] 
)