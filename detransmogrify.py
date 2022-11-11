from tkinter.filedialog import askdirectory
import os
import shutil
import xml.etree.ElementTree as ET
import re
import html2text

DEFAULT_DATA_DIR = "C:\\BrAutomation\\AS410\\Help-en\\Data"
# CONTENT_FILENAME = "brhelpcontent.xml"
# CONTENT_FILENAME = "brhelpcontent_tiny.xml"
CONTENT_FILENAME = "brhelpcontent_small.xml"
OUTPUT_DIR = "BrHelpDetransmogrified"
PATH_AND_FILE_LOG = "paths_and_text.csv"

baseDirAbsPath = DEFAULT_DATA_DIR


try:
    os.remove(PATH_AND_FILE_LOG)
except OSError:
    pass


def handleError(error):
    # print(error)
    with open("errors.txt", 'a') as e:
        e.write(error + '\n')

# Ref: https://github.com/Alir3z4/html2text/blob/master/docs/usage.md
def parse(htmlSrc: str):
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
    # Remove characters that are not a-z A-Z 0-9, '_'
    # https://kb.globalscape.com/Knowledgebase/10460/What-are-acceptable-characters-for-WAFSCDP-file-and-folder-names
    return re.sub(r'[^\w &\-\+=,\(\)\{\}]+', r'_', text)


def pageTitleShorten(text: str):

    # Handle error types (e.g. "-10280038: asdf asdf adsf sadf asdf adsf asdf asdf asd asdf sadf")
    modified = re.sub(r'(-?\d{8,}:.{10}).{10,}', r'\1 {truncated}' , text)
    
    
    # Limit file length to 50
    if len(modified) > 50:
        modified = modified[0:50]

    return modified


def cleanText(text):
    # Replaces non-space whitespace characters with space char
    return re.sub(r'[\r\n\t]', r' ', text)


def processNode(node, path, orderID, tocPath):

    # Print Path to function
    if 'Text' in node.attrib:
        print(tocPath + '/' + node.attrib['Text'])
    else:
        print(tocPath + '/' + "<no Text ", node.tag, ">")


    if (node.tag == "Section" or node.tag == "Page"):



        if {'Text', 'File', 'Id'} <= node.attrib.keys():

            nodeTextClean = cleanText(node.attrib["Text"])

            # Record all paths and text, for length and trunction analysis
            with open(PATH_AND_FILE_LOG, 'a', encoding="utf-8") as l:
                l.write(str(len(tocPath)) + '\t')
                l.write(tocPath + '\t')
                l.write(str(len(nodeTextClean)) + '\t')
                l.write(nodeTextClean + '\n')


            if node.tag == "Section": 
                
                # create folder inside path
                newPath = os.path.join(path, str(orderID))
                os.mkdir(newPath)
                
                # Create file inside folder with contents of Section Article
                contentFile = os.path.join(baseDirAbsPath, node.attrib["File"])
                newFile = os.path.join(newPath, "_SECTION " + textToValidDir(nodeTextClean) + ".info")
                with open(newFile, 'w+', encoding="utf-8") as n:
                    try:
                        with open(contentFile, 'rb') as f:
                            fileEncoding = UnicodeDammit(f.read()).original_encoding

                        with open(contentFile, 'r', encoding=fileEncoding) as c: 
                            n.write("# NOTE: THIS HEADER AUTO-GENERATED BY B&R HELP DETRANSMOGRIFIER\n")
                            n.write("# It contains the content of the folder's own help article\n#\n")
                            n.write(parse(c.read()))
                    except Exception as e:
                        handleError("UNABLE TO OPEN FILE: <" + contentFile + "> for TOC doc <" + tocPath + nodeTextClean + '>, ' + str(e))
                
                # Create file with Table of Contents path as content (since it cannot be in folder names due to path length limits)
                tocFile = os.path.join(newPath, "_TOC.info")
                with open(tocFile, 'w+', encoding="utf-8") as t:
                    t.write("# NOTE: THIS FILE AUTO-GENERATED BY B&R HELP DETRANSMOGRIFIER\n")
                    t.write("# It contains information about the current Help directory\n#\n")
                    t.write("# Table of Contents path:\n")
                    t.write("# " + tocPath + '/\n#\n')
                    t.write("# Section Name:\n")
                    t.write("# " + nodeTextClean + "\n#\n")
                    t.write("# Pages and subsections:\n")
                    for i,child in enumerate(node):
                        if 'Text' in child.attrib:
                            if child.tag == 'Section':
                                t.write("# SUBSECTION "+ str(i) +": \t" + child.attrib["Text"] + "\n")
                            elif child.tag == 'Page':
                                t.write("# PAGE "+ str(i) +":       \t" + child.attrib["Text"] + "\n")

                # Recursively process each node's children (this is where the magic happens)
                for i,child in enumerate(node):
                    processNode(child, newPath, i, tocPath + '/' + nodeTextClean)


            if node.tag == "Page":

                contentFile = os.path.join(baseDirAbsPath, node.attrib["File"])
                newFile = os.path.join(path, str(orderID) + ' ' + textToValidDir(pageTitleShorten(nodeTextClean)) + ".txt")
                with open(newFile, 'w+', encoding="utf-8") as n:
                    try:
                        with open(contentFile, 'rb') as f:
                            fileEncoding = UnicodeDammit(f.read()).original_encoding

                        with open(contentFile, 'r', encoding=fileEncoding) as c: 
                            n.write("# NOTE: THIS HEADER AUTO-GENERATED BY B&R HELP DETRANSMOGRIFIER\n# \n")
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



if __name__=="__main__":
    print("Executing detransmogrify main...")

    # Prompt user to select Help Data directory, with a default
    userSelectedPath = askdirectory(title='Select Help Data folder containing brhelpcontent.xml', initialdir=DEFAULT_DATA_DIR) # shows dialog box and return the path
    print("User selected path:", userSelectedPath) 


    # Formalize path and file with os.path
    baseDirAbsPath = os.path.abspath(userSelectedPath)
    pfContentXml = os.path.join(baseDirAbsPath, CONTENT_FILENAME)
    print(pfContentXml)

    
    # Parse Tree!
    tree = ET.parse(pfContentXml)
    root = tree.getroot()

    # Delete previous implementation
    print("Deleting existing folder of detransmogrified text...")
    outputDirAbsPath = os.path.abspath(OUTPUT_DIR)
    deleteFolder(outputDirAbsPath)
    os.mkdir(outputDirAbsPath)

    # Process Each node (each node is either a Section or a Page)
    # Note: root node's children are top-level folders in Help
    for i,topLevelFolderNode in enumerate(root):
        processNode(topLevelFolderNode, outputDirAbsPath, i, 'Help')

    print("DETRANSMOGRIFICATION COMPLETE")



