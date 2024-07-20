from distutils.core import setup, Extension

module = Extension('RFCommRAW', sources=['rfcommraw/rfcommraw.c'], libraries=['bluetooth'])

setup(name='RFCommRAW',
      version='2.0',
      description='RFCOMM low level communication',
      ext_modules=[module])

