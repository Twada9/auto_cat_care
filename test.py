import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart




def send_gmail():
    # 送信元メールアドレスとパスワード
    sender_email = "qnote.mobilecicd@gmail.com"
    sender_password = "XEuqsH4Z9FnU5z"

    # 送信先メールアドレス
    recipient_email = "wada@qnote.co.jp"
    # メールの構築
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "休日猫世話"
    message.attach(MIMEText("埋まっています。", "plain"))

    try:
        # GmailのSMTPサーバーに接続
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)

            # メールの送信
            server.sendmail(sender_email, recipient_email, message.as_string())

        print("メールが送信されました。")
        

    except Exception as e:
        print(f"エラー: {e}")
send_gmail()