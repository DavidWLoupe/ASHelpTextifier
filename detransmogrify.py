from tkinter.filedialog import askdirectory
import os
import shutil
import xml.etree.ElementTree as ET
import re

DEFAULT_DATA_DIR = "C:\\BrAutomation\\AS410\\Help-en\\Data"
CONTENT_FILENAME = "brhelpcontent.xml"
# CONTENT_FILENAME = "brhelpcontent_tiny.xml"
# CONTENT_FILENAME = "brhelpcontent_small.xml"
OUTPUT_DIR = "BrHelpDetransmogrified"


baseDirAbsPath = DEFAULT_DATA_DIR

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

def processNode(node, path, orderID, tocPath):


    if 'Text' in node.attrib:
        print(node.attrib['Text'])
    else:
        print("<no text ", node.tag, ">")
    


    if (node.tag == "Section" or node.tag == "Page"):

        if {'Text', 'File', 'Id'} <= node.attrib.keys():
            
            if node.tag == "Section": 
                
                # create folder inside path
                newPath = os.path.join(path, str(orderID))
                os.mkdir(newPath)
                
                # Create file inside folder with contents of Section Article
                contentFile = os.path.join(baseDirAbsPath, node.attrib["File"])
                newFile = os.path.join(newPath, "_SECTION " + textToValidDir(node.attrib["Text"]) + ".txt")
                with open(newFile, 'w+') as n:
                    with open(contentFile) as c: 
                        n.write(c.read())
                
                # Create file with Table of Contents path as content (since it cannot be in folder names due to path length limits)
                tocFile = os.path.join(newPath, "_TOC.txt")
                with open(tocFile, 'w+') as t:
                    t.write("Table of Contents path:\n")
                    t.write(tocPath + '/\n\n')
                    t.write("Section Name:\n" + node.attrib["Text"] + "\n")

                # Recursively process each node's children
                for i,child in enumerate(node):
                    processNode(child, newPath, i, tocPath + '/' + node.attrib["Text"])


            if node.tag == "Page":

                contentFile = os.path.join(baseDirAbsPath, node.attrib["File"])
                newFile = os.path.join(path, str(orderID) + ' ' + textToValidDir(node.attrib["Text"]) + ".txt")
                with open(newFile, 'w+') as n:
                    with open(contentFile) as c: 
                        n.write(c.read())


        else:
            print("ERROR: Section or Page did not have required attributes")


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
    outputDirAbsPath = os.path.abspath(OUTPUT_DIR)
    deleteFolder(outputDirAbsPath)
    os.mkdir(outputDirAbsPath)


    # Process 
    # Note: root node's children are top-level help folders
    for i,topLevelFolderNode in enumerate(root):
        processNode(topLevelFolderNode, outputDirAbsPath, i, '')





