# coding=gbk 
import re

path = "2.txt"

marks = ['。', '？']

text = ""

with open(path, "r") as myfile:
    lines = myfile.readlines()
    
    inParagraph = False
    i = 0
    print(len(lines))
    while i < len(lines):
        line = lines[i]
        #pattern = re.compile(r'第.*章')
        #if pattern.search(line):
        #    text = text + line
        #    i += 1
        #    inParagraph = False
        #    continue

        #print(i)
        if inParagraph:
            cleanLine = line.strip()
            text = text + cleanLine
            i += 1
            #line = lines[i]
            continue
        else:
            cleanLine = line.rstrip()
            text = text + cleanLine
            if len(cleanLine)>0 and not cleanLine[-1] in marks:
                inParagraph = True
            
open("3.txt", "w").write(text)
