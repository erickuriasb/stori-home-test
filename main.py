import shutil
import pandas as pd

from fastapi import FastAPI, File, UploadFile
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

from email_sender import smtp_email_sender

app = FastAPI()


def process_transactions(df):
    months = {
        "1": "January", "2": "Febrary", "3": "March", "4": "April", "5": "May",
        "6": "June", "7": "July", "8": "August", "9": "September", "10": "October",
        "11": "November", "12": "December"
    }
    report = {
        "Total_Balance": df['Transaction'].sum()
    }
    Debit_Amount = 0
    Credit_Amount = 0
    Count_Debit_Transactions = 0
    Count_Credit_Transactions = 0
    transactions_by_month = {}
    for row in range(len(df)):
        transaction = df.loc[row].to_dict()
        if transaction["Transaction"] < 0:
            Debit_Amount += transaction["Transaction"]
            Count_Debit_Transactions += 1
        else:
            Credit_Amount += transaction["Transaction"]
            Count_Credit_Transactions += 1
        if months[transaction["Date"][0]] in transactions_by_month:
            transactions_by_month[months[transaction["Date"][0]]] += 1
        else:
            transactions_by_month[months[transaction["Date"][0]]] = 1

    report["Average_Debit_Amount"] = Debit_Amount / Count_Debit_Transactions
    report["Average_Credit_Amount"] = Credit_Amount / Count_Credit_Transactions
    #report["Transactions_By_Month"] = [{key: value} for key,value in transactions_by_month.items()]
    report["Transactions_By_Month"] = transactions_by_month
    
    return report


@app.post('/file_processing/')
async def read_csv_file(email: EmailStr, file: UploadFile):
    with open ("movements.csv", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    df = pd.read_csv("movements.csv")
    report = process_transactions(df)
    try:
        smtp_email_sender(email, report)
    except Exception as ex:
        print(ex)
    return report