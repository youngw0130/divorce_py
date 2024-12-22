from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = FastAPI()

SERVICE_ACCOUNT_FILE = "tlrkrghk-a82aabac4256.json"
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1IOF3cXgA_EdITvUFb0EaYqJDg6KBNBFFpmA5x2CBFVg/edit?usp=sharing"

def fetch_spreadsheet_data():
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        client = gspread.authorize(creds)
        sheet = client.open_by_url(SPREADSHEET_URL).sheet1
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google Sheets API Error: {str(e)}")

def generate_plot(df):
    pivot_table = df.pivot_table(index="연도", columns="성별", values="이혼건수")

    plt.figure(figsize=(10, 6))
    for gender in pivot_table.columns:
        plt.plot(pivot_table.index, pivot_table[gender], marker="o", label=gender)

    plt.title("연도별 남녀 이혼율", fontsize=16)
    plt.xlabel("연도", fontsize=12)
    plt.ylabel("이혼건수", fontsize=12)
    plt.legend(title="성별", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.6)

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    buffer.close()
    plt.close()

    return image_base64

@app.get("/", response_class=HTMLResponse)
async def show_divorce_rate():
    try:
        df = fetch_spreadsheet_data()
        plot_image = generate_plot(df)
        html_content = f"""
        <html>
            <head>
                <title>연도별 남녀 이혼율</title>
            </head>
            <body>
                <h1 style='text-align: center;'>연도별 남녀 이혼율</h1>
                <img src="data:image/png;base64,{plot_image}" alt="Divorce Rate Graph" style='display: block; margin: auto;'/>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")