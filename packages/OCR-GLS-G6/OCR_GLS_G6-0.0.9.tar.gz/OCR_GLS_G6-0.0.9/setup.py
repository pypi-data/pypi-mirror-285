import io
from os.path import abspath, dirname, join
from setuptools import find_packages, setup


HERE = dirname(abspath(__file__))
LOAD_TEXT = lambda name: io.open(join(HERE, name), encoding='UTF-8').read()
DESCRIPTION = '\n\n'.join(LOAD_TEXT(_) for _ in [
    'README.rst'
])

setup(
  name = 'OCR_GLS_G6',      
  packages = ['OCR_GLS_G6'], 
  version = '0.0.9',  
  license='MIT', 
  description = 'OCR_GLS_G6 - Optical character recognition and QR codes. Support Multiple PDF page file.',
  long_description=DESCRIPTION,
  author = 'Burin Panchat',                 
  author_email = 'burin.gbp@gmail.com',     
  url = 'https://git.bdms.co.th/Burin.Pa/ocr_gls_g6',  
  download_url = 'https://git.bdms.co.th/Burin.Pa/ocr_gls_g6/-/blob/master/dist/ocr_gls_g6.zip',  
  keywords = ['OCR_GLS_G6', 'OCR', 'ocr'],   
  classifiers=[
    'Development Status :: 3 - Alpha',     
    'Intended Audience :: Developers',     
    'Topic :: Documentation',
    'License :: OSI Approved :: MIT License',        
    'Programming Language :: Python :: 3.7',
  ],
  install_requires=[
    "easyocr==1.7.1",
    "pyzbar==0.1.9",
    "IronPdf==2024.5.1.2",
    "PyPDF2==3.0.1"
    ],
)