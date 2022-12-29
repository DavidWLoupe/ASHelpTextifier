import os
import csv

PATH_TO_FILE = "./process runs//all 221210_1200//"
CSVFILENAME = "paths_and_text.csv"
# CSVFILENAME = "paths_and_text short.csv"





pfCsvToAnalyze = os.path.join(PATH_TO_FILE, CSVFILENAME)
# print(pfCsvToAnalyze)

maxPathDepth = 0
deepestPath = ''

maxPathLen = 0
largestPath = ''

maxFilenameLen = 0
largestFilename = ''

maxPathFilenameLen = 0
largestPathFilename = ''


with open(pfCsvToAnalyze, newline='') as f:
    rows = csv.reader(f, delimiter='\t')

    for row in rows:
        
        # print(row)
        
        # for c in row[1]:
        #     if c == '/':
        #         slashCount += 1
        folders = row[1].split("//")

        # print(folders)

        #pathDepth = sum(map(lambda x : 1 if '/' in x else 0, row[1]))
        pathDepth = len(folders)

        pathLen = 0
        for f in folders:
            pathLen += len(f)
        filenameLen = int(row[2])


        # Deepest Path
        if pathDepth > maxPathDepth:
            maxPathDepth = pathDepth
            deepestPath = row[1]

        # Largest Path
        if pathLen > maxPathLen:
            maxPathLen = pathLen
            largestPath = row[1]

        # Largest filename
        if filenameLen > maxFilenameLen:
            maxFilenameLen = filenameLen
            largestFilename = row[3]

        # Largest pathfilename
        if pathLen + filenameLen > maxPathFilenameLen:
            maxPathFilenameLen = pathLen + 1 + filenameLen
            largestPathFilename = row[1] + '/' + row[3]

        # print(row)
        

print("Deepest Path:\t", maxPathDepth, deepestPath)
print("\n")
print("Largest Path:\t", maxPathLen, largestPath)
print("\n")
print("Largest Filename:\t", maxFilenameLen, largestFilename)
print("\n")
print("Largest PathFilename:\t", maxPathFilenameLen, largestPathFilename)




