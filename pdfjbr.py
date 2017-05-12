#!/usr/bin/env python 
# -*- encoding: latin1 -*-

__author__ = 'jadsonbr@outlook.com.br <Jadson B. Ribeiro>'
__copyright__ = "Copyright 2017 by Jadson Bonfim Ribeiro <jadsonbr@outlook.com.br>"
__licence__ = "MIT Licence"
__version__ = "0.1.1"

import sys
try:
    from PyPDF2 import PdfFileWriter, PdfFileReader
except:
    print("[ERROR]: This script requires the PyPdf library. ")
    sys.exit(0)
import os
import glob
import tempfile
from datetime import datetime


config = {
    'outputdir': '',
    'sufChunk': 'cpm',
    'sufBurst': 'seite',
    'sufSplit': 'split',
    'numformat': '%(#)03d'
}


def _formatDate(timestamp):
    datum = datetime.fromtimestamp(timestamp)
    return datum.strftime('%d-%m-%Y %H:%M')


def _glob(expr):
    """ expands the wildcard expressions to filenames """
    matchedfiles = []
    # if expr is a directory like c:\mypdfs, we add a *.pdf to the end in order to support dir globbing
    if (os.path.isdir(expr)):
        expr = os.path.join(expr, '*.pdf')
        # save all matched files in a list
    matchedfiles = glob.glob(expr)
    # just make sure we really only caught PDFs
    for n, match in enumerate(matchedfiles):
        if not match.lower().endswith(".pdf"):
            del matchedfiles[n]
    return matchedfiles


def _writePDF(inputfile, output, filecount, suffix):
    """writes the in-memory-PDF to a file and builds the filename"""
    base, ext = os.path.splitext(inputfile)
    filenum = config['numformat'] % {'#':filecount}
    targetfile = "%(base)s-%(suffix)s-%(filenum)s%(ext)s" % \
    {'base': base,
    'suffix': suffix,
    'filenum': filenum,
    'ext': ext}
    filecount += 1
    try:
        outputStream = open(targetfile, "wb")
        output.write(outputStream)
        outputStream.close()
    except:
        _error("[ERROR] Could not write %s file" % (targetfile))


def _writePDFChunk(inputfile, output, filecount, suffix, destino=None):
    """writes the in-memory-PDF to a file and builds the filename"""
    base, ext = os.path.splitext(inputfile)
    if destino is not None:
        base = destino +'\\'+os.path.splitext(os.path.basename(inputfile))[0]
    filenum = config['numformat'] % {'#':filecount}
    targetfile = "%(base)s-%(suffix)s-%(filenum)s%(ext)s" % \
    {'base': base ,
    'suffix': suffix,
    'filenum': filenum,
    'ext': ext}
    filecount += 1
    try:
        outputStream = open(targetfile, "wb")
        output.write(outputStream)
        outputStream.close()
    except:
        _info("[ERROR] Could not write %s file" % (targetfile))
        # _error("[ERROR] Could not write %s file" % (targetfile))


def _error(msg):
    print(msg)
    sys.exit(0)

def _info(msg):
    print(msg)


def PDFInfo(inputfiles):
    """prints useful Information about a PDF File """
    totalpagenum = 0
    totalfilesize = 0
    for inputfile in inputfiles:
        input1 = PdfFileReader(open(inputfile, "rb"))
        fileinfo = os.stat(inputfile)
        filesizekb = fileinfo[6] / 1024
        pagenum = input1.getNumPages()
        print("\n\n")
        print(inputfile)
        print("\n")
        print("\tTitle:\t\t %s" % input1.getDocumentInfo().title)
        print("\tSize (KBytes):\t\t %s" % filesizekb)
        print("\tLast modified:\t\t %s" % (_formatDate(fileinfo[8])))
        print("\tCreated:\t\t %s" % (_formatDate(fileinfo[9])))
        print("\tPages :\t\t %s" % pagenum)
        print("\tAuthor :\t\t %s" % input1.getDocumentInfo().author)
        print("\tSource document created with :\t\t %s" % input1.getDocumentInfo().creator)
        print("\tIn PDF converted by :\t\t %s" % input1.getDocumentInfo().producer)
        totalpagenum += pagenum
        totalfilesize += filesizekb
    print(80 * "-")
    print("OVERALL INFO:")
    print("Total pages: %s" % (totalpagenum))
    print("Total file size (kb): %s" % (totalfilesize))


def split(inputfile, splitcount=''):
    """splits a PDF after n Pages"""
    output = PdfFileWriter()
    input1 = PdfFileReader(open(inputfile, "rb"))
    try:
        splitcount = int(splitcount)
    except:
        splitcount = input("How many pages split?: ")
        splitcount = int(splitcount)
    print(inputfile)
    totalpages = input1.getNumPages()
    # add page 1 from input1 to output document, unchanged
    for n, page in enumerate(input1.pages):
        if n % splitcount == 0 and n > 0:
            fileno = int(n/splitcount)
            _writePDF(inputfile, output, fileno, config['sufSplit'])
            output = PdfFileWriter()
        output.addPage(page)
    fileno = int(n/splitcount + 1)
    _writePDF(inputfile, output, fileno, config['sufSplit'])


def burst(inputfile):
    """bursts a PDF (creates a new PDF file for every page in the source PDF) """
    input1 = PdfFileReader(open(inputfile, "rb"))
    for n, page in enumerate(input1.pages):
        output = PdfFileWriter()
        output.addPage(page)
        _writePDF(inputfile, output, n, config['sufBurst'])


def chunk(inputfile, chunklimit='', outputDir=None):
 
    """chunks a PDF (splits the pdf into chunks that do not exceed a certain filesize) """
    input1 = PdfFileReader(open(inputfile, "rb"))
    tmppages = []
    try:
        chunklimit = float(chunklimit)
    except:
         chunklimit = input("Size limit for the partial documents (in MB) z.B. 0.6, 3?: ")
         chunklimit = float(chunklimit)
    chunklimit = chunklimit*1000*1000
    chunksize = 0
    # write each page of the pdf to a temporary file, TODO: replace tempfiles by StringIO (Performance!)
    for n, page in enumerate(input1.pages):
        page.compressContentStreams()
        output = PdfFileWriter()
        output.addPage(page)
        fd, temp_file_name = tempfile.mkstemp()
        outputStream = open(temp_file_name, 'wb')
        tmppages.append(temp_file_name)
        output.write(outputStream)
        outputStream.close()
        os.close(fd)
        # check each page tmpfile for size and merge as much files as possible before reaching the limit
        output = PdfFileWriter()
    #print("======== NEW PDF ========")
    filecount = 1
    for n, tmppage in enumerate(tmppages):
        pdfpage = PdfFileReader(open(tmppage, "rb"))
        pagesize = os.path.getsize(tmppage)
        # Check 500kb  per page
        if (pagesize / 1024.0) > 0.500:
            _info('Page %s exceeds the limit of 500kb' % n)
        if pagesize > chunklimit:
            _error("[ERROR] Page %s exceeds the chunk limit of %s MB. Please choose a larger limit." \
            % (n, chunklimit/1000000))
        pagenum = pdfpage.getNumPages()
        # print ("    Seite:%d, Groesse: %d") % (n,pagesize)
        if chunksize + pagesize < chunklimit:
            output.addPage(pdfpage.getPage(0))
            # print tmppage
            chunksize += pagesize
        else:
            _writePDFChunk(inputfile, output, filecount, config['sufChunk'], outputDir)
            filecount += 1
            output = PdfFileWriter()
            output.addPage(pdfpage.getPage(0))
            print("======== NEW PDF  ========")
            chunksize = 0 + pagesize
        if n+1 == len(tmppages):
            _writePDFChunk(inputfile, output, filecount, config['sufChunk'], outputDir)

        
    
def merge(inpdfs, outpdf):
    """merges 2 or more pdfs into one
     TODO: support pages ranges for each page
           use logging functions (debug/error/etc)
    """
    output = PdfFileWriter()
    inputs = []
    for inpdf in inpdfs:
        try:
            mergein = (PdfFileReader(open(inpdf, "rb")))
            print("%s Title: %s (%s Pages)" % (inpdf, mergein.getDocumentInfo().title, mergein.getNumPages()))
            inputs.append(mergein)
        # invalid file
        except IOError:
            print("Error! Could not read file %s") % (inpdf)
    for input in inputs:
        for page in input.pages:
            output.addPage(page)
    outputStream = open(outpdf, "wb")
    output.write(outputStream)
    outputStream.close()
    

def _intro():
    print(90 * "=")
    print(40 * " " + "PDF Manipulator")
    print(15 * " " + "(c) 2017 by Jadson Bonfim Ribeiro  |  E-mail: jadsonbr@outlook.com.br")
    print(90 * "=")
    print("""
       use:
 
       pdfjbr split 5 file.pdf              File file.pdf in PDFs with 5 pages each
       pdfjbr chunk 3 file.pdf outputDir    File file.pdf can be divided by up to 3 MB by PDFs
       pdfjbr burst file.pdf                Write each single page in file.pdf in a PDF
       pdfjbr merge f1.pdf f2.pdf           F1.pdf and f2.pdf merge into a PDF
       pdfjbr merge output.pdf dir          Merge all PDFs in the dir directory into output.pdf
       pdfjbr info f1.pdf                   Displays document information (size, page number, title, ...) at f1.pdf
       pdfjbr pagecount file.pdf            Displays information about the number of pages in the document
          """)
    _error("")

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("[ERROR] Invalid call")
        _intro()
    elif sys.argv[1] == "split":
        if os.path.isfile(sys.argv[-1]):
            inputfile = sys.argv[-2]
            split(inputfile)
        else:
            _error("[ERROR] Could not read file %s" % (sys.argv[2]))
    elif sys.argv[1] == "burst":
        if os.path.isfile(sys.argv[2]):
            inputfile = sys.argv[2]
            burst(inputfile)
        else:
            _error("[ERROR] Could not read file %s" % (sys.argv[2]))

    elif sys.argv[1] == "merge":
        mergefiles = []
        outpdf = sys.argv[2]
        if os.path.isfile(sys.argv[2]):
            input("[WARNING] %s already exists. Press Ctrl + C to abort, <ENTER> to continue." % (sys.argv[2]))
        for inputfile in sys.argv[3:]:
                mergefiles.extend(_glob(inputfile))
        print(mergefiles)
        merge(mergefiles, outpdf)

    elif sys.argv[1] == "chunk" and len(sys.argv) > 4:
        if os.path.isfile(sys.argv[-2]):
            chunklimit = sys.argv[-3]
            inputfile = sys.argv[-2]
            if not os.path.isdir(sys.argv[-1]):
                _error("[ERROR] Could not find directory %s" % (sys.argv[4]))
            else:
                output = sys.argv[4];
            chunk(inputfile, chunklimit, output)
        else:
            _error("[ERROR] Could not read file %s" % (sys.argv[2]))

    elif sys.argv[1] == "info":
        PDFInfo(_glob(sys.argv[2]))

    elif sys.argv[1] == "pagecount":
        if os.path.isfile(sys.argv[2]):
            input1 = PdfFileReader(open(sys.argv[2], "rb"))
            print("%d Pages" % input1.getNumPages())
        else:
            _error("[ERROR] Could not read file %s" % (sys.argv[2]))

    elif sys.argv[1] == "help":
        _intro()

#pyinstaller --clean --onefile --console --icon "D:\Projetos-Python\jbrpdf\jbrpdf.ico" --uac-admin --win-private-assemblies pdfjbr.py
