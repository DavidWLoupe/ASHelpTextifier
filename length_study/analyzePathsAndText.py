import os
import csv

PATH_TO_FILE = "./process runs//all 221110_2200//"
CSVFILENAME = "paths_and_text.csv"





pfCsvToAnalyze = os.path.join(PATH_TO_FILE, CSVFILENAME)
# print(pfCsvToAnalyze)

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
        
        pathLen = int(row[0])
        filenameLen = int(row[2])

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
        

print("Largest Path:\t", maxPathLen, largestPath)
print("\n")
print("Largest Filename:\t", maxFilenameLen, largestFilename)
print("\n")
print("Largest PathFilename:\t", maxPathFilenameLen, largestPathFilename)




