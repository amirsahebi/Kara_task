from fastapi import FastAPI,status
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
import requests
import json
from web3 import Web3

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Configure Fastapi app
app = FastAPI()

# Set api address and settings
@app.get('/contract/{contract_address}/{wallet_address}',status_code = status.HTTP_200_OK)
def Getwallet(contract_address,wallet_address):

    # Get abi of contract
    abi = Getabi(contract_address)

    # Fill in your infura API key here
    infura_url = "https://mainnet.infura.io/v3/5b7b408e928d4ffcad8de4704a45a022"

    # Connect to web3
    web3 = Web3(Web3.HTTPProvider(infura_url))

    # Get contract details
    contract = web3.eth.contract(address=contract_address, abi=abi)
    
    # Get balance of wallet of the particular contract
    balance = contract.functions.balanceOf(wallet_address).call()

    return JSONResponse({"status_code" : 200,"msg" : "OK","result" : {"balance" : balance}}, 200)


# Get abi using selenium and chrome driver
def Getabi(contract_address):
    chrome_options = Options()
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    driver = webdriver.Remote("http://selenium:4444/wd/hub",{'browserName': 'chrome'},options=chrome_options)
    url = f"https://etherscan.io/address/{contract_address}#code"
    driver.get(url)
    WebDriverWait(driver,20).until(EC.presence_of_element_located((By.ID, "js-copytextarea2")))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    a=soup.find(id="js-copytextarea2")
    jsonData = json.loads(a.contents[0])
    return jsonData