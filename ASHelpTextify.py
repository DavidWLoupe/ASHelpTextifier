from tkinter.filedialog import askdirectory
import os
import shutil
import xml.etree.ElementTree as ET
import re
import html2text
from bs4 import UnicodeDammit

DEFAULT_DATA_DIR = "C:\\BrAutomation\\AS410\\Help-en\\Data"
CONTENT_FILENAME = "brhelpcontent.xml"
# CONTENT_FILENAME = "brhelpcontent_tiny.xml"
# CONTENT_FILENAME = "brhelpcontent_small.xml"
OUTPUT_DIR_SUFFIX = "Help_Textified"
PATH_AND_TEXT_LOG_ENABLE = False
PATH_AND_TEXT_LOG_FILENAME = "length_study/paths_and_text.csv"
PRINT_PROCESS_LOCATION = True
CREATE_FULL_PATH_FILE_LIST = True
FULL_TOC_PATH_FILE_LIST_FILENAME = "FullTocPathFileList.info"
ERROR_LOG = "errors.txt"
MAX_FOLDER_LEN = 11

baseDirAbsPath = DEFAULT_DATA_DIR


def handleError(error):
    # print(error)
    with open(ERROR_LOG, 'a', encoding="utf-8") as e:
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
    print(dirAbsPath)

    if os.path.isdir(dirAbsPath):
        shutil.rmtree(dirAbsPath)
        print("Folder Found and Deleted")
    else:
        print("Folder Not Found")


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


def shortenFolder(s):
    shortened = s[:MAX_FOLDER_LEN]
    return re.sub(r'\s*$', r'', shortened)    


def processNode(node, path, orderID, tocPath):


    if (node.tag == "Help"):
        # Only one node (the root node) is tagged Help, so this only runs once at the top level

        if GENERATE_TEXT_ENABLE:
            newFile = os.path.join(path, "_TABLE_OF_CONTENTS.info")
            with open(newFile, 'w+', encoding="utf-8") as n:
                n.write("# NOTE: THIS HEADER AUTO-GENERATED BY AS HELP TEXTIFIER\n")
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
                with open(FULL_TOC_PATH_FILE_LIST_FILENAME, 'a', encoding="utf-8") as l:
                    l.write(tocPath + '//' + nodeTextClean + '\n')

            if PATH_AND_TEXT_LOG_ENABLE:
                # Record all paths and text, for length and trunction analysis
                with open(PATH_AND_TEXT_LOG_FILENAME, 'a', encoding="utf-8") as l:
                    l.write(str(len(tocPath)) + '\t')
                    l.write(tocPath + '\t')
                    l.write(str(len(nodeTextClean)) + '\t')
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
                                n.write("# NOTE: THIS HEADER AUTO-GENERATED BY AS HELP TEXTIFIER\n")
                                n.write("# It contains the content of the folder's own help article\n")
                                n.write("#\n")
                                n.write("# Table of Contents path: "  + tocPath + "/\n")
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
                                n.write("# NOTE: THIS HEADER AUTO-GENERATED BY AS HELP TEXTIFIER\n")
                                n.write("#\n")
                                n.write("# Table of Contents path: "  + tocPath + "/\n")
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
    print("Deleting existing folder of textified text...")
    deleteFolder(outputDirAbsPath)
    os.mkdir(outputDirAbsPath)

    try:
        os.remove(PATH_AND_TEXT_LOG_FILENAME)
    except OSError:
        pass

    try:
        os.remove(ERROR_LOG)
    except OSError:
        pass

    try:
        os.remove(FULL_TOC_PATH_FILE_LIST_FILENAME)
    except OSError:
        pass


if __name__=="__main__":
    print("Executing textify main...")

    # Prompt user to select Help Data directory, with a default
    userSelectedPath = askdirectory(title='Select Help Data folder containing brhelpcontent.xml', initialdir=DEFAULT_DATA_DIR) # shows dialog box and return the path
    print("User selected path:", userSelectedPath) 

    # Formalize path and file with os.path
    baseDirAbsPath = os.path.abspath(userSelectedPath)
    pfContentXml = os.path.join(baseDirAbsPath, CONTENT_FILENAME)
    outputDirAbsPath = os.path.abspath(extractASVersionFromPath(baseDirAbsPath) + OUTPUT_DIR_SUFFIX)
    print(pfContentXml)

    cleanPreviousFiles(outputDirAbsPath)

    # Parse Tree!
    tree = ET.parse(pfContentXml)
    root = tree.getroot()

    # Process Each node (each node is either a Help, a Section, or a Page)
    processNode(root, outputDirAbsPath, 0, '')

    print("TEXTIFICATION COMPLETE")



