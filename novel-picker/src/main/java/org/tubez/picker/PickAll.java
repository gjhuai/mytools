package org.tubez.picker;

import java.util.Map;
import java.util.ResourceBundle;

public class PickAll {

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

		System.out.println("The End ! totalSum:" + (NovelPicker.totalSum - 1) + " failureSum:" + NovelPicker.failureSum);
		System.out.println("run time: " + (endTime - startTime) / 6000 + "s");
	}

}
