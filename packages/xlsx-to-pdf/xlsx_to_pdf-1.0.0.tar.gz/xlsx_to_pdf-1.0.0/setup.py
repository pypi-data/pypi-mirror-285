from setuptools import setup


setup(
  name = 'xlsx-to-pdf',
  packages = ['invoicing'],
  version = '1.0.0', 
  license='MIT',
  description = 'This package can be used to convert Excel invoices to PDF invoices.',
  author = 'Anay Sanish',                   
  author_email = 'anayvalath7@gmail.com',  
  url = 'https://github.com/avs-7/app19-python-package',              
  keywords = ['invoice', 'excel', 'pdf', 'conversion'],   
  install_requires=['pandas', 'fpdf', 'openpyxl'],
  classifiers=[
    'Development Status :: 3 - Alpha',          
    'Intended Audience :: Developers',          
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3.8',      
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
  ],
)
