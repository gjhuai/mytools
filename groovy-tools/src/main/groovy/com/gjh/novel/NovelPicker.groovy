package com.gjh.novel

import org.w3c.dom.NamedNodeMap
import org.w3c.dom.Node
import org.w3c.dom.NodeList

import javax.mail.Message
import javax.mail.MessagingException
import javax.mail.Session
import javax.mail.Transport
import javax.mail.PasswordAuthentication
import javax.mail.internet.AddressException
import javax.mail.internet.InternetAddress
import javax.mail.internet.MimeMessage
import javax.xml.parsers.DocumentBuilder
import javax.xml.parsers.DocumentBuilderFactory
import javax.xml.xpath.XPath
import javax.xml.xpath.XPathConstants
import javax.xml.xpath.XPathExpression
import javax.xml.xpath.XPathExpressionException
import javax.xml.xpath.XPathFactory
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths
import java.nio.file.StandardOpenOption
import java.util.logging.Logger;
import java.util.regex.Pattern;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

@GrabResolver(name = 'aliyun', root = 'https://maven.aliyun.com/repository/public')
@Grab('javax.mail:mail:1.5.0-b01')
@Grab("org.jsoup:jsoup:1.9.2")

/**
 * 
 * <pre>
 * Title: 网页抓取程序
 * Description: 
 * 		根据不同的网页结构 需要修改getElement方法实现解析
 * </pre>
 * 
 * @author GJH
 */
class Picker {
	private Logger logger = Logger.getLogger(Picker.class.getCanonicalName());
	
	/**
	 * 抓取总数
	 */
	static int totalSum = 1;
	/**
	 * 获取失败记录数
	 */
	static int failureSum = 0;

	/**
	 * 获取所有章节
	 * @return Map<String,String> <章节名, url>
	 */
	Map<String, String> getChapters(String catalogUrl, String urlPrefix) {
		// 获取目录所在页面元素
		Document doc = getHtmlDoc(catalogUrl);
		
		int idx = catalogUrl.indexOf("/", catalogUrl.indexOf("//") + 2);
		
		// 抓取站点url
		String siteUrl = catalogUrl.substring(0, idx);
		// 文字根url
		String subUrl = catalogUrl.substring(idx);
		
				
		Elements links = doc.select("a[href]");
		Map<String, String> emap = new LinkedHashMap<String, String>();

		for (Element link : links) {
			String href = link.attr("href").trim();
			if (href.contains("javascript")) {
				continue;
			}
			if (href.startsWith("/")) { // e.g. /2546/89898.html, 从根路径开始
				href = siteUrl + href;
			} else if (!href.startsWith("http")) {	// e.g. 2546/89898.html, 从当前页面相对开始
				href = siteUrl + subUrl.substring(0, subUrl.lastIndexOf('/')) + "/" + href;
			}
			if (!href.startsWith(urlPrefix)) {
				continue;
			}
			String chapterName = link.text().trim();
			emap.put(chapterName, href);
		}
		System.out.println("URL Total：" + emap.size());
		return emap;
	}
	

	/**
	 * 获取Html Document
	 */
	private Document getHtmlDoc(String url) {
		Document doc = null;
		try {
			doc = Jsoup.connect(url).timeout(600000)
					.userAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:23.0) Gecko/20100101 Firefox/23.0")
					.get();
		} catch (IOException e) {
			logger.severe("无法连接到"+url+" --> "+e.getLocalizedMessage());
			throw new RuntimeException(e);
		}
		return doc;
	}

	/**
	 * 文件缓存
	 * 
	 * @param filePath
	 *            路径
	 * @param chapterMap
	 *            写入内容
	 * @param encoding
	 *            文件编码
	 * @param shiftWord
	 *            屏蔽关键字
	 */
	void pickAllNovelText(String filePath, Map<String, String> chapterMap, String encoding, String[] shiftWord) {
		try {
			File file = new java.io.File(filePath);
			if (!file.exists()) {
				file.createNewFile();
			}
			if (file.isFile() && file.exists()) {
				OutputStreamWriter write = new OutputStreamWriter(new FileOutputStream(file), encoding);
				BufferedWriter bufferedWriter = new BufferedWriter(write);

				String content = "";
				// 遍历Map
				for (Map.Entry<String, String> a : chapterMap.entrySet()) {
					String aName = a.getKey();
					content = this.getSingleChapterText(aName, a.getValue(), shiftWord);
					bufferedWriter.write(aName);
					bufferedWriter.newLine();
					bufferedWriter.write(content);
					bufferedWriter.newLine();
				}
				bufferedWriter.flush();
				write.close();

			} else {
				System.out.println("file error");
			}
		} catch (Exception e) {
			System.out.println("writeFile error");
			e.printStackTrace();
		}
	}

	/**
	 * catch内容
	 */
	String getSingleChapterText(String chapterName, String chapterUrl, String[] shiftWord) {
		Element body = this.getHtmlDoc(chapterUrl).body();

//		Elements brList = body.select("br");
//		for (Element br : brList) {
//			br.replaceWith(new TextNode("BRBR", ""));
//		}
//		String contents = body.text();
//		contents = contents.replaceAll("BRBR", "\n");
		String html = body.html();
		Pattern pScript = Pattern.compile("<script.+?</script>", Pattern.DOTALL | Pattern.CASE_INSENSITIVE);
		html = pScript.matcher(html).replaceAll("");
		
		html = html.replaceAll("<.+?>", "");
		html = html.replaceAll("&nbsp;", " ");
//		String contents = html;
		String contents = html.replaceAll("\\s{60,}", "");

		// 屏蔽关键词
		for (String str : shiftWord) {
			contents = contents.replaceAll(str, "");
		}
		// 抓取内容长度大于100 即成功
		if (contents.length() > 100) {
			System.out.println("Succeed - " + totalSum + chapterName);
		} else {
			System.out.println("* Failure - " + totalSum + chapterName);
			failureSum++;
		}
		totalSum++;
		return contents;
	}


	static void pickAll() {
		long startTime = System.currentTimeMillis();

		ResourceBundle proMap = ResourceBundle.getBundle("novel");

		// 目录页
		String catalogUrl = proMap.getString("catalogUrl");
		// 各章节的前缀
		String urlPrefix = proMap.getString("urlPrefix");
		// 保存路径
		String filePath = proMap.getString("filePath");
		// 屏蔽关键字
		String[] shiftWord = proMap.getString("shiftWord").split("&");

		// 解析目录所在页面元素 获取所有章节url
		Picker picker = new Picker();
		Map<String, String> urlMap = picker.getChapters(catalogUrl, urlPrefix);
		// 通过所有章节url 获取每个章节内容并保存
		picker.pickAllNovelText(filePath, urlMap, "UTF-8", shiftWord);

		long endTime = System.currentTimeMillis();

		System.out.println("The End ! totalSum:" + (Picker.totalSum - 1) + " failureSum:" + Picker.failureSum);
		System.out.println("run time: " + (endTime - startTime) / 6000 + "s");
	}

}


class MailSender {
	Session session = null;

	public MailSender(String smtpHost, String sslPort, String username, String pwd){
		Properties props = new Properties();

		props.put("mail.smtp.host", smtpHost);
//		props.put("mail.smtp.socketFactory.port", sslPort);
//		props.put("mail.smtp.socketFactory.class", "javax.net.ssl.SSLSocketFactory");
		props.put("mail.smtp.auth", "true");
		props.put("mail.smtp.port", sslPort);

		session = Session.getDefaultInstance(props,
				new javax.mail.Authenticator() {
					protected PasswordAuthentication getPasswordAuthentication() {
						return new PasswordAuthentication(username, pwd);
					}
				});
		//session.setDebug(true);
	}

	public void send(String from, String to, String subject, String content){
		try {
			Message message = new MimeMessage(session);
			message.setFrom(new InternetAddress(from));
			message.setRecipients(Message.RecipientType.TO, InternetAddress.parse(to));
			message.setSubject(subject);
			message.setText(content);

			Transport.send(message);

			System.out.println("Done");

		} catch (MessagingException e) {
			throw new RuntimeException(e);
		}
	}

	static void main(String[] args) {
		sendQQMailFrom189("Testing Subject", "Dear Mail Crawler," + "\n\n No spam to my email, please!");
	}

	/**
	 * 含敏感信息就不能发出
	 * @param subject
	 * @param content
	 */
	public static void sendQQMailFrom189(String subject, String content) {
		new MailSender("smtp.189.cn", "25", "18109032120", "guanok77")
				.send("18109032120@189.cn", "gjhuai@qq.com", subject, content);
	}

	public static void sendQQMailFromJdgm(String subject, String content) throws AddressException, MessagingException {
		new MailSender("mail.cdjdgm.com", "25", "jianghuai.guan@cdjdgm.com", "gjh123321")
				.send("jianghuai.guan@cdjdgm.com", "gjhuai@qq.com", subject, content);
	}

	public static void sendQQMailFromSina(String subject, String content) throws AddressException, MessagingException {
		new MailSender("smtp.sina.cn", "25", "gjhuai@sina.cn", "sdjtuy7&")
				.send("gjhuai@sina.cn", "gjhuai@qq.com", subject, content);
	}

	static void sendQQMailFrom163(String subject, String content) throws AddressException, MessagingException {
		/**
		 * 设置smtp服务器以及邮箱的帐号和密码
		 * 用QQ 邮箱作为发生者不好使 （原因不明）
		 * 163 邮箱可以，但是必须开启  POP3/SMTP服务 和 IMAP/SMTP服务
		 * 因为程序属于第三方登录，所以登录密码必须使用163的授权码
		 */
		// 注意： [授权码和你平时登录的密码是不一样的]
		new MailSender("smtp.163.com", "25", "asemire", "392327013")
				.send("asemire@163.com", "gjhuai@qq.com", subject, content);

		// gjhuai@qq.com 的授权码是 jbbpdpcjsgivbicb
		// 收件人地址、邮件标题、内容
	}

}

class PickLatest {
	private final static Map<String, String> posMap = new HashMap<>();


	public static void main(String[] args) throws InterruptedException {
		PickLatest.pickLatest();
		while(true){
			int hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY);
			if (hour==15){
				PickLatest.pickLatest();
			}
			Thread.sleep(60*60*1000);
		}

	}

	static void pickLatest() {
		resetPos();

		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		factory.setNamespaceAware(true);
		DocumentBuilder builder;
		org.w3c.dom.Document doc = null;
		try {
			builder = factory.newDocumentBuilder();
			doc = builder.parse("latest.xml");

			// Create XPathFactory object
			XPathFactory xpathFactory = XPathFactory.newInstance();

			// Create XPath object
			XPath xpath = xpathFactory.newXPath();

			sendLatestChapter(doc, xpath);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}


	private static void sendLatestChapter(org.w3c.dom.Document doc, XPath xpath) {
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
					if (newPos.compareTo(pos)>0 && content.trim().length()!=0){
						MailSender.sendQQMailFromJdgm(name, content);
						//MailSender.sendQQMailFromSina(name, content);
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
		Picker picker = new Picker();
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

	private static void writePos(String name, String newPos){
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


def mainRun(def args){
	println('aaaaa')
	Picker.pickAll()
}


//if (this.args.size() <1 )  {
//	println "No Input File!!!!!"
//	return
//}

mainRun(NovelPicker.args)

