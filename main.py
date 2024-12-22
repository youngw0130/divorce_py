from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import gspread
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = FastAPI()

def fetch_google_sheet_data():
    gc = gspread.service_account(filename="tlrkrghk-a82aabac4256.json")
    
    spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/12aVmGJ7dgixKIZNPT-WhmTQzakf4ITuB/edit?usp=sharing")
    
    worksheet = spreadsheet.sheet1
    
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df

@app.get("/", response_class=HTMLResponse)
async def show_chart():
    df = fetch_google_sheet_data()

    print(df.head())

    plt.figure(figsize=(10, 6))

    male_data = df[df["성별"] == "남성"]
    plt.plot(male_data["연도"], male_data["이혼률"], marker="o", label="남성", color="blue")

    female_data = df[df["성별"] == "여성"]
    plt.plot(female_data["연도"], female_data["이혼률"], marker="o", label="여성", color="red")

    plt.title("대한민국 연간 이혼률 (남성과 여성)")
    plt.xlabel("년도")
    plt.ylabel("이혼건수")
    plt.legend()
    plt.grid()

    img_stream = io.BytesIO()
    plt.savefig(img_stream, format="png")
    img_stream.seek(0)

    img_base64 = base64.b64encode(img_stream.read()).decode("utf-8")

    html_content = f"""
    <html>
        <head>
            <title>대한민국 연간 이혼률</title>
        </head>
        <body>
            <h1>대한민국 연간 이혼률 (남성과 여성)</h1>
            <img src="data:image/png;base64,{img_base64}" alt="Divorce Rate Chart"/>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
