package org.tubez.picker;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.xpath.XPath;
import javax.xml.xpath.XPathConstants;
import javax.xml.xpath.XPathExpression;
import javax.xml.xpath.XPathExpressionException;
import javax.xml.xpath.XPathFactory;

import org.w3c.dom.Document;
import org.w3c.dom.NamedNodeMap;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

public class PickLatest {
	private final static Map<String, String> posMap = new HashMap<>();

    public static void main(String[] args) {
    	pick();

    }

    public static void pick() {
		resetPos();
    	
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true);
        DocumentBuilder builder;
        Document doc = null;
        try {
            builder = factory.newDocumentBuilder();
            doc = builder.parse("latest.xml");

            // Create XPathFactory object
            XPathFactory xpathFactory = XPathFactory.newInstance();

            // Create XPath object
            XPath xpath = xpathFactory.newXPath();

            sendLatestChapter(doc, xpath);
        } catch (ParserConfigurationException | SAXException | IOException e) {
            e.printStackTrace();
        }
	}
    

    private static void sendLatestChapter(Document doc, XPath xpath) {
        try {
            //create XPathExpression object
            XPathExpression expr = xpath.compile("/books/book");
            //evaluate expression result on XML document
            NodeList nodes = (NodeList) expr.evaluate(doc, XPathConstants.NODESET);
            for (int i = 0; i < nodes.getLength(); i++){
            	Node book = nodes.item(i);
            	NamedNodeMap attrs = book.getAttributes();
            	String name = attrs.getNamedItem("name").getNodeValue();
            	String link = attrs.getNamedItem("link").getNodeValue();
            	Node p = attrs.getNamedItem("prefix");
            	String prefix = p==null?link:p.getNodeValue();
            	// 获取上次章节位置pos
            	String pos = posMap.get(name);
            	// 得到最新章节
            	String[] result = getLastestChapter(link, prefix, pos);
            	String content = result[0];
            	String newPos = result[1];

            	try {
            		if (content.trim().length()!=0 && newPos.compareTo(newPos)>0){
            			Mailman.sendQQMailFrom189(name, content);
            			writePos(name, newPos);
            			System.out.println("已发送："+name);
            		} else {            			
            			System.out.println("没有发现新章节："+name);
            		}
				} catch (Exception e) {
					e.printStackTrace();
				}
            }
        } catch (XPathExpressionException e) {
            e.printStackTrace();
        }
    }
    
    private static String[] getLastestChapter(String link, String prefix, String pos){
    	NovelPicker picker = new NovelPicker();
		Map<String, String> urlMap = picker.getChapters(link, prefix);
		String newPos = pos;
		StringBuilder latestChapter = new StringBuilder();
		
		for (Map.Entry<String, String> kv : urlMap.entrySet()){
			String chapterLink = kv.getValue();
			int start = chapterLink.lastIndexOf('/');
			int end = chapterLink.lastIndexOf('.');
			if (start>end){
				continue;
			}
			String idx = chapterLink.substring(start+1, end);
			if (idx.length()>=pos.length() && idx.compareTo(pos)>0){
				String content = picker.getSingleChapterText(kv.getKey(), chapterLink, new String[]{});
				latestChapter.append(content);
				newPos = idx;
			}
		}
		return new String[]{latestChapter.toString(), newPos};
    }
    
    private static void resetPos(){
    	List<String> lines;
		try {
			lines = Files.readAllLines(Paths.get("pos.txt"));
		} catch (IOException e) {
			System.out.println("pos.txt文件打开失败");
			throw new RuntimeException(e);
		}
    	for (String line : lines){
    		String[] sArr = line.split("=");
    		posMap.put(sArr[0], sArr[1]);
    	}
    }
    
    static void writePos(String name, String newPos){
    	List<String> lines;
    	Path path = Paths.get("pos.txt");
		try {
			lines = Files.readAllLines(Paths.get("pos.txt"));
			List<String> newLines = new ArrayList<>(lines.size());
			for (String line :lines){
				if (line.startsWith(name+"=")){
					line = name+"="+newPos;					
				}
				newLines.add(line);
			}
			Files.write(path, newLines, StandardOpenOption.TRUNCATE_EXISTING);
		} catch (IOException e) {
			System.out.println("pos.txt文件打开失败");
			throw new RuntimeException(e);
		}
    }

}
