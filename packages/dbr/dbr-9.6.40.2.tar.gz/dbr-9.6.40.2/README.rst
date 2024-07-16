Dynamsoft Python Barcode SDK
====================================================
|version| |python| |pypi| 

.. |version| image:: https://img.shields.io/pypi/v/dbr?color=orange
.. |python| image:: https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue
.. |pypi| image:: https://img.shields.io/pypi/dm/dbr


What You Should Know About Dynamsoft Barcode Reader
---------------------------------------------------
|trial|

.. |trial| image:: https://img.shields.io/badge/Get-30--day%20FREE%20Trial-blue
            :target: https://www.dynamsoft.com/customer/license/trialLicense?product=dbr

`Dynamsoft Barcode Reader SDK <https://www.dynamsoft.com/barcode-reader/overview/?utm_source=pypi>`_ 
enables you to efficiently embed barcode reading functionality in your
web, desktop or mobile application using just a few lines of code.
Saving you months of added development time and resources, our SDK can
create high-speed and reliable barcode scanner software applications to
meet your business needs.

About Python Barcode SDK
-------------------------
The Python Barcode SDK is a wrapper for Dynamsoft C++ Barcode SDK. It comes with all the general
features of Dynamsoft Barcode Reader, bringing convenience for Python developers.


Version
-------

-  9.6.40.2

Supported Platforms
-------------------

- Windows x64

- Linux(x64, ARM32, ARM64)

- macOS(10.15+)

Supported Python Versions
-------------------------

-  Python3.6

-  Python3.7

-  Python3.8

-  Python3.9

-  Python3.10

-  Python3.11

-  Python3.12

Installation
------------

   pip install dbr

Supported Symbologies
---------------------

-  Linear Barcodes (1D) :

   -  Code 39 *(including Code 39 Extended)*
   -  Code 93
   -  Code 128
   -  Codabar
   -  Interleaved 2 of 5
   -  EAN-8
   -  EAN-13
   -  UPC-A
   -  UPC-E
   -  Industrial 2 of 5
   -  MSI Code
   -  Code 11

-  2D Barcodes :

   -  QR Code *(including Micro QR Code)*
   -  Data Matrix
   -  PDF417 *(including Micro PDF417)*
   -  Aztec Code
   -  MaxiCode *(mode 2-5)*
   -  DotCode

-  Patch Code

-  Pharmacode

-  GS1 Composite Code

-  GS1 DataBar :

   -  Omnidirectional
   -  Truncated
   -  Stacked
   -  Stacked Omnidirectional
   -  Limited
   -  Expanded
   -  Expanded Stacked

-  Postal Codes :

   -  USPS Intelligent Mail
   -  Postnet
   -  Planet
   -  Australian Post
   -  UK Royal Mail

Quick Start
-----------
.. code-block:: python

   from dbr import *

   # Apply for a trial license: https://www.dynamsoft.com/customer/license/trialLicense?product=dbr&utm_source=github
   license_key = "Input your own license"
   image = r"Please input your own image path"

   BarcodeReader.init_license(license_key)

   reader = BarcodeReader()

   try:
      text_results = reader.decode_file(image)

      if text_results != None:
         for text_result in text_results:
               print("Barcode Format : ")
               print(text_result.barcode_format_string)
               print("Barcode Text : ")
               print(text_result.barcode_text)
               print("Localization Points : ")
               print(text_result.localization_result.localization_points)
               print("Exception : ")
               print(text_result.exception)
               print("-------------")
   except BarcodeReaderError as bre:
      print(bre)


Sample Code
------------
https://github.com/Dynamsoft/barcode-reader-python-samples

Documentation
-----------------

- `API <https://www.dynamsoft.com/barcode-reader/programming/python/api-reference/?utm_source=pypi>`_
- `User Guide <https://www.dynamsoft.com/barcode-reader/programming/python/user-guide.html?utm_source=pypi>`_
- `Release Notes <https://www.dynamsoft.com/barcode-reader/programming/python/release-notes/python-9.html?utm_source=pypi>`_


Contact Us
----------

support@dynamsoft.com
