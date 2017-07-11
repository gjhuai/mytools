package org.tubez.picker;

import javax.mail.BodyPart;
import javax.mail.Message;
import javax.mail.MessagingException;
import javax.mail.Multipart;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.*;
import java.util.*;
import java.util.Base64.Encoder;

import javax.activation.*;

public class Mailman {

	private String smtpHost = ""; // 
	private String from = ""; // 发件人地址
	private String smtpUser = ""; // 用户名
	private String smtpPwd = ""; // 密码

//    private String affix = ""; // 附件地址
//    private String affixName = ""; // 附件名称
    
    private Properties props = new Properties();
    
    /**
     * 
     * @param smtpHost smtp服务器
     * @param smtpUser	用户名
     * @param smtpPwd	密码
     * @param from	发件人地址
     */
    public Mailman(String smtpHost, String smtpUser, String smtpPwd, String from){
        // 设置发送邮件的邮件服务器的属性（这里使用网易的smtp服务器）
        props.put("mail.smtp.host", smtpHost);
        // 需要经过授权，也就是有户名和密码的校验，这样才能通过验证（一定要有这一条）
        props.put("mail.smtp.auth", "true");
        
    	this.smtpHost = smtpHost;
        this.smtpUser = smtpUser;
        this.smtpPwd = smtpPwd;
        this.from = from;
    }

//    public void setAffix(String affix, String affixName) {
//        this.affix = affix;
//        this.affixName = affixName;
//    }

    public void send(String to, String subject, String content) throws AddressException, MessagingException {

        // 用刚刚设置好的props对象构建一个session
        Session session = Session.getDefaultInstance(props);

        // 有了这句便可以在发送邮件的过程中在console处显示过程信息，供调试使
        // 用（你可以在控制台（console)上看到发送邮件的过程）
        session.setDebug(true);

        // 用session为参数定义消息对象
        MimeMessage message = new MimeMessage(session);

        // 加载发件人地址
        message.setFrom(new InternetAddress(from));
        // 加载收件人地址
        message.addRecipient(Message.RecipientType.TO, new InternetAddress(to));
        // 加载标题
        message.setSubject(subject);

        // 向multipart对象中添加邮件的各个部分内容，包括文本内容和附件
        Multipart multipart = new MimeMultipart();

        // 设置邮件的文本内容
        BodyPart contentPart = new MimeBodyPart();
        contentPart.setText(content);

        multipart.addBodyPart(contentPart);

        // 将multipart对象放到message中
        message.setContent(multipart);
        // 保存邮件
        message.saveChanges();
        // 发送邮件
        Transport transport = session.getTransport("smtp");
        // 连接服务器的邮箱
        try {
			transport.connect(smtpHost, smtpUser, smtpPwd);
			// 把邮件发送出去
			transport.sendMessage(message, message.getAllRecipients());
		} catch (MessagingException e) {
			throw e;
		} finally{
			try {
				transport.close();
			} catch (MessagingException e) {
				e.printStackTrace();
			}			
		}
    }

    public static void sendQQMailFrom189(String subject, String content) throws AddressException, MessagingException {
    	Mailman cn = new Mailman("smtp.189.cn", "18109032120", "guanok77", "18109032120@189.cn");
    	cn.send("gjhuai@qq.com", subject, content);
    }
    
    public static void sendQQMailFromJdgm(String subject, String content) throws AddressException, MessagingException {
    	Mailman cn = new Mailman("mail.cdjdgm.com", "jianghuai.guan@cdjdgm.com", "gjh123321", "jianghuai.guan@cdjdgm.com");
    	cn.send("gjhuai@qq.com", subject, content);
    }
    
    public static void sendQQMailFrom163(String subject, String content) throws AddressException, MessagingException {
        /**
         * 设置smtp服务器以及邮箱的帐号和密码
         * 用QQ 邮箱作为发生者不好使 （原因不明）
         * 163 邮箱可以，但是必须开启  POP3/SMTP服务 和 IMAP/SMTP服务
         * 因为程序属于第三方登录，所以登录密码必须使用163的授权码  
         */
        // 注意： [授权码和你平时登录的密码是不一样的]
        Mailman cn = new Mailman("smtp.163.com", "asemire", "392327013", "asemire@163.com");
        
        // gjhuai@qq.com 的授权码是 jbbpdpcjsgivbicb
        // 收件人地址、邮件标题、内容
        cn.send("gjhuai@qq.com", subject, content);
    }

    public static void main(String[] args) throws AddressException, MessagingException {
    	String content = "一个带附件的JavaMail邮件";
    	sendQQMailFrom189("邮件标题", content);
    }
}