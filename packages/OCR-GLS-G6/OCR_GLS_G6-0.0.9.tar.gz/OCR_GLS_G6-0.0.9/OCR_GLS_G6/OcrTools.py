import easyocr
import cv2
from pyzbar.pyzbar import decode
import os
import tempfile
from ironpdf import PdfDocument
import PyPDF2

class OcrTools:
    def __init__(self, pdfPath):
        self.pdfPath = pdfPath

    def pdfToImg(pdfPath="", locationFile=""):
        pdf = PdfDocument.FromFile(pdfPath)
        # Extract all pages to a folder as image files
        pdf.RasterizeToImageFiles(locationFile, DPI=300)
        return locationFile

    def count_pdf_pages(file_path):
        file = open(file_path,'rb')
        pdfReader = PyPDF2.PdfReader(file)
        totalPages = len(pdfReader.pages)
        print(f"Total Pages: {totalPages}")
        return totalPages
    
    def easyOCR(typeOfOcr='Text', locationFile="",
                area={'offset_x_min': 0, 'offset_y_min': 0,
                      'width': 0, 'height': 0},
                dataCheck=['valueForCheck'],
                languageOcr=['th', 'en'],
                deviation=50
                ):
        temp = tempfile.mkdtemp(prefix="pre_",suffix="_suf")
        name, extension = os.path.splitext(locationFile)
        pdfCount=OcrTools.count_pdf_pages(locationFile)
        if extension == ".pdf":
            root = locationFile.find("/")
            if root > 0:
                newFileLocation = locationFile.rsplit('/', 1)[1]
            else:
                newFileLocation = "."
            print(newFileLocation)
            imageLocation = OcrTools.pdfToImg(
                locationFile, temp+"\\"+newFileLocation+".png")
        else:
            imageLocation = locationFile
        area_xMax = area['offset_x_min']+area['width']
        area_yMax = area['offset_y_min']+area['height']
        allResultDetective = []
        for i in range(pdfCount):
            if pdfCount >1:
                i+=1
                print(i,imageLocation)
                fileLocation = imageLocation.replace(".pdf", ".pdf_pg"+str(i))
            else:
                fileLocation = imageLocation
            if typeOfOcr == 'Text':
                reader = easyocr.Reader(languageOcr)
                allResults = reader.readtext(fileLocation)
                for result in allResults:
                    print(result)
                    pos1, pos2, pos3, pos4 = result[0]
                    xMin = round(min([pos1[0], pos2[0], pos3[0], pos4[0]]))
                    xMax = round(max([pos1[0], pos2[0], pos3[0], pos4[0]]))
                    yMin = round(min([pos1[1], pos2[1], pos3[1], pos4[1]]))
                    yMax = round(max([pos1[1], pos2[1], pos3[1], pos4[1]]))
                    if (area['offset_x_min'] in range(xMin-deviation, xMin+deviation)):
                        if (area['offset_y_min'] in range(yMin-deviation, yMin+deviation)):
                            if (area_xMax in range(xMax-deviation, xMax+deviation)):
                                if (area_yMax in range(area_yMax-deviation, area_yMax+deviation)):
                                    word = result[1]
                                    print(word)
                                    for wordCheck in dataCheck:
                                        if word.lower() == wordCheck.lower():
                                            valid = True
                                        else:
                                            valid = False
                                    accuracy_percent = str(
                                        round(result[2]*100))+"%"
                                    allResultDetective.append({
                                        'page':i,
                                        'coordinates': result[0],
                                        'value': word,
                                        'valid': valid,
                                        'accuracy_percent': accuracy_percent,
                                    })
                os.remove(fileLocation)
            elif typeOfOcr == 'qrcode':
                image = cv2.imread(fileLocation)
                cropped_image = image[area['offset_y_min']:area_yMax, area['offset_x_min']:area_xMax]
                result = decode(cropped_image)
                os.remove(fileLocation)
                if result:
                    allResultDetective.append({
                        'page':i,
                        'coordinates': [area['offset_y_min'], area_yMax, area['offset_x_min'], area_xMax],
                        'value': result[0].data,
                        'valid': True,
                        'accuracy_percent': '-',
                    }) 
                else:
                    allResultDetective.append({
                        'page':i,
                        'coordinates': [area['offset_y_min'], area_yMax, area['offset_x_min'], area_xMax],
                        'value': result,
                        'valid': False,
                        'accuracy_percent': '-',
                    })
        return allResultDetective
