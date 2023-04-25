from tkinter.filedialog import askopenfile
import os
import shutil
import datetime
import xml.etree.ElementTree as ET
import re
import html2text
from tkinter.filedialog import askdirectory
from bs4 import UnicodeDammit

DEFAULT_DATA_DIR = "C:\\BrAutomation\\AS410\\Help-en\\Data"
# DEFAULT_DATA_FILE = "brhelpcontent.xml"
# DEFAULT_DATA_FILE = "brhelpcontent_tiny.xml"
DEFAULT_DATA_FILE = "brhelpcontent_small.xml"
OUTPUT_DIR = ".\\out\\"
OUTPUT_DIR_SUFFIX = "HelpText"
GENERATE_TEXT_ENABLE = True                                         # If False, no text files will be generated (i.e. skip main function)
PATH_AND_TEXT_LOG_ENABLE = False                                    # If True, make a CSV file with TOC path and text of every article (for analysis)
PATH_AND_TEXT_LOG_DIR = "\\length_study\\"
PATH_AND_TEXT_LOG_FILENAME = "paths_and_text.csv"
CREATE_FULL_PATH_FILE_LIST = True                                   # If True, Make a single file with all toc content in root output folder, for searching paths and titles
FULL_TOC_PATH_FILE_LIST_FILENAME = "FullTocPathFileList.info"
ERROR_LOG_FILENAME = "errors.txt"
MAX_FOLDER_LEN = 11
PRINT_PROCESS_LOCATION = True

baseDirAbsPath = DEFAULT_DATA_DIR
autoGenNoticeText = "# NOTE: THIS HEADER AUTO-GENERATED BY AS HELP TEXTIFIER"


def handleError(error):
    # print(error)
    with open(errorLogAbsDir, 'a', encoding="utf-8") as e:
        e.write(error + '\n')


def parse(htmlSrc: str): 
    # Ref: https://github.com/Alir3z4/html2text/blob/master/docs/usage.md
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_tables = True
    h.ignore_emphasis = True
    return h.handle(htmlSrc)


def deleteFolder(path: str):
    dirAbsPath = os.path.abspath(path)
    #  print("Attempting to delete: ", dirAbsPath)

    if os.path.isdir(dirAbsPath):
        shutil.rmtree(dirAbsPath)
        # print("Folder Found and Deleted")
    else:
        pass
        # print("Folder Not Found")


def textToValidDir(text: str):
    # Remove characters that are not valid for foldernames and replaces with '_'
    # https://kb.globalscape.com/Knowledgebase/10460/What-are-acceptable-characters-for-WAFSCDP-file-and-folder-names
    return re.sub(r'[^\w &\-\+=,\(\)\{\}]+', r'_', text)


def pageTitleShorten(text: str):
    return re.sub(r'(.{38}).{12,}', r'\1 {truncated}' , text)


def cleanText(text):
    # Replaces non-space whitespace characters with space char
    return re.sub(r'[\r\n\t]', r' ', text)

def extractASVersionFromPath(path):
    # scan path for AS version (e.g. AS410)
    rslt = re.search(r"[\\/](AS\d+)[\\/]", path)
    if rslt:
        return rslt[1]
    else:
        return "AS"

def getDTCode():
    dt = datetime.datetime.now()
    return str(dt.year)[2:] + str(dt.month).zfill(2) + str(dt.day).zfill(2) + str(dt.hour).zfill(2) + str(dt.minute).zfill(2)

def shortenFolder(s):
    shortened = s[:MAX_FOLDER_LEN]
    return re.sub(r'\s*$', r'', shortened)    


def processNode(node, path, orderID, tocPath):

    if (node.tag == "Help"):
        # Only one node (the root node) is tagged Help, so this only runs once at the top level

        if GENERATE_TEXT_ENABLE:
            newFile = os.path.join(path, "_TABLE_OF_CONTENTS.info")
            with open(newFile, 'w+', encoding="utf-8") as n:
                n.write(autoGenNoticeText + '\n')
                n.write("# It contains the top-level table of contents\n")
                n.write("#\n")
                for i,child in enumerate(node):
                    if 'Text' in child.attrib:
                        if child.tag == 'Section':
                            n.write("# SECTION "+ str(i) +": \t" + child.attrib["Text"] + "\n")
                        elif child.tag == 'Page':
                            n.write("# PAGE "+ str(i) +":       \t" + child.attrib["Text"] + "\n")
                n.write("#\n")

        # Recursively process each node's children
        for i,child in enumerate(node):
            processNode(child, path, i, 'Help')


    if (node.tag == "Section" or node.tag == "Page"):

        if {'Text', 'File', 'Id'} <= node.attrib.keys():

            nodeTextClean = cleanText(node.attrib["Text"])
            
            if PRINT_PROCESS_LOCATION:
                print(tocPath + '/' + nodeTextClean)

            if CREATE_FULL_PATH_FILE_LIST:
                # Record all paths and text, for length and trunction analysis
                with open(fullTocPathFileListAbsDir, 'a', encoding="utf-8") as l:
                    l.write(tocPath + '//' + nodeTextClean + '\n')

            if PATH_AND_TEXT_LOG_ENABLE:
                # Record all paths and text, for length and trunction analysis
                with open(pathAndTextDirAbsPath + '//' + PATH_AND_TEXT_LOG_FILENAME, 'a', encoding="utf-8") as l:
                    l.write(tocPath + '\t')
                    l.write(nodeTextClean + '\n')


            if node.tag == "Section": 
                
                # create folder inside path
                newPath = os.path.join(path, shortenFolder(str(orderID) + ' ' + textToValidDir(nodeTextClean)))
                os.mkdir(newPath)
                
                if GENERATE_TEXT_ENABLE:
                    # Create file inside folder with contents of Section Article
                    contentFile = os.path.join(baseDirAbsPath, node.attrib["File"])
                    newFile = os.path.join(newPath, "_SECTION " + textToValidDir(nodeTextClean) + ".info")
                    with open(newFile, 'w+', encoding="utf-8") as n:
                        try:
                            with open(contentFile, 'rb') as f:
                                fileEncoding = UnicodeDammit(f.read()).original_encoding

                            with open(contentFile, 'r', encoding=fileEncoding) as c: 
                                n.write(autoGenNoticeText + '\n')
                                n.write("# It contains the content of the folder's own help article\n")
                                n.write("#\n")
                                n.write("# Table of Contents path: "  + tocPath + "//\n")
                                n.write("# ContentFile:            " + "file:///" + os.path.abspath(contentFile) + "\n")
                                n.write("# GUID:                   " + node.attrib["Id"] + "\n")
                                n.write("#\n")
                                for i,child in enumerate(node):
                                    if 'Text' in child.attrib:
                                        if child.tag == 'Section':
                                            n.write("# SUBSECTION "+ str(i) +": \t" + child.attrib["Text"] + "\n")
                                        elif child.tag == 'Page':
                                            n.write("# PAGE "+ str(i) +":       \t" + child.attrib["Text"] + "\n")
                                n.write("#\n")
                                n.write(parse(c.read()))
                        except Exception as e:
                            handleError("UNABLE TO OPEN FILE: <" + contentFile + "> for TOC doc <" + tocPath + nodeTextClean + '>, ' + str(e))

                # Recursively process each node's children (this is where the magic happens!)
                for i,child in enumerate(node):
                    processNode(child, newPath, i, tocPath + '//' + nodeTextClean)


            if node.tag == "Page":
                
                if GENERATE_TEXT_ENABLE:
                    contentFile = os.path.join(baseDirAbsPath, node.attrib["File"])
                    newFile = os.path.join(path, str(orderID) + ' ' + textToValidDir(pageTitleShorten(nodeTextClean)) + ".txt")
                    with open(newFile, 'w+', encoding="utf-8") as n:
                        try:
                            with open(contentFile, 'rb') as f:
                                fileEncoding = UnicodeDammit(f.read()).original_encoding

                            with open(contentFile, 'r', encoding=fileEncoding) as c: 
                                n.write(autoGenNoticeText + '\n')
                                n.write("#\n")
                                n.write("# Table of Contents path: "  + tocPath + "//\n")
                                n.write("# ContentFile:            " + "file:///" + os.path.abspath(contentFile) + "\n")
                                n.write("# GUID:                   " + node.attrib["Id"] + "\n")
                                n.write("#\n")
                                n.write(parse(c.read()))
                        except Exception as e:
                            handleError("UNABLE TO OPEN FILE: <" + contentFile + "> for TOC doc <" + tocPath + '/' +  nodeTextClean + '>, ' + str(e))

        else:
            handleError("ERROR: Section or Page did not have required attributes")

    else:
        # node is tagged with neither Page nor Section
        pass


def cleanPreviousFiles(outputDirAbsPath):
    
    # Delete previous implementation
    # print("Deleting existing folder of textified text...")
    deleteFolder(outputDirAbsPath)
    os.makedirs(outputDirAbsPath, exist_ok=True)

    try:
        os.remove(PATH_AND_TEXT_LOG_FILENAME)
    except OSError:
        pass

    try:
        os.remove(ERROR_LOG_FILENAME)
    except OSError:
        pass

    try:
        os.remove(FULL_TOC_PATH_FILE_LIST_FILENAME)
    except OSError:
        pass


if __name__=="__main__":
    print("Executing textify main...")

    # Prompt user to select Help Data Content XML, with a default
    tioWrapUserSelectedContentXml = askopenfile(    title='Select Help content xml file...', 
                                                    initialdir = DEFAULT_DATA_DIR, 
                                                    initialfile=DEFAULT_DATA_FILE, 
                                                    filetypes=[("datafile", "*.xml")]) # shows dialog box and return the file as TextIOWrapper object
    pfContentXml = os.path.abspath(tioWrapUserSelectedContentXml.name)
    print("User-selected content XML file:", pfContentXml)
    baseDirAbsPath = os.path.dirname(pfContentXml)
    outputDirAbsPath = os.path.abspath(OUTPUT_DIR + extractASVersionFromPath(baseDirAbsPath) + OUTPUT_DIR_SUFFIX + getDTCode())
    cleanPreviousFiles(outputDirAbsPath)

    if PATH_AND_TEXT_LOG_ENABLE:
        pathAndTextDirAbsPath = os.path.abspath(outputDirAbsPath + '//' + PATH_AND_TEXT_LOG_DIR)
        os.makedirs(pathAndTextDirAbsPath)

    if FULL_TOC_PATH_FILE_LIST_FILENAME:
        fullTocPathFileListAbsDir = os.path.abspath(outputDirAbsPath +'//' + FULL_TOC_PATH_FILE_LIST_FILENAME)
    
    errorLogAbsDir = os.path.abspath(outputDirAbsPath +'//' + ERROR_LOG_FILENAME)

    # Parse Tree!
    tree = ET.parse(pfContentXml)
    root = tree.getroot()

    # Process Each node (each node is either a Help, a Section, or a Page)
    processNode(root, outputDirAbsPath, 0, '')

    print("TEXTIFICATION COMPLETE")



