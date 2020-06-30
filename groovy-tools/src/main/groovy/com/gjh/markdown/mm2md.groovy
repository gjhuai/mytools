package com.gjh.markdown
//package my.groovy

import groovy.xml.XmlSlurper

def recurseRead(outline, level){
    if (outline.@type != 'note'){
        println("#"*level + " ${outline.@text}\n")
    } else {
        println("${outline.@text}\n")
    }

    outline.outline.find{
        recurseRead(it, level+1)
    }
}

def mmFile
if (args.size() ==1 )  {
    mmFile = args[0]
} else {
    mmFile = '刷单.xml'
}

def xmlSource = new File(mmFile)
def root= new XmlSlurper().parse(xmlSource)

// 二级
root.body.outline.outline.find{
    recurseRead(it, 1)
}

