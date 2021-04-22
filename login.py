import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.common.alert
from selenium.common.exceptions import *
import pyautogui


def getFromJSON(path, id):
    with open(path) as f:
        data = json.load(f)
    return data[id]

def getDateFormatted():
    aux = today.replace(year=today.year-100)
    tString = aux.strftime('%d.%m.%y')
    tString = tString.split(".")
    day = tString[0].replace("0", "")
    tString = ("%s.%s.%s") % (day, tString[1], tString[2])
    return tString


def getChromedriver(path):
    options = webdriver.ChromeOptions() 
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options, executable_path=path)
    return driver




def listaMaterias(name):
    materias = driver.find_elements_by_class_name("media-body")
    found = None
    i = 0
   
    while found == None and i < len(materias):
        materia = materias[i]
        text = materia.text
        if text == name: 
            found = materia
        else: i += 1
    return found


def login(user, passw):
    success = True;
    driver.get("https://aulavirtual.instituto.ort.edu.ar/login/index.php")
    driver.find_element_by_id("username").send_keys(user)
    driver.find_element_by_id("password").send_keys(passw)
    driver.find_element_by_id("loginbtn").click()
    try:
        if driver.find_element_by_id("loginerrormessage"): success = False
    except Exception:
        pass

    return success


def schedule():
    wd = today.weekday()
    t = today.time()
    materias = getFromJSON(matPath, 'materias')
    m = None
    i = 0

    while m == None and i < len(materias):
        materia = materias[i]
        day = materia["day"]
        hour = materia["hour"].split("/")
        start = datetime.strptime(hour[0], '%H:%M').time()
        end = datetime.strptime(hour[1], '%H:%M').time()

        if (day == wd and (t >= start and t <= end)):
            m = materia
        else: i += 1
    return m


def checkAsistencia():
    driver.switch_to.window(driver.window_handles[0])
    driver.find_element_by_partial_link_text("Asistencia").click()
    path = "//div[1]/div[4]/div[2]/div/section/div[1]/table[1]/tbody/tr"
    found = None
    tString = getDateFormatted()
    i = 1

    try:
        driver.find_element_by_partial_link_text("Enviar asistencia").click()
        driver.find_element_by_xpath('//div[1]/div[4]/div[2]/div/section/div[1]/form/fieldset/div/div/div[2]/label[1]/input').click()
        driver.find_element_by_id("id_submitbutton").click()
    except Exception as e:
        print("No hay asistencia para enviar")


def openZoom(course):
    url = driver.current_url
    
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
   
    driver.get(url + "&section=1")
    driver.find_element_by_partial_link_text(course).click()
    driver.find_element_by_xpath('//*[@id="region-main"]/div[1]/table/tbody/tr[1]/th/form/button').click()
   
    driver.switch_to.window(driver.window_handles[2])
    time.sleep(4)
    pyautogui.press('left')
    pyautogui.press('enter')


def closeTabs():
    for i in range(1, 3):
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
    driver.switch_to.window(driver.window_handles[0])


def main():
    user = getFromJSON(credPath, 'user')
    passw = getFromJSON(credPath, 'pass')

    print("Iniciando sesión...")    
    if login(user, passw):
        tab = driver.find_element_by_xpath('//*[@id="page-wrapper"]/nav/div/button')
        if tab.get_attribute("aria-expanded") == "false": tab.click()
        try:
            materia = schedule()
            if materia != None: print("Logueando en " + materia["name"] + "...")
            # type error
            materiaW = listaMaterias(materia["name"])
            materiaW.click()
            # nosuchelementexception
            openZoom(materia["course"])
            print("Confirmando asistencia...")
            checkAsistencia()
            closeTabs()
            print("Terminado")
            
        except TypeError as te:
            print("La materia no existe o no corresponde ninguna al horario")
        except NoSuchElementException as nse:
            print("El nombre del curso es inválido")
    else:
        print("Usuario o contraseña incorrectos")

        
driver = getChromedriver(r'./files/chromedriver')
today = datetime.now()
credPath = './files/credentials.json'
matPath = './files/materias.json'

if __name__ == "__main__": main()














