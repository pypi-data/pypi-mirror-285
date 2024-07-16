(OCR-GLS-G6) OCR
----------------

|github release version| |python version| |license|

--------------

.. _วิธีติดตั้ง:

วิธีติดตั้ง
-----------

เปิด CMD / Terminal

.. code:: python

   pip install OCR-GLS-G6

--------------

.. _วิธีใช้:

วิธีใช้
-------

.. code:: python

   from OCR_GLS_G6.OcrTools import OcrTools

   fileLocation="simple.pdf" // ไฟล์ PDF หรือ ไฟล์รูปภาพ

   OcrTools.easyOCR(typeOfOcr="qrcode",locationFile=fileLocation,area={'offset_x_min':2078,'offset_y_min':3152,'width':213,'height':220})

   // Output
   {   
       'coordinates': [ตำแหน่งของไฟล์ที่อ่านข้อมูล],
       'value': ข้อความที่ได้จาก QR หรือ ข้อความในไฟล์ที่ต้องการ,
       'valid': ความถูกต้องของข้อมูล
       'accuracy_percent': เปอร์เซ็นความถูกต้องของข้อมูล
   }

--------------

คำแนะนำ
-------

============ ========================
Area         คำอธิบาย
============ ========================
offset_x_min พิกัดแกน X ที่น้อยที่สุด
offset_y_min พิกัดแกน Y ที่น้อยที่สุด
width        ความกว้างของพื้นที่
height       ความยาวของพื้นที่
============ ========================

พัฒนาโดย: Burin Panchat GLS Develop G6

.. |github release version| image:: https://img.shields.io/pypi/pyversions/OCR-GLS-G6
.. |python version| image:: https://img.shields.io/pypi/v/OCR-GLS-G6
   :target: https://pypi.org/project/OCR-GLS-G6/0.0.6/
.. |license| image:: https://img.shields.io/github/license/nhn/tui.editor.svg
