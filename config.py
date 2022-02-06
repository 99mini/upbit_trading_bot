import pyupbit

teletoken = "5216984337:AAG917KRJkThAboMF9HsIFb_EvMd0FkDyes"
teleurl = "https://api.telegram.org/bot" + teletoken + "/sendMessage"
telebotid = "5257292307"

all_ticker_url = "https://api.upbit.com/v1/ticker"

f = open("ym_api_key.txt")
lines = f.readlines()
ACCESS_KEY = lines[0].strip()
SECRET_KEY = lines[1].strip()
f.close()

INTERVAL = 'minutes60'

# upbit class instance
upbit = pyupbit.Upbit(ACCESS_KEY, SECRET_KEY)