package com.gjh.mail;
import javax.mail.*;
import javax.mail.internet.*;

@GrabResolver(name = 'aliyun', root = 'https://maven.aliyun.com/repository/public')
@Grab('javax.mail:mail:1.5.0-b01')


public class SimpleSSLMail {

    private static final String SMTP_HOST_NAME = "smtp.189.cn";
    private static final int SMTP_HOST_PORT = 465;
    private static final String SMTP_AUTH_USER = "18109032120";
    private static final String SMTP_AUTH_PWD  = "guanok77";
    private static final String FROM_MAIL  = "18109032120@189.cn";
    private static final String TO_MAIL  = "gjhuai@qq.com";

    public static void main(String[] args) throws Exception{
       new SimpleSSLMail().test();
    }

    public void test() throws Exception{
        Properties props = new Properties();

        props.put("mail.transport.protocol", "smtps");
        props.put("mail.smtps.host", SMTP_HOST_NAME);
        props.put("mail.smtps.auth", "true");
        // props.put("mail.smtps.quitwait", "false");

        Session mailSession = Session.getDefaultInstance(props);
        mailSession.setDebug(true);
        Transport transport = mailSession.getTransport();

        MimeMessage message = new MimeMessage(mailSession);
        message.setFrom(new InternetAddress(FROM_MAIL));
        message.setSubject("Testing SMTP-SSL");
        message.setContent("This is a test", "text/plain");

        message.addRecipient(Message.RecipientType.TO, new InternetAddress(TO_MAIL));

        transport.connect(SMTP_HOST_NAME, SMTP_HOST_PORT, SMTP_AUTH_USER, SMTP_AUTH_PWD);

        transport.sendMessage(message,
            message.getRecipients(Message.RecipientType.TO));
        transport.close();
    }

}