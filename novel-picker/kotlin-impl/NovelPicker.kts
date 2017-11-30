import org.jsoup.Jsoup
import org.jsoup.nodes.Document
import java.io.*
import java.util.*
import java.util.logging.Logger
import java.util.regex.Pattern

/**
 *
 * <pre>
 * Title: 网页抓取程序
 * Description:
 * 根据不同的网页结构 需要修改getElement方法实现解析
</pre> *
 *
 * @author GJH
 */
class NovelPicker {
    private val logger = Logger.getLogger(NovelPicker::class.java.canonicalName)

    /**
     * 获取所有章节
     * @return Map<String></String>,String> <章节名></章节名>, url>
     */
    fun getChapters(catalogUrl: String, urlPrefix: String): Map<String, String> {
        // 获取目录所在页面元素
        val doc = getHtmlDoc(catalogUrl)

        val idx = catalogUrl.indexOf("/", catalogUrl.indexOf("//") + 2)

        // 抓取站点url
        val siteUrl = catalogUrl.substring(0, idx)
        // 文字根url
        val subUrl = catalogUrl.substring(idx)


        val links = doc!!.select("a[href]")
        val emap = LinkedHashMap<String, String>()

        for (link in links) {
            var href = link.attr("href").trim()
            if (href.contains("javascript")) {
                continue
            }
            if (href.startsWith("/")) { // e.g. /2546/89898.html, 从根路径开始
                href = siteUrl + href
            } else if (!href.startsWith("http")) {    // e.g. 2546/89898.html, 从当前页面相对开始
                href = siteUrl + subUrl.substring(0, subUrl.lastIndexOf('/')) + "/" + href
            }
            if (!href.startsWith(urlPrefix)) {
                continue
            }
            val chapterName = link.text().trim()
            emap.put(chapterName, href)
        }
        println("URL Total：" + emap.size)
        return emap
    }


    /**
     * 获取Html Document
     */
    private fun getHtmlDoc(url: String): Document? {
        var doc: Document?
        try {
            doc = Jsoup.connect(url).timeout(600000)
                    .userAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:23.0) Gecko/20100101 Firefox/23.0")
                    .get()
        } catch (e: IOException) {
            logger.severe("无法连接到" + url + " --> " + e.localizedMessage)
            throw RuntimeException(e)
        }

        return doc
    }

    /**
     * 文件缓存
     *
     * @param filePath
     * 路径
     * @param chapterMap
     * 写入内容
     * @param encoding
     * 文件编码
     * @param shiftWord
     * 屏蔽关键字
     */
    fun pickAllNovelText(filePath: String, chapterMap: Map<String, String>, encoding: String, shiftWord: Array<String>) {
        try {
            val file = File(filePath)
            if (!file.exists()) {
                file.createNewFile()
            }
            if (file.isFile && file.exists()) {
                val write = OutputStreamWriter(FileOutputStream(file), encoding)
                val bufferedWriter = BufferedWriter(write)

                var content : String
                // 遍历Map
                for ((aName, value) in chapterMap) {
                    content = this.getSingleChapterText(aName, value, shiftWord)
                    bufferedWriter.write(aName)
                    bufferedWriter.newLine()
                    bufferedWriter.write(content)
                    bufferedWriter.newLine()
                }
                bufferedWriter.flush()
                write.close()

            } else {
                println("file error")
            }
        } catch (e: Exception) {
            println("writeFile error")
            e.printStackTrace()
        }

    }

    /**
     * catch内容
     */
    fun getSingleChapterText(chapterName: String, chapterUrl: String, shiftWord: Array<String>): String {
        val body = this.getHtmlDoc(chapterUrl)!!.body()

        //		Elements brList = body.select("br");
        //		for (Element br : brList) {
        //			br.replaceWith(new TextNode("BRBR", ""));
        //		}
        //		String contents = body.text();
        //		contents = contents.replaceAll("BRBR", "\n");
        var html = body.html()
        val pScript = Pattern.compile("<script.+?</script>", Pattern.DOTALL or Pattern.CASE_INSENSITIVE)
        html = pScript.matcher(html).replaceAll("")

        html = html.replace("<.+?>".toRegex(), "")
        html = html.replace("&nbsp;".toRegex(), " ")
        //		String contents = html;
        var contents = html.replace("\\s{60,}".toRegex(), "")

        // 屏蔽关键词
        for (str in shiftWord) {
            contents = contents.replace(str.toRegex(), "")
        }
        // 抓取内容长度大于100 即成功
        if (contents.length > 100) {
            println("Succeed - " + totalSum + chapterName)
        } else {
            println("* Failure - " + totalSum + chapterName)
            failureSum++
        }
        totalSum++
        return contents
    }

    companion object {

        /**
         * 抓取总数
         */
        internal var totalSum = 1
        /**
         * 获取失败记录数
         */
        internal var failureSum = 0
    }

}


val novel_list: List<Map<String, Any>> = listOf(
        mapOf(
                "name" to "汉乡",
                "url"  to "http://www.hanxiangxiaoshuo.com/hanxiang/",
                "prefix" to "http://www.hanxiangxiaoshuo.com/book/",
                "contentId" to "BookText",
                "excludeTags" to listOf("^h4"),
                "download" to false
        ),
        mapOf(
                "name" to "音乐系",
                "url" to "http://www.qingfxy.com/modules/article/reader.php?aid=1375",
                "prefix" to "http://www.qingfxy.com/modules/article/reader.php?aid=1375",
                "contentId" to "chapter_bd_924915",
                "excludeTags" to listOf("^h4"),
                "download" to true
        )
)


for (novel in novel_list){
    print("-------------------")
    // 目录页
    val catalogUrl = novel["url"].toString()
    // 各章节的前缀
    val urlPrefix = novel["prefix"].toString()
    //val contentId = novel["contentId"]
    //val excludeTags = novel["excludeTags"]
    // 解析目录所在页面元素 获取所有章节url
    val picker = NovelPicker()
    val urlMap = picker.getChapters(catalogUrl, urlPrefix)

    // 屏蔽关键字
    val shiftWord : Array<String> = arrayOf()
    // 通过所有章节url 获取每个章节内容并保存
    val filePath = "d:\\" + novel["name"].toString() + ".txt"
    picker.pickAllNovelText(filePath, urlMap, "UTF-8", shiftWord);
}
