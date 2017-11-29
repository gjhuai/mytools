package org.tubez.picker;

import java.util.Properties;

import javax.mail.Message;
import javax.mail.MessagingException;
import javax.mail.PasswordAuthentication;
import javax.mail.Session;
import javax.mail.Transport;
import javax.mail.internet.AddressException;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeMessage;

public class MailSender {
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
	
	public static void main(String[] args) {
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
    
    public static void sendQQMailFrom163(String subject, String content) throws AddressException, MessagingException {
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