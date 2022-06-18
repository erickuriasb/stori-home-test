from http.client import HTTPException
import shutil
import pandas as pd

from fastapi import FastAPI, File, UploadFile
from pydantic import EmailStr

from email_sender import smtp_email_sender

app = FastAPI()
app.title = "Stori Challenge"
app.description = "To solve the exercise, this is an API with a single Endpoint that receives a CSV file and an email address, It processes the file and sends the report to the given email address."


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


@app.post('/file_processing/', status_code=201, tags=["Main Endpoint"])
async def read_csv_file(email: EmailStr, file: UploadFile):
    """
    Read CSV File and Process it.
  
    This function open the CSV file and transform the data and process it, then take the process result and send an email to the given address.
  
    Parameters:
    email (EmailStr): a valid email address
    file (UploadFile): a CSV file with the transactions of an account.
  
    Returns:
    dict: If everything it's OK, returns a dictionary with a success message.
          Else, return a Exception with a code error.
  
    """
    with open("movements.csv", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    df = pd.read_csv("movements.csv")
    try:
        report = process_transactions(df)
    except:
        return HTTPException(status_code=400, detail="CSV file could not be processed")
    try:
        smtp_email_sender(email, report)
    except:
        return HTTPException(status_code=400, detail="Something went wrong sending the email")
    return {"status": "The email was created and sended sucessfully!"}
