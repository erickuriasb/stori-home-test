import smtplib
from decouple import config
from email.message import EmailMessage
from email.mime.text import MIMEText


def smtp_email_sender(email_to: str, report: dict):
    user = config('OUTLOOK_USER')
    password = config('OUTLOOK_PASSWORD')
    server = smtplib.SMTP("smtp.office365.com", 587)
    server.starttls()
    server.ehlo()
    try:
        server.login(user, password)
    except Exception as ex:
        print(ex)

    message = EmailMessage()
    message['Subject'] = "Movements Report"
    body = f"""
        <div style="background: rgb(0, 103, 127);">
        <img src="https://play-lh.googleusercontent.com/acrduPY3FNGodTtdx0e6WGOz_EEqJ7KeRJMJARWnETH-5j2oxV2_Tb4hwIWraQKymd4=s64-rw" style="display: block; width:80px">
        </div>
        <h1>Hi,</h1>
        <p>How are you?</p>
        <p>This is the report of movements and transactions in your account:</p>
        <p>
        Total Balance is <strong>${report["Total_Balance"]:.2f}</strong><br>
        Average credit ammount: <strong>${report["Average_Credit_Amount"]}</strong><br>
        Average debit ammount: <strong>${report["Average_Debit_Amount"]}</strong><br>
        </p>
    """
    transactions = ""
    for month, value in report["Transactions_By_Month"].items():
        body += f"""Number of transactions in {month}: <strong>{value}</strong><br>"""
    body += "</p>"

    message_test = MIMEText(body, "html")
    message.attach(message_test)

    try:
        server.sendmail(user, email_to, message_test.as_string())
    except Exception as ex:
        raise Exception("")
    else:
        print("E-mail sended!")
