package com.gjh.novel

if (this.args.size() <1 )  {
    println "No Input File!!!!!"
    return
}

def filePath = this.args[0]

//def filePath = 'd:/2.txt'
def fileName = filePath[0..filePath.lastIndexOf('.')-1]

def endStr = ".。!！?？」》节”".toCharArray().collect { String.valueOf(it)}

def lines = new File(filePath).readLines("GBK")

def text = new StringBuilder()
def isEnd = true
def upLineIsEnd = false

def stripEnd = ~/(\S+)\s*/
def stripBegin = ~/\s*(\S+)/
for (int i=0;i<lines.size();i++){
    String line = lines[i]
    if (!line || line.isAllWhitespace()){
        continue
    }
	line = line.replaceAll(stripEnd, '$1')
    isEnd = checkIsEnd(line, endStr)

    if (upLineIsEnd==false) {
		line = line.replaceAll(stripBegin, '$1')
    }
    text.append(line)

    if (isEnd){
        text.append("\r\n\r\n")
    }

    upLineIsEnd = isEnd
}
text = clean(text.toString())
new File(fileName+"_.txt").write(text.toString())


def checkIsEnd(String line, endStr){
    def isEnd = false
    for (String c : endStr ){
        if (line.endsWith(c)){
            isEnd = true
            break;
        }
    }

    if (line.contains("章") || line.contains("楔子")){
		isEnd = true
    }
    
    return isEnd
}

String clean(String text){
	text = text.replaceAll(/#\w{3};/, '')
	text = text.replaceAll(/&\w{3};/, '')
	text = text.replaceAll("</br>", '')
	text = text.replaceAll("amp;", '')
	text = text.replaceAll("&hellip;", '…')
	text = text.replaceAll("&quot;", '“')
	text = text.replaceAll(/#x\w{4};/, '')
	text = text.replaceAll(/\d{4}-\d{1,2}-\d{1,2}/, '\n')
	text = text.replaceAll(/\d{4}年\d{1,2}月\d{1,2}日/, '\n')
	text = text.replaceAll(/(第\S{1,5}章)/, '\n$1')
    return text
}