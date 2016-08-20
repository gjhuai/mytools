package org.tubez.picker;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.ResourceBundle;
import java.util.regex.Pattern;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

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
public class NovelPicker {

	/**
	 * 抓取总数
	 */
	private static int totalSum = 1;

	/**
	 * 获取失败记录数
	 */
	private static int failureSum = 0;

	/**
	 * 测试入口
	 * 
	 * @param args
	 */
	public static void main(String[] args) {
		long startTime = System.currentTimeMillis();

		ResourceBundle proMap = ResourceBundle.getBundle("picker");

		// 目录页
		String catalogUrl = proMap.getString("catalogUrl");
		// 各章节的前缀
		String urlPrefix = proMap.getString("urlPrefix");
		// 保存路径
		String filePath = proMap.getString("filePath");
		// 屏蔽关键字
		String[] shiftWord = proMap.getString("shiftWord").split("&");

		// 解析目录所在页面元素 获取所有章节url
		NovelPicker picker = new NovelPicker();
		Map<String, String> urlMap = picker.getChapters(catalogUrl, urlPrefix);
		// 通过所有章节url 获取每个章节内容并保存
		picker.pickAllNovelText(filePath, urlMap, "UTF-8", shiftWord);

		long endTime = System.currentTimeMillis();

		System.out.println("The End ! totalSum:" + (totalSum - 1) + " failureSum:" + failureSum);
		System.out.println("run time: " + (endTime - startTime) / 6000 + "s");
	}


	/**
	 * 获取所有章节
	 * @return Map<String,String> <章节名, url>
	 */
	public Map<String, String> getChapters(String catalogUrl, String urlPrefix) {
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
			if (href.startsWith("/")) {
				href = siteUrl + href;
			} else if (!href.startsWith("http")) {
				href = siteUrl + subUrl.substring(0, subUrl.lastIndexOf('/')) + "/" + href;
			}
			if (!href.startsWith(urlPrefix)) {
				continue;
			}
			String text = link.text().trim();
			emap.put(text, href);
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
			e.printStackTrace();
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
	public void pickAllNovelText(String filePath, Map<String, String> chapterMap, String encoding, String[] shiftWord) {
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
	private String getSingleChapterText(String chapterName, String chapterUrl, String[] shiftWord) {
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
		html = html.replaceAll("&nbsp;", "");
		String contents = html.replaceAll("\\s{15,}", "");

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

}
