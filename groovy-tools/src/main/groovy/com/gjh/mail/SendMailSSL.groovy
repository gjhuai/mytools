package com.gjh.mail

import javax.mail.*
import javax.mail.internet.InternetAddress
import javax.mail.internet.MimeMessage


@GrabResolver(name = 'aliyun', root = 'https://maven.aliyun.com/repository/public')
@Grab('javax.mail:mail:1.5.0-b01')


public class SendMailSSL {
	Session session = null;
	
	public SendMailSSL(String smtpHost, String sslPort, String username, String pwd){
		Properties props = new Properties();
		props.put("mail.smtp.host", smtpHost);
		props.put("mail.smtp.socketFactory.port", sslPort);
		props.put("mail.smtp.socketFactory.class", "javax.net.ssl.SSLSocketFactory");
		props.put("mail.smtp.auth", "true");
		props.put("mail.smtp.port", sslPort);
		
		session = Session.getDefaultInstance(props,
			new javax.mail.Authenticator() {
				protected PasswordAuthentication getPasswordAuthentication() {
					return new PasswordAuthentication(username, pwd);
				}
			});
		session.setDebug(true);
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

	public static void sendQQMailFrom189(String subject, String content) {
		new SendMailSSL("smtp.189.cn", "465", "18109032120", "guanok77")
				.send("18109032120@189.cn", "gjhuai@qq.com", subject, content);
	}
}