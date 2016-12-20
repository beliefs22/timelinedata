import os
import PyPDF2
directory = r'H:\Pycharm Projects\timelinedata_working\Ip_Subject_Files\pdfs'
sep = os.sep
current_files = os.listdir(directory)

for thefile in current_files:
    if thefile.endswith(".pdf"):
        output = thefile.replace(".pdf",".txt")
        with open(directory + sep + output,'w') as outfile, open(directory + sep + thefile,'rb') as pdffile:
            print("writing file for", thefile)
            pdfreader = PyPDF2.PdfFileReader(pdffile)
            num_of_pages = pdfreader.numPages
            for i in range(num_of_pages):
                page = pdfreader.getPage(i)
                text = page.extractText()
                outfile.write(text.encode('ascii', 'ignore'))


