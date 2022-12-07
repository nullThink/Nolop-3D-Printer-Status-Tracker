import time
from pyotp import *

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

USERNAME = "nolop"
PASSWORD = "3dprint"

TWILIO_TOKEN = ""
TWILIO_SID = ""


printerStates = {}
DRIVER_PATH = r'C:\Users\legok\chromedriver_win32\chromedriver.exe'

options = webdriver.ChromeOptions()
options.add_argument('ignore-certificate-errors')
options.add_argument('--disable-software-rasterizer')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def parsePrinterStates():
    free = []
    occupied = []
    offline = []

    for printer in printerStates:
        if(printerStates[printer]["status"] == "Operational"):
            free.append(printer)
        elif("Printing" in printerStates[printer]["status"]):
            occupied.append({"printer": printer, "time": printerStates[printer]["time-remaining"]})
        else:
            offline.append({printer: printerStates[printer]})
    
    # Sorts the dictionary in order of least time remaining
    occupied = sorted(occupied, key=lambda d: d["time"])


    print("FREE PRINTERS")  
    for printer in free:
        print("{}".format(printer.upper()))
    print("\n")
    
    print("PRINTERS IN USE")
    for printer in occupied:
        remainingTime = printer["time"] + " remaining."

        if (remainingTime == " - "):
            remainingTime = "RECENTLY STARTED"

        print("{0}: {1}".format(printer["printer"].upper(), remainingTime))
    print("\n")
    
    print("OFFLINE PRINTERS")
    for printer in offline:
        print("{0}: {1}".format(list(printer.keys())[0].upper(), printer[list(printer.keys())[0]]["status"].upper()))
    print("\n")

# Gets data for each printer from their individual NOLOP site
for i in range(1, 13):
    currentPrinter = "p" + str(i)

    if(i != 5):
        printerSite = "https://{}.nolop.org/".format(currentPrinter)
    else:
        printerSite = "https://10.245.72.231/"

    try:
        driver.get(printerSite)
    except:
        printerStates[currentPrinter] = {"status":"ERROR GETTING WEBPAGE", "time":""}
        continue

    # Login Step
    usernameInputBar = driver.find_element(By.XPATH, '//*[@id="login-user"]')
    passwordInputBar = driver.find_element(By.XPATH, '//*[@id="login-password"]')
    
    usernameInputBar.send_keys(USERNAME)
    passwordInputBar.send_keys(PASSWORD)

    loginButton = driver.find_element(By.XPATH, '//*[@id="login-button"]')
    loginButton.click()

    while(driver.current_url != printerSite + "?#temp"):
        time.sleep(0.001)

    # Get State and Log

    wait = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, '//*[@id="state"]/div/strong[1]'))) #This is a dummy element)
    
    while(wait.text == ''):
        time.sleep(0.001)
    
    printerStatus = wait.text

    printTimeRemaining = driver.find_element(By.XPATH, '//*[@id="state"]/div/strong[9]').get_attribute('title')
    #print(printTimeRemaining)
    
    if(printTimeRemaining == ''):
        try:
            printTimeRemaining = driver.find_element(By.XPATH, '//*[@id="state"]/div/strong[10]').get_attribute('title')
        except:
            printTimeRemaining = "ERROR"

    printerStates[currentPrinter] = {"status": printerStatus, "time-remaining": printTimeRemaining}

parsePrinterStates()

driver.quit()