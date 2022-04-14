
directorio = 'C:/Users/julio/PycharmProjects/SeleniumToltec'

import random
import time
from datetime import datetime
from timeit import default_timer as timer

import numpy as np
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from selenium.webdriver.firefox.options import Options as Opc

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def RealtorJS(df, estrategia, precioMeta, lugar, Ciudad, criterio, mes):
    driver=webdriver.Chrome('chromedriver.exe')
    driver.get(f'https://www.realtor.com/realestateandhomes-search/{lugar}')
    paginas = driver.find_elements_by_xpath('//a[@class="item btn "]')

    if len(paginas) == 0:
        print(f'Páginas faltantes: 1')
        ultPag = 2

    else:
        ultPag = int(paginas[-2].text)  # Número de la última página en formato Int
        print(f'Páginas faltantes {ultPag - 1}')
        desplazamiento = ultPag - 1

    contador = 0
    estatus = "prueba"

    for i in range(ultPag - 1):
        if estatus.find(mes) != -1:
            break
        time.sleep(3)
        # Todas las propiedades en un listado en una página
        props = driver.find_elements_by_xpath('//li[@data-testid="result-card"]')
        # Procedimiento para obtener información
        for prop in props:
            if estrategia == "Sold":
                estatus = prop.find_element_by_xpath('.//span[@class="jsx-3853574337 statusText"]').text.replace(
                    'Sold - ', "")
                estatus1 = 'Sold'
                precio = prop.find_element_by_xpath('.//span[@data-label="pc-price-sold"]').text
                if estatus.find(mes) != -1:
                    break
            else:
                # if estrategia == "PENDING":
                estatus = prop.find_element_by_xpath('.//span[@class="jsx-3853574337 statusText"]').text
                precio = prop.find_element_by_xpath(
                    './/span[@data-label="pc-price"]').text  # Para convertirlo a número int(precio.replace("$","").replace(",",""))

            if precio == 'Contact For Price':
                continue
            comparaPrecio = int(precio.replace("$", "").replace(",", "").replace("From", ""))
            if estatus == "Pending" or estatus1 == 'Sold' and comparaPrecio >= precioMeta:
                print(precio, " ", estatus, contador + filasActuales)  # Debugging
                df = pd.concat([df, new_df], ignore_index=True)
                dirección = prop.find_element_by_xpath('.//div[@data-label="pc-address"]').text.replace('\n', " ")
                enlace = prop.find_element_by_xpath('.//a[@rel="noopener"]').get_attribute('href')
                if dirección == '':
                    df.loc[contador + filasActuales, "ZIP"] = '???'
                else:
                    df.loc[contador + filasActuales, "ZIP"] = int(dirección[dirección.find(Ciudad) + 3:len(dirección)])
                df.loc[contador + filasActuales, "CITY"] = dirección[dirección.find(",") + 2:dirección.find(Ciudad) + 2]
                df.loc[contador + filasActuales, "SOLD"] = estatus
                df.loc[contador + filasActuales, "PROPERTY ADDRESS"] = dirección
                df.loc[contador + filasActuales, "PRICE"] = comparaPrecio
                df.loc[contador + filasActuales, "LINK"] = enlace
                escritor = pd.ExcelWriter(f'./{Ciudad}.xlsx', engine='xlsxwriter')
                df.to_excel(escritor, sheet_name='Prueba', index=False)
                escritor.save()
                contador = contador + 1

        print(f'Páginas faltantes {ultPag - i}')

        # Procedimiento para entrar a la página siguiente
        # element = driver.find_element(By.LINK_TEXT, "Next")
        # actions = ActionChains(driver)
        # actions.move_to_element(element).perform()
        driver.find_element(By.LINK_TEXT, "Next").click()
        time.sleep(random.uniform(1, 3))

    print('Terminó la búsqueda de RealtorJS')
    driver.close()

    if criterio == 'Address':
        df = df.drop_duplicates(subset=['PROPERTY ADDRESS'], keep='first')
        escritor = pd.ExcelWriter(f'./{Ciudad}.xlsx', engine='xlsxwriter')
        df.to_excel(escritor, sheet_name='Prueba', index=False)
        escritor.save()

    del estatus
    del estatus1
    del precio
    del comparaPrecio
    del dirección
    del enlace

    return df


##############################################################################################################################

def BrokersInfoJS(df, initialRows):
    finalRows = df.shape[0]
    print(f'finalRows: {finalRows}')
    newRowsAdded = finalRows - initialRows
    print(f'newRowsAdded: {newRowsAdded}')

    del finalRows

    df.reset_index(drop=True, inplace=True)

    excepciones = [",", "-", "BROTHERS", "GROUP", "TEAM", "REALTOR", "LLC", "& ASSOCIATES", "Co-Owner",
                   "PEARSON PROPERTIES", "BROKER", "THE", " Keller Williams Luxury Homes", "HART", "&"]

    cuentale = 0
    stopper = random.randrange(10, 30, 1)

    for i in range(newRowsAdded):
        if cuentale == stopper:
            driver=webdriver.Chrome('chromedriver.exe')
            driver.get('https://www.google.com/')
            stopper = random.randrange(10, 30, 1)
            time.sleep(10)
            cuentale = 0
        else:
            driver=webdriver.Chrome('chromedriver.exe')
            driver.get(df.loc[i + filasActuales, 'LINK'])
            print("# Registro: ", i + filasActuales, "Enlace: ", df.loc[i + filasActuales, 'LINK'])
            time.sleep(10)
            try:
                tarjeta = driver.find_element_by_xpath(
                    '//div[@class="styles__Seller-sc-1x5mdkr-0 kTWsHn"]').text.replace('Seller represented by:',
                                                                                       '').replace('\n', '')
            except NoSuchElementException:
                df.loc[i + filasActuales, 'COMPANY'] = '???'
                df.loc[i + filasActuales, 'BROKER'] = "???"
                continue

            broker = tarjeta[tarjeta.find('with ') + 5:len(tarjeta)]
            df.loc[i + filasActuales, 'COMPANY'] = broker
            if len(tarjeta) != 0:
                agente = tarjeta[0:tarjeta.find('with') - 1]
                for exc in excepciones:
                    agente = agente.upper().replace(exc, "")
                    df.loc[i + filasActuales, 'BROKER'] = agente
            else:
                df.loc[i + filasActuales, 'BROKER'] = 'Buscar personalmente'
                df.loc[i + filasActuales, 'COMPANY'] = 'Buscar personalmente'

            escritor = pd.ExcelWriter(f'./{Ciudad} Just Sold.xlsx', engine='xlsxwriter')
            df.to_excel(escritor, sheet_name='Prueba', index=False)
            escritor.save()

        cuentale = cuentale + 1

        print(f'Propiedades faltantes: {newRowsAdded - i}')

        driver.close()

        del tarjeta
        del broker
        del agente
        del escritor

    return df


#############################################################################################################################

def Realtor(df, estrategia, precioMeta, lugar, Ciudad, criterio):
    filasActuales = df.shape[0]
    cols = ["ZIP", "CITY", "SOLD", "PRICE", "BROKER", "PROPERTY ADDRESS", "YEARS OF EXPERIENCE", "COMPANY", "DRE #",
            "TYPE OF LICENSE", "E MAIL", "BROKER ADDRESS", "PHONE", "OWNER", "OWNER ADDRESS", "LINK", "COMMENT",
            "Status", "Ext PA", "Ext OA", "Investors"]
    vacios = np.repeat("", len(df.columns))
    vaciosRow = vacios.tolist()
    new_df = pd.DataFrame([vaciosRow], columns=cols)

    driver=webdriver.Chrome('chromedriver.exe')
    driver.get(f'https://www.realtor.com/realestateandhomes-search/{lugar}')
    paginas = driver.find_elements_by_xpath('//a[@class="item btn "]')

    if len(paginas) == 0:
        print(f'Páginas faltantes: 1')
        ultPag = 2

    else:
        ultPag = int(paginas[-2].text)  # Número de la última página en formato Int
        print(f'Páginas faltantes {ultPag - 1}')
        desplazamiento = ultPag - 1

    contador = 0

    for i in range(ultPag - 1):
        time.sleep(3)
        # Todas las propiedades en un listado en una página
        props = driver.find_elements_by_xpath('//li[@data-testid="result-card"]')
        # Procedimiento para obtener información
        for prop in props:
            estatus = prop.find_element_by_xpath('.//span[@class="jsx-3853574337 statusText"]').text
            precio = prop.find_element_by_xpath(
                './/span[@data-label="pc-price"]').text  # Para convertirlo a número int(precio.replace("$","").replace(",",""))
            if precio == 'Contact For Price':
                continue

            comparaPrecio = int(precio.replace("$", "").replace(",", "").replace("From", "").replace("XDR", ""))
            if estatus == "Pending" and comparaPrecio >= precioMeta:
                print(f'Precio: {precio}, Estatus: {estatus}, # Registro: {contador + filasActuales}')  # Debugging
                df = pd.concat([df, new_df], ignore_index=True)
                dirección = prop.find_element_by_xpath('.//div[@data-label="pc-address"]').text.replace('\n', " ")
                enlace = prop.find_element_by_xpath('.//a[@rel="noopener"]').get_attribute('href')
                try:
                    df.loc[contador + filasActuales, "ZIP"] = int(dirección[dirección.find(Ciudad) + 3:len(dirección)])
                except ValueError:
                    df.loc[contador + filasActuales, "ZIP"] = 'Ingresar Manualmente'
                df.loc[contador + filasActuales, "CITY"] = dirección[dirección.find(",") + 2:dirección.find("TX") + 2]
                df.loc[contador + filasActuales, "SOLD"] = estatus
                df.loc[contador + filasActuales, "PROPERTY ADDRESS"] = dirección
                df.loc[contador + filasActuales, "PRICE"] = precio
                df.loc[contador + filasActuales, "LINK"] = enlace
                escritor = pd.ExcelWriter(f'./{Ciudad}.xlsx', engine='xlsxwriter')
                df.to_excel(escritor, sheet_name='Prueba', index=False)
                escritor.save()
                contador = contador + 1

        print(f'Páginas faltantes {ultPag - i}')

        # Procedimiento para entrar a la página siguiente
        # element = driver.find_element(By.LINK_TEXT, "Next")
        # actions = ActionChains(driver)
        # actions.move_to_element(element).perform()
        driver.find_element(By.LINK_TEXT, "Next").click()
        time.sleep(random.uniform(1, 3))

    driver.close()

    if criterio == 'Address':
        df = df.drop_duplicates(subset=['PROPERTY ADDRESS'], keep='first')
        escritor = pd.ExcelWriter(f'./{Ciudad}.xlsx', engine='xlsxwriter')
        df.to_excel(escritor, sheet_name='Prueba', index=False)
        escritor.save()

    del estatus
    del dirección
    del precio
    del comparaPrecio
    del enlace
    del escritor

    return df


###############################################################################################################################

def EstatedOwnerInfo(df, initialRows):
    ownerCorrections = [' Living Trust ', ' Revocable Trust ', ' Agreement ', ' (Trustee) ', ' Tr ', ' Trust ',
                        ' trust ', ' (Life Est) ']

    finalRows = df.shape[0]
    print(f'finalRows: {finalRows}')
    newRowsAdded = finalRows - initialRows
    print(f'newRowsAdded: {newRowsAdded}')

    em = 'bmendia@toltec-capital.com'
    contra = '#Toltec2018'
    driver=webdriver.Chrome('chromedriver.exe')
    driver.get('https://estated.com/login')
    driver.maximize_window()

    try:
        signup = driver.find_element_by_xpath('//*[@id="estated-login"]/div/div[2]/div/div/div/h2')
        print(signup)  # Debbuging
        time.sleep(5)
        emailKeys = driver.find_element_by_xpath('//*[@id="email"]')
        emailKeys.send_keys('bmendia@toltec-capital.com')
        contraKeys = driver.find_element_by_xpath('//*[@id="password"]')
        contraKeys.send_keys('#Toltec2018')
        boton = driver.find_element_by_xpath('//*[@id="login"]')
        boton.submit()
    except NoSuchElementException:
        time.sleep(5)
        emailKeys = driver.find_element_by_xpath('//*[@id="email"]')
        emailKeys.send_keys('bmendia@toltec-capital.com')
        contraKeys = driver.find_element_by_xpath('//*[@id="password"]')
        contraKeys.send_keys('#Toltec2018')
        boton = driver.find_element_by_xpath('//*[@id="login"]')
        boton.submit()

    del em
    del contra
    del finalRows

    time.sleep(10)
    driver.get('https://estated.com/account/lookup')
    combined = driver.find_element_by_xpath('//*[@id="method-3"]/a')
    combined.click()

    insertar = driver.find_element_by_xpath('//*[@id="combined-form"]/div/input')

    for i in range(newRowsAdded):
        time.sleep(10)
        insertar.clear()
        insertar.send_keys(df.loc[i + filasActuales, 'PROPERTY ADDRESS'])
        time.sleep(2)
        insertar.submit()
        time.sleep(5)
        # wait = WebDriverWait(driver, 10)

        # try:
        #   element = WebDriverWait(driver,20).until(EC.frame_to_be_available_and_switch_to_it(By.XPATH,'//*[@id="report"]/div[3]/div/div/div/div[1]/div/div[2]/span[2]'))
        # except:

        try:
            time.sleep(2)
            errorAddress = driver.find_element_by_xpath('//*[@id="lookup-container"]/div/div/h3').text
            if errorAddress == "We couldn't find that address.":
                df.loc[i + filasActuales, 'COMMENT'] = "Error en la búsqueda"
                df.loc[i + filasActuales, 'OWNER'] = "???"
                df.loc[i + filasActuales, 'OWNER ADDRESS'] = "???"
                print(i)
                continue
        except NoSuchElementException:
            time.sleep(3)
            owner = driver.find_element_by_xpath(
                '//*[@id="report"]/div[3]/div/div/div/div[1]/div/div[2]/span[2]').text.replace("\n", " ")
            ownerAddress = driver.find_element_by_xpath(
                '//*[@id="report"]/div[3]/div/div/div/div[2]/span[2]').text.replace(
                "\n", " ").replace("*Owner is known to occupy subject property", "")
            # if owner.find(',')!=-1 and owner.find(''): ##Terminar de desarrollar idea
            for j in ownerCorrections:
                owner = owner.replace(j, ". ")
                if owner == '':
                    owner = "???"
                else:
                    df.loc[i + filasActuales, 'OWNER'] = owner
                if owner == '':
                    ownerAddress = "???"
                else:
                    ownerAddress = driver.find_element_by_xpath(
                        '//*[@id="report"]/div[3]/div/div/div/div[2]/span[2]').text.replace("\n", " ").replace(
                        "*Owner is known to occupy subject property", "")
                    df.loc[i + filasActuales, 'OWNER ADDRESS'] = ownerAddress
            print(f'Dueño: {owner}, Dirección: {ownerAddress},# Registro: {i}')

            escritor = pd.ExcelWriter(f'./{Ciudad}.xlsx', engine='xlsxwriter')
            df.to_excel(escritor, sheet_name='Prueba', index=False)
            escritor.save()

    driver.close()

    del owner
    del ownerAddress
    del escritor

    print("Terminó la búsqueda de información del propietario")

    return df


###############################################################################################################################

def LicenciasTX(df, initialRows):
    finalRows = df.shape[0]
    print(f'finalRows: {finalRows}')
    newRowsAdded = finalRows - initialRows
    print(f'newRowsAdded: {newRowsAdded}')

    del finalRows

    print('Buscando información de los brokers')

    driver=webdriver.Chrome('chromedriver.exe')
    for m in range(newRowsAdded):
        if m == 1:
            espera = 30
        else:
            espera = 15
        # Abriendo la página para las licencias
        driver.get(
            'https://www.trec.texas.gov/apps/license-holder-search/?lic_name=&industry=Real+Estate&email=&city=&county=&zip=&display_status=&lic_hp=&ws=649&license_search=Search')
        if df.loc[m + filasActuales, 'DRE #'] == "Buscar ID aparte":
            inputNomLic = df.loc[m + filasActuales, 'BROKER']
            # Encontrar el rectángulo para introducir el nombre
            licName = driver.execute_script("return document.getElementsByName('lic_name')[0];")
            driver.execute_script("arguments[0].click();", licName)
            driver.execute_script("arguments[0].click();", licName)
            time.sleep(espera)
            # Introducir el nombre del agente
            keys = f"arguments[0].value='{inputNomLic}';"
            driver.execute_script(keys, licName)
            # Enviar información y pasar a la siguiente página
            driver.find_element(By.NAME, "lic_name").send_keys(Keys.ENTER)
            time.sleep(10)
            multiplesOpciones = driver.execute_script(
                "return document.getElementsByClassName('paginator-description');")
            try:
                errorBusqueda = driver.find_element_by_xpath('//*[@id="main-content"]/div[3]/div[1]/h5').text
                if errorBusqueda == 'No Matching Records':
                    df.loc[m + filasActuales, 'COMMENT'] = "Verificar nombre (Abreviaciones, puntuaciones, etc)"
                    continue
            except NoSuchElementException:
                print("No hay errores en el nombre")
            if len(multiplesOpciones) != 0:
                df.loc[m + filasActuales, 'COMMENT'] = "Múltiples opciones"
                continue
            # Extraer el número de la licencia y sustituirlo
            numeroLicencia = driver.find_element_by_xpath('//h5[@class="panel-title"]').text
            if numeroLicencia.find(
                    'LLC') != -1:  # MAndamuchas opciones para elegir con cuando el tipo de Licencia es Real EState LLC
                df.loc[m + filasActuales, 'COMMENT'] = "Múltiples opciones"
                continue
            extrIni = numeroLicencia.find("#") + 1
            extrFin = len(numeroLicencia)
            dre = int(numeroLicencia[extrIni:extrFin])
            df.loc[m + filasActuales, "DRE #"] = dre
        else:
            inputNomLic = df.loc[m + filasActuales, "DRE #"]
            # Abriendo la página para las licencias
            time.sleep(4)
            # Encontrar el rectángulo para introducir el nomrbe
            licName = driver.execute_script("return document.getElementsByName('lic_name')[0];")
            driver.execute_script("arguments[0].click();", licName)
            driver.execute_script("arguments[0].click();", licName)
            time.sleep(25)
            # Introducir el nombre del agente
            keys = f"arguments[0].value='{inputNomLic}';"
            driver.execute_script(keys, licName)
            # Enviar información y pasar a la siguiente página
            driver.find_element(By.NAME, "lic_name").send_keys(Keys.ENTER)
            # Verficar que no sea un tipo de licencia rara

        # Extrayendo el tipo de licencia{
        time.sleep(10)
        numeroLicencia = driver.find_element_by_xpath('//h5[@class="panel-title"]').text
        tipoLicencia = numeroLicencia[0:numeroLicencia.find(",")]
        df.loc[m + filasActuales, 'TYPE OF LICENSE'] = tipoLicencia
        # Extrayendo el email del agente
        email = driver.find_elements_by_xpath('//div[@class="data-fluid rev-field"]')[0].text
        df.loc[m + filasActuales, "E MAIL"] = email
        # Encontrando el teléfono del agente
        phone = driver.find_elements_by_xpath('//div[@class="data-fluid rev-field"]')[1].text
        df.loc[m + filasActuales, "PHONE"] = phone
        # Encontrando la dirección del agente
        brokerAddress = \
        driver.find_elements_by_xpath('//div[@class="field-fluid col-xs-12 col-sm-12 col-md-12 col-lg-12"]')[
            0].text.replace("\n", " ").replace('Business Address ', "")
        df.loc[m + filasActuales, "BROKER ADDRESS"] = brokerAddress
        # Encontrando los años de experiencia
        lastDate = int('20' + driver.find_element_by_xpath(
            '//*[@id="main-content"]/div[3]/div[2]/table/tbody/tr[last()]/td[1]').text[6:8])
        fecha = datetime.now().year
        if lastDate > fecha:
            lastDate = lastDate - 100
        experiencia = fecha - lastDate
        df.loc[m + filasActuales, "YEARS OF EXPERIENCE"] = experiencia

        escritor = pd.ExcelWriter(f'./{Ciudad}.xlsx', engine='xlsxwriter')
        df.to_excel(escritor, sheet_name='Prueba', index=False)
        escritor.save()

    driver.close()

    del inputNomLic
    del keys
    del errorBusqueda
    del numeroLicencia
    del extrIni
    del extrFin
    del dre
    del licName
    del email
    del phone
    del brokerAddress
    del lastDate
    del experiencia
    del escritor

    print('Terminó la búsqueda de brokers')

    return df


##############################################################################################################################

def BrokersInfo(df, initialRows):
    finalRows = df.shape[0]
    print(f'finalRows: {finalRows}')
    newRowsAdded = finalRows - initialRows
    print(f'newRowsAdded: {newRowsAdded}')

    excepciones = [",", "-", "BROTHERS", "GROUP", "TEAM", "REALTOR", "LLC", "& ASSOCIATES", "Co-Owner",
                   "PEARSON PROPERTIES", "BROKER", "THE", " Keller Williams Luxury Homes", "HART", "&",
                   "International Realtor", "'s"]

    for i in range(newRowsAdded):
        try:
            driver = webdriver.Firefox()
            driver.get('http://www.google.com')
            time.sleep(2)
            #tarjeta = driver.find_elements_by_xpath('//div[@class="provider"]')
            driver.get(df.loc[i + filasActuales, 'LINK'])
        except:
            driver = webdriver.Chrome()
            driver.get('http://www.google.com')
            time.sleep(2)
            # tarjeta = driver.find_elements_by_xpath('//div[@class="provider"]')
            driver.get(df.loc[i + filasActuales, 'LINK'])
        print(i + filasActuales, df.loc[i + filasActuales, 'LINK'])
        tarjeta = driver.find_elements_by_xpath('//div[@class="provider"]')
        #################3
        if len(tarjeta) != 0:
            try:
                licencia = int(
                    driver.find_element_by_xpath('//li[@data-testid="state-license"]').text.replace('state license\n#',
                                                                                                    ""))
            except NoSuchElementException:
                df.loc[i + filasActuales, 'DRE #'] = "Buscar ID aparte"
            else:
                df.loc[i + filasActuales, 'DRE #'] = licencia

            try:
                agente = tarjeta[0].find_element_by_xpath('.//a[@data-testid="provider-link"]').text
            except NoSuchElementException:
                agente = tarjeta[0].find_element_by_xpath('.//span').text
                for exc in excepciones:
                    agente = agente.upper().replace(exc, "")
                df.loc[i + filasActuales, 'BROKER'] = agente
            else:
                for exc in excepciones:
                    agente = agente.upper().replace(exc, "")
                df.loc[i + filasActuales, 'BROKER'] = agente

            try:
                broker = tarjeta[1].find_element_by_xpath('.//a[@data-testid="provider-link"]').text
            except NoSuchElementException:
                broker = tarjeta[1].find_element_by_xpath('.//span').text
                df.loc[i + filasActuales, 'COMPANY'] = broker
            else:
                df.loc[i + filasActuales, 'COMPANY'] = broker
        else:
            tarjeta2 = driver.find_elements_by_xpath('//span[@class="rdc-ldp-5or6gw dmbdaG"]')
            agente = tarjeta2[0].text.replace('Listed by ', "")
            for exc in excepciones:
                agente = agente.upper().replace(exc, "")
            df.loc[i + filasActuales, 'BROKER'] = agente
            broker = tarjeta2[1].text.replace('with ', "")
            df.loc[i + filasActuales, 'COMPANY'] = broker
            licencia = 'Buscar ID aparte'
            df.loc[i + filasActuales, 'DRE #'] = licencia

        escritor = pd.ExcelWriter(f'./{Ciudad}.xlsx', engine='xlsxwriter')
        df.to_excel(escritor, sheet_name='Prueba', index=False)
        escritor.save()

        print(f'Propiedades faltantes: {newRowsAdded - i}')

        driver.close()

    del tarjeta
    del agente
    del broker
    del escritor

    return df

###############################################################################################################################

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

directorio_credenciales = 'credentials_module.json'


# iniciar sesion
def login():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(directorio_credenciales)

    if gauth.access_token_expired:
        gauth.Refresh()
        gauth.SaveCredentialsFile(directorio_credenciales)
    else:
        gauth.Authorize()

    return GoogleDrive(gauth)


# Crear archivo de texto simple
def crear_archivo_texto(nombre_archivo, contenido, id_folder):
    credenciales = login()
    archivo = credenciales.CreateFile({'title': nombre_archivo,
                                       'parents': [{'kind': 'drive#filelink', 'id': id_folder}]})
    archivo.SetContentString(contenido)
    archivo.Upload()


# SUBIR UN ARCHIVO A DRIVE
def subir_archivo(ruta_archivo, id_folder):
    credenciales = login()
    archivo = credenciales.CreateFile({'parents': [{"kind": "drive#fileLink",
                                                    "id": id_folder}]})
    archivo['title'] = ruta_archivo.split("/")[-1]
    archivo.SetContentFile(ruta_archivo)
    archivo.Upload()


# DESCARGAR UN ARCHIVO DE DRIVE POR ID
def bajar_archivo_por_id(id_drive, ruta_descarga):
    credenciales = login()
    archivo = credenciales.CreateFile({'id': id_drive})
    nombre_archivo = archivo['title']
    archivo.GetContentFile(ruta_descarga + nombre_archivo)


# BUSCAR ARCHIVOS
def busca(query):
    resultado = []
    credenciales = login()
    # Archivos con el nombre 'mooncode': title = 'mooncode'
    # Archivos que contengan 'mooncode' y 'mooncoders': title contains 'mooncode' and title contains 'mooncoders'
    # Archivos que NO contengan 'mooncode': not title contains 'mooncode'
    # Archivos que contengan 'mooncode' dentro del archivo: fullText contains 'mooncode'
    # Archivos en el basurero: trashed=true
    # Archivos que se llamen 'mooncode' y no esten en el basurero: title = 'mooncode' and trashed = false
    lista_archivos = credenciales.ListFile({'q': query}).GetList()
    for f in lista_archivos:
        # ID Drive
        print('ID Drive:', f['id'])
        resultado.append(f['id'])
        # Link de visualizacion embebido
        print('Link de visualizacion embebido:', f['embedLink'])
        resultado.append(f['embedLink'])
        # Link de descarga
        print('Link de descarga:', f['downloadUrl'])
        resultado.append(f['downloadUrl'])
        # Nombre del archivo
        print('Nombre del archivo:', f['title'])
        resultado.append(f['title'])
        # Tipo de archivo
        print('Tipo de archivo:', f['mimeType'])
        resultado.append(f['mimeType'])
        # Esta en el basurero
        print('Esta en el basurero:', f['labels']['trashed'])
        resultado.append(f['labels']['trashed'])
        # Fecha de creacion
        print('Fecha de creacion:', f['createdDate'])
        resultado.append(f['createdDate'])
        # Fecha de ultima modificacion
        print('Fecha de ultima modificacion:', f['modifiedDate'])
        resultado.append(f['modifiedDate'])
        # Version
        print('Version:', f['version'])
        resultado.append(f['version'])
        # Tamanio
        print('Tamanio:', f['fileSize'])
        resultado.append(f['fileSize'])

    return resultado


# DESCARGAR UN ARCHIVO DE DRIVE POR NOMBRE
def bajar_archivo_por_nombre(nombre_archivo, ruta_descarga):
    credenciales = login()
    lista_archivos = credenciales.ListFile({'q': "title = '" + nombre_archivo + "'"}).GetList()
    if not lista_archivos:
        print('No se encontro el archivo: ' + nombre_archivo)
    archivo = credenciales.CreateFile({'id': lista_archivos[0]['id']})
    archivo.GetContentFile(ruta_descarga + nombre_archivo)


# BORRAR/RECUPERAR ARCHIVOS
def borrar_recuperar(id_archivo):
    credenciales = login()
    archivo = credenciales.CreateFile({'id': id_archivo})
    # MOVER A BASURERO
    archivo.Trash()
    # SACAR DE BASURERO
    archivo.UnTrash()
    # ELIMINAR PERMANENTEMENTE
    archivo.Delete()


# CREAR CARPETA
def crear_carpeta(nombre_carpeta, id_folder):
    credenciales = login()
    folder = credenciales.CreateFile({'title': nombre_carpeta,
                                      'mimeType': 'application/vnd.google-apps.folder',
                                      'parents': [{"kind": "drive#fileLink",
                                                   "id": id_folder}]})
    folder.Upload()


# MOVER ARCHIVO
def mover_archivo(id_archivo, id_folder):
    credenciales = login()
    archivo = credenciales.CreateFile({'id': id_archivo})
    propiedades_ocultas = archivo['parents']
    archivo['parents'] = [{'isRoot': False,
                           'kind': 'drive#parentReference',
                           'id': id_folder,
                           'selfLink': 'https://www.googleapis.com/drive/v2/files/' + id_archivo + '/parents/' + id_folder,
                           'parentLink': 'https://www.googleapis.com/drive/v2/files/' + id_folder}]
    archivo.Upload(param={'supportsTeamDrives': True})


# ENLISTAR LOS PERMISOS ACTUALES
def enlistar_permisos_actuales(id_drive):
    drive = login()
    file1 = drive.CreateFile({'id': id_drive})
    permissions = file1.GetPermissions()
    lista_de_permisos = file1['permissions']

    for permiso in lista_de_permisos:
        # ID DEL PERMISO
        print('ID PERMISO: {}'.format(permiso['id']))
        # ROLE = owner | organizer | fileOrganizer | writer | reader
        print('ROLE: {}'.format(permiso['role']))
        # TYPE (A QUIEN SE LE COMPARTIRA LOS PERMISOS) = anyone | group | user
        print('TYPE: {}'.format(permiso['type']))

        # EMAIL
        if permiso.get('emailAddress'):
            print('EMAIL: {}'.format(permiso['emailAddress']))

        # NAME
        if permiso.get('name'):
            print('NAME: {}'.format(permiso['name']))

        print('=====================================================')


# INSERTAR/ OTORGAR PERMISOS
def insertar_permisos(id_drive, type, value, role):
    drive = login()
    file1 = drive.CreateFile({'id': id_drive})
    # VALUE (EMAIL DE A QUIEN SE LE OTORGA EL PERMISO)
    permission = file1.InsertPermission({'type': type, 'value': value, 'role': role})


# ELIMINAR PERMISOS
def eliminar_permisos(id_drive, permission_id=None, email=None):
    drive = login()
    file1 = drive.CreateFile({'id': id_drive})
    permissions = file1.GetPermissions()
    if permission_id:
        file1.DeletePermission(permission_id)
    elif email:
        for permiso in permissions:
            if permiso.get('emailAddress'):
                if permiso.get('emailAddress') == email:
                    file1.DeletePermission(permiso['id'])



print("Por favor ingrese los siguientes parámetros")
estrategia= input('Indique el tipo de estrategia (Pending, Sold): ')
precioMeta= input("Precio mínimo de las propiedades que busca: ")
precioMeta=int(precioMeta)
lugar= input("ZIP o Zona de su interés: ") #78738
Ciudad=input("Ciudad de su interés (TX, CA): ")
criterio = input("Tipo de búsqueda (Brokers, Owners): ")
lugar=f'{lugar.replace(" ","-")}_{Ciudad}'
if estrategia == 'Sold':
    lugar=lugar+'/show-recently-sold'
    mes = input('mes: ')

import os

checkpoint = input("Valide el checkpoint: ")

ruta_descarga = directorio
# filasActuales = df.shape[0]
# cols=["ZIP", "CITY", "SOLD", "PRICE","BROKER","PROPERTY ADDRESS","YEARS OF EXPERIENCE","COMPANY","DRE #", "TYPE OF LICENSE","E MAIL", "BROKER ADDRESS", "PHONE","OWNER","OWNER ADDRESS","LINK", "COMMENT","Status","Ext PA", "Ext OA", "Investors"]
# vacios=np.repeat("",len(df.columns))
# vaciosRow=vacios.tolist()
# new_df = pd.DataFrame([vaciosRow],columns=cols)

inicio = timer()  # Marcar cuando inicia la prueba

if Ciudad == 'CA':
    print('debugging')
    if estrategia == 'Pending':
        id_folder = '1I2zGiNJQdqfuW2GiXVBgoEoMMj64I2bx'
        print('debugging')
        if criterio == 'Brokers':

            print('Realizando procesos ____________')
            Ciudad = f'{Ciudad} Brokers'
            bajar_archivo_por_nombre(f'{Ciudad}.xlsx', f'{ruta_descarga}/')

            df = pd.read_excel(f'{Ciudad}.xlsx', index_col=False, header=0,
                               names=["ZIP", "CITY", "SOLD", "PRICE", "BROKER", "PROPERTY ADDRESS",
                                      "YEARS OF EXPERIENCE", "COMPANY", "DRE #", "TYPE OF LICENSE", "E MAIL",
                                      "BROKER ADDRESS", "PHONE", "OWNER", "OWNER ADDRESS", "LINK", "COMMENT", "Status",
                                      "Ext PA", "Ext OA", "Investors"])
            filasActuales = df.shape[0]
            cols = ["ZIP", "CITY", "SOLD", "PRICE", "BROKER", "PROPERTY ADDRESS", "YEARS OF EXPERIENCE", "COMPANY",
                    "DRE #", "TYPE OF LICENSE", "E MAIL", "BROKER ADDRESS", "PHONE", "OWNER", "OWNER ADDRESS", "LINK",
                    "COMMENT", "Status", "Ext PA", "Ext OA", "Investors"]
            vacios = np.repeat("", len(df.columns))
            vaciosRow = vacios.tolist()
            new_df = pd.DataFrame([vaciosRow], columns=cols)
            initialRows = df.shape[0]
            Ciudad = 'CA'
            #############Funciones a llamar##################
            ResultadosRealtor = Realtor(df, estrategia, precioMeta, lugar, Ciudad, criterio)
            ResultadosBrokerInfo = BrokersInfo(ResultadosRealtor, initialRows)
            ###agregar el módulo de las licencias de California
            ResultadosBrokerInfo
            ############Fin de fnuciones a llamar############
            archivo = f"{directorio}/{Ciudad}.xlsx"
            nombre_nuevo = f"{directorio}/{Ciudad} Brokers.xlsx"
            os.remove(nombre_nuevo)
            os.rename(archivo, nombre_nuevo)

            eliminar = busca(f'title = "{Ciudad} Brokers.xlsx"')[0]

            borrar_recuperar(eliminar)

            subir_archivo(f'{Ciudad} Brokers.xlsx', id_folder)

            print("El archivo se ha actualizado exitosamente en GD")

        elif criterio == 'Owners':
            print('Realizando proceso Realtor + Estated')

            Ciudad = f'{Ciudad} Owners'

            bajar_archivo_por_nombre(f'{Ciudad}.xlsx', f'{ruta_descarga}/')

            df = pd.read_excel(f'{Ciudad}.xlsx', index_col=False, header=0,
                               names=["ZIP", "CITY", "SOLD", "PRICE", "BROKER", "PROPERTY ADDRESS",
                                      "YEARS OF EXPERIENCE", "COMPANY", "DRE #", "TYPE OF LICENSE", "E MAIL",
                                      "BROKER ADDRESS", "PHONE", "OWNER", "OWNER ADDRESS", "LINK", "COMMENT", "Status",
                                      "Ext PA", "Ext OA", "Investors"])
            filasActuales = df.shape[0]
            cols = ["ZIP", "CITY", "SOLD", "PRICE", "BROKER", "PROPERTY ADDRESS", "YEARS OF EXPERIENCE", "COMPANY",
                    "DRE #", "TYPE OF LICENSE", "E MAIL", "BROKER ADDRESS", "PHONE", "OWNER", "OWNER ADDRESS", "LINK",
                    "COMMENT", "Status", "Ext PA", "Ext OA", "Investors"]
            vacios = np.repeat("", len(df.columns))
            vaciosRow = vacios.tolist()
            new_df = pd.DataFrame([vaciosRow], columns=cols)
            initialRows = df.shape[0]
            Ciudad = 'CA'
            #############Funciones a llamar############
            ResultadosRealtor = Realtor(df, estrategia, precioMeta, lugar, Ciudad, criterio)
            ResultadosEstated = EstatedOwnerInfo(ResultadosRealtor, initialRows)
            ResultadosEstated
            ##########Fin de funciones a llamar#######
            archivo = f"{directorio}/{Ciudad}.xlsx"
            nombre_nuevo = f"{directorio}/{Ciudad} Owners.xlsx"
            os.remove(nombre_nuevo)
            os.rename(archivo, nombre_nuevo)

            eliminar = busca(f'title = "{Ciudad} Owners.xlsx"')[0]

            borrar_recuperar(eliminar)

            subir_archivo(f'{Ciudad} Owners.xlsx', id_folder)

            print("El archivo se ha actualizado exitosamente en GD")

    if estrategia == 'Sold':
        print('Realizando procesos ______________________')
        Ciudad = f'{Ciudad} Just Sold'

        id_folder = '1YR8C3Gfqe24YtSybuirCg3uEc5wY91En'
        bajar_archivo_por_nombre(f'{Ciudad}.xlsx', f'{ruta_descarga}/')

        df = pd.read_excel(f'{Ciudad}.xlsx', index_col=False, header=0,
                           names=["ZIP", "CITY", "SOLD", "PRICE", "BROKER", "PROPERTY ADDRESS", "YEARS OF EXPERIENCE",
                                  "COMPANY", "DRE #", "TYPE OF LICENSE", "E MAIL", "BROKER ADDRESS", "PHONE", "OWNER",
                                  "OWNER ADDRESS", "LINK", "COMMENT", "Status", "Ext PA", "Ext OA", "Investors"])
        filasActuales = df.shape[0]
        cols = ["ZIP", "CITY", "SOLD", "PRICE", "BROKER", "PROPERTY ADDRESS", "YEARS OF EXPERIENCE", "COMPANY", "DRE #",
                "TYPE OF LICENSE", "E MAIL", "BROKER ADDRESS", "PHONE", "OWNER", "OWNER ADDRESS", "LINK", "COMMENT",
                "Status", "Ext PA", "Ext OA", "Investors"]
        vacios = np.repeat("", len(df.columns))
        vaciosRow = vacios.tolist()
        new_df = pd.DataFrame([vaciosRow], columns=cols)
        initialRows = df.shape[0]

        Ciudad = 'CA'
        #############Funciones a llamar##################
        ResultadosRealtorJS = RealtorJS(df, estrategia, precioMeta, lugar, Ciudad, criterio, mes)
        # ResuladoBrokersInfoJS = BrokersInfoJS(ResultadosRealtorJS ,initialRows,driver) ##Sólo una vez que se haya incorporado el elemento 'Type of Property'
        ResultadosEstated = EstatedOwnerInfo(ResultadosRealtorJS,
                                             initialRows)  ## Hacer el cambio de ResultadosRealtorJS  a ResuladoBrokersInfoJS cuando se agregue la variable 'Type of Property'
        ResultadosEstated
        ############Fin de fnuciones a llamar############
        archivo = f"{directorio}/{Ciudad}.xlsx"
        nombre_nuevo = f"{directorio}/{Ciudad} Just Sold.xlsx"
        os.remove(nombre_nuevo)
        os.rename(archivo, nombre_nuevo)

        eliminar = busca(f'title = "{Ciudad} Just Sold.xlsx"')[0]

        borrar_recuperar(eliminar)

        subir_archivo(f'{Ciudad} Just Sold.xlsx', id_folder)

        print("El archivo se ha actualizado exitosamente en GD")
if Ciudad == 'TX':
    if estrategia == 'Pending':
        id_folder = '1REhsbMqnLPrYbgteU5VRye9JHAKZXQDC'
        if criterio == 'Brokers':
            if criterio == 'Brokers':
                print('Realizando procesos ____________')

                Ciudad = f'{Ciudad} Brokers'
                bajar_archivo_por_nombre(f'{Ciudad}.xlsx', f'{ruta_descarga}/')

                df = pd.read_excel(f'{Ciudad}.xlsx', index_col=False, header=0,
                                   names=["ZIP", "CITY", "SOLD", "PRICE", "BROKER", "PROPERTY ADDRESS",
                                          "YEARS OF EXPERIENCE", "COMPANY", "DRE #", "TYPE OF LICENSE", "E MAIL",
                                          "BROKER ADDRESS", "PHONE", "OWNER", "OWNER ADDRESS", "LINK", "COMMENT",
                                          "Status", "Ext PA", "Ext OA", "Investors"])
                filasActuales = df.shape[0]
                cols = ["ZIP", "CITY", "SOLD", "PRICE", "BROKER", "PROPERTY ADDRESS", "YEARS OF EXPERIENCE", "COMPANY",
                        "DRE #", "TYPE OF LICENSE", "E MAIL", "BROKER ADDRESS", "PHONE", "OWNER", "OWNER ADDRESS",
                        "LINK", "COMMENT", "Status", "Ext PA", "Ext OA", "Investors"]
                vacios = np.repeat("", len(df.columns))
                vaciosRow = vacios.tolist()
                new_df = pd.DataFrame([vaciosRow], columns=cols)
                initialRows = df.shape[0]

                Ciudad = 'TX'
                #############Funciones a llamar##################
                ResultadosRealtor = Realtor(df, estrategia, precioMeta, lugar, Ciudad, criterio)
                ResultadosBrokerInfo = BrokersInfo(ResultadosRealtor, initialRows)
                ResutaldoLicenciasTX = LicenciasTX(ResultadosBrokerInfo, initialRows)
                ResutaldoLicenciasTX
                ############Fin de fnuciones a llamar############
                archivo = f"{directorio}/{Ciudad}.xlsx"
                nombre_nuevo = f"{directorio}/{Ciudad} Brokers.xlsx"
                os.remove(nombre_nuevo)
                os.rename(archivo, nombre_nuevo)

                eliminar = busca(f'title = "{Ciudad} Brokers.xlsx"')[0]

                borrar_recuperar(eliminar)

                subir_archivo(f'{Ciudad} Brokers.xlsx', id_folder)

                print("El archivo se ha actualizado exitosamente en GD")

        elif criterio == 'Owners':

            print('Realizando procesos _______________')

            Ciudad = f'{Ciudad} Owners'

            bajar_archivo_por_nombre(f'{Ciudad}.xlsx', f'{ruta_descarga}/')

            df = pd.read_excel(f'{Ciudad}.xlsx', index_col=False, header=0,
                               names=["ZIP", "CITY", "SOLD", "PRICE", "BROKER", "PROPERTY ADDRESS",
                                      "YEARS OF EXPERIENCE", "COMPANY", "DRE #", "TYPE OF LICENSE", "E MAIL",
                                      "BROKER ADDRESS", "PHONE", "OWNER", "OWNER ADDRESS", "LINK", "COMMENT", "Status",
                                      "Ext PA", "Ext OA", "Investors"])
            filasActuales = df.shape[0]
            cols = ["ZIP", "CITY", "SOLD", "PRICE", "BROKER", "PROPERTY ADDRESS", "YEARS OF EXPERIENCE", "COMPANY",
                    "DRE #", "TYPE OF LICENSE", "E MAIL", "BROKER ADDRESS", "PHONE", "OWNER", "OWNER ADDRESS", "LINK",
                    "COMMENT", "Status", "Ext PA", "Ext OA", "Investors"]
            vacios = np.repeat("", len(df.columns))
            vaciosRow = vacios.tolist()
            new_df = pd.DataFrame([vaciosRow], columns=cols)
            initialRows = df.shape[0]

            Ciudad = 'TX'
            #############Funciones a llamar############
            ResultadosRealtor = Realtor(df, estrategia, precioMeta, lugar, Ciudad, criterio)
            ResultadosEstated = EstatedOwnerInfo(ResultadosRealtor, initialRows)
            ResultadosEstated
            ##########Fin de funciones a llamar#######
            archivo = f"{directorio}/{Ciudad}.xlsx"
            nombre_nuevo = f"{directorio}/{Ciudad} Owners.xlsx"
            os.remove(nombre_nuevo)
            os.rename(archivo, nombre_nuevo)

            eliminar = busca(f'title = "{Ciudad} Owners.xlsx"')[0]

            borrar_recuperar(eliminar)

            subir_archivo(f'{Ciudad} Owners.xlsx', id_folder)

            print("El archivo se ha actualizado exitosamente en GD")

    if estrategia == 'Sold':
        id_folder = '1t1ZFKbtEoYbYrhEqqJYroIV5wJRYIwx2'

        print('Realizando procesos ______________________')
        Ciudad = f'{Ciudad} Just Sold'

        bajar_archivo_por_nombre(f'{Ciudad}.xlsx', f'{ruta_descarga}/')

        df = pd.read_excel(f'{Ciudad}.xlsx', index_col=False, header=0,
                           names=["ZIP", "CITY", "SOLD", "PRICE", "BROKER", "PROPERTY ADDRESS", "YEARS OF EXPERIENCE",
                                  "COMPANY", "DRE #", "TYPE OF LICENSE", "E MAIL", "BROKER ADDRESS", "PHONE", "OWNER",
                                  "OWNER ADDRESS", "LINK", "COMMENT", "Status", "Ext PA", "Ext OA", "Investors"])
        filasActuales = df.shape[0]
        cols = ["ZIP", "CITY", "SOLD", "PRICE", "BROKER", "PROPERTY ADDRESS", "YEARS OF EXPERIENCE", "COMPANY", "DRE #",
                "TYPE OF LICENSE", "E MAIL", "BROKER ADDRESS", "PHONE", "OWNER", "OWNER ADDRESS", "LINK", "COMMENT",
                "Status", "Ext PA", "Ext OA", "Investors"]
        vacios = np.repeat("", len(df.columns))
        vaciosRow = vacios.tolist()
        new_df = pd.DataFrame([vaciosRow], columns=cols)

        initialRows = df.shape[0]

        Ciudad = 'TX'
        #############Funciones a llamar##################
        ResultadosRealtorJS = RealtorJS(df, estrategia, precioMeta, lugar, Ciudad, criterio, mes)
        # ResuladoBrokersInfoJS = BrokersInfoJS(ResultadosRealtorJS ,initialRows) ##Sólo una vez que se haya incorporado el elemento 'Type of Property'
        ResultadosEstated = EstatedOwnerInfo(ResultadosRealtorJS,
                                             initialRows, )  ## Hacer el cambio de ResultadosRealtorJS  a ResuladoBrokersInfoJS cuando se agregue la variable 'Type of Property'
        ResultadosEStated
        ############Fin de fnuciones a llamar############
        archivo = f"{directorio}/{Ciudad}.xlsx"
        nombre_nuevo = f"{directorio}/{Ciudad} Just Sold.xlsx"
        os.remove(nombre_nuevo)
        os.rename(archivo, nombre_nuevo)

        eliminar = busca(f'title = "{Ciudad} Just Sold.xlsx"')[0]

        borrar_recuperar(eliminar)

        subir_archivo(f'{Ciudad} Just Sold.xlsx', id_folder)

        print("El archivo se ha actualizado exitosamente en GD")
