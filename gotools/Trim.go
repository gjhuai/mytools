package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/axgle/mahonia"
)


func checkIsEnd(line string, endStr []rune) bool{
    var isEnd = false
    for _, c := range endStr {
        if strings.HasSuffix(line, string(c)) {
            isEnd = true
            break;
        }
    }

    if (strings.HasSuffix(line, "章") || strings.HasSuffix(line, "楔子")){
		isEnd = true
    }
    
    return isEnd
}

func clean(text string) string{
	reg := regexp.MustCompile(`#\w{3};`)
	text = reg.ReplaceAllString(text, "")
	reg = regexp.MustCompile(`&\w{3};`)
	text = reg.ReplaceAllString(text, "")
	text = strings.Replace(text, "</br>", "", -1)
	text = strings.Replace(text, "amp;", "", -1)
	text = strings.Replace(text, "&hellip;", "…", -1)
	text = strings.Replace(text, "&quot;", "“", -1)
	reg = regexp.MustCompile(`#x\w{4};`)
	text = reg.ReplaceAllString(text, "")

	reg = regexp.MustCompile(`\d{4}-\d{1,2}-\d{1,2}`)
	text = reg.ReplaceAllString(text, "\n")

	reg = regexp.MustCompile(`\d{4}年\d{1,2}月\d{1,2}日`)
	text = reg.ReplaceAllString(text, "\n")

	reg = regexp.MustCompile(`(第\S{1,5}章)`)
	text = reg.ReplaceAllString(text, "\n${1}")
    return text
}

func main() {

	// if len(os.Args)<1{
	// 	fmt.Println("No Input File!!!!!")
	//     return
	// }
	filePath := os.Args[0]
	filePath = "中文2.txt"

	endStr := []rune(".。!！?？」》节章”")

	isEnd := true
	upLineIsEnd := false
	text := ""

	stripEnd := regexp.MustCompile(`(\S*)\s*`)
	stripBegin := regexp.MustCompile(`\s*(\S*)`)

	fi, _ := os.Open(filePath)
   	defer fi.Close()
	// 把原来ANSI格式的文本文件里的字符，用gbk进行解码。
   	decoder := mahonia.NewDecoder("gb18030") 
   	f, _ := ioutil.ReadAll(decoder.NewReader(fi))

	contents := string(f)
	lines := strings.Split(contents, "\n")
	for _, line := range lines {
		if line = stripEnd.ReplaceAllString(line, "${1}"); len(line) == 0 {
			continue
		}
		isEnd = checkIsEnd(line, endStr)
		// fmt.Print(isEnd)

		if upLineIsEnd==false {
			line = stripBegin.ReplaceAllString(line, "${1}")
		}
		text = text + line

		if (isEnd){
			text = text + "\r\n\r\n"
		}
		upLineIsEnd = isEnd
		// fmt.Println(line)
	}
	text = clean(text)
	fileName := filePath[0:strings.LastIndex(filePath, ".")]+"_.txt"
	ioutil.WriteFile(fileName, []byte(text), 0777)
	fmt.Println("输出：", fileName)
	
    time.Sleep(time.Duration(2) * time.Second)
}