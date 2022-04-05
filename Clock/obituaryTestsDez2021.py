#!/usr/bin/python
# -*- coding: utf-8 -*-                 # NOQA


import sys
import os
import platform
import signal
import datetime
import time
import json
import locale
import random
from bs4 import BeautifulSoup
import requests
import cssutils
import re
import shutil
import glob

# import urllib
# import re


from subprocess import Popen

#source = requests.get('https://www.infofunerais.pt/pt/?op=search&pesquisaFalecimentos=1&tipo=freguesia&onde=3238&quem=&onde_txt=VILA+CHÃ%2C+VALE+DE+CAMBRA%2C+AVEIRO').text
source = requests.get('https://www.infofunerais.pt/pt/?op=search&pesquisaFalecimentos=1&tipo=&onde=&quem=&onde_txt=vale+de+cambra').text
#source = requests.get('https://www.infofunerais.pt/pt/?op=search&pesquisaFalecimentos=1&tipo=freguesia&onde=3235&quem=&onde_txt=junqueira%2C+VALE+DE+CAMBRA%2C+AVEIRO').text


soup =BeautifulSoup(source, 'html5lib')

### To change all names below
global nomes
global fotos
global datas
global ids
global ages
global adress
global obituaryList
global funeral


def pessoa(nome, photo, date, id, age,adress,funeral):


    global dicionario

    dicionario = {
        "name" : nome,
        "photo" : photo,
        "date" : date,
        "id" : id,
        "age" : age,
        "adress" : adress,
        "funeral" : funeral
        }

    #print dicionario
    obituaryList.append(dicionario)


nomes = []
fotos = []
datas = []
ids = []
ages = []
adress = []
obituaryList = []
funeral = []

for falecimentos in soup.find_all('span',class_='nome',limit=6):
	nomes.append(falecimentos.text)

for result in  soup.find_all('div',attrs={'class':'f_bloc_img','style':True},limit=6):
	pattern = r"(?<=url\().*(?='\))"
	url = re.search(pattern, result["style"]).group(0)
	url= url[1:]
        #print(str(url))
	fotos.append(str(url))


for obito in soup.find_all('span',class_='idade', limit=6):
	datas.append(obito.text)


for result in  soup.find_all('div',class_='f_bloc',limit=6):
	for link in result.find_all('a', attrs={'href': re.compile("^https://")}):
		idfinal = link.get('href')[-5:]
		ids.append(idfinal)

for local in soup.find_all('span',class_='local',limit=6):
	adress.append(local.text)


for id in ids:

	soure = requests.get('https://www.infofunerais.pt/pt/funerais.html?id=' +  id).text

	soup2 =BeautifulSoup(soure, 'html5lib')

	for idade in soup2.find_all('span',class_='idade-detail',limit=6):
            ages.append(idade.text.strip())

for id in ids:

	soure = requests.get('https://www.infofunerais.pt/pt/funerais.html?id=' +  id).text

	soup2 =BeautifulSoup(soure, 'html5lib')
        try:
            funeral.append(soup2.find_all('span',class_='italic')[-1].get_text(strip=True))

        except:
            funeral.append(str("Data e Hora a definir"))


print funeral
#print funeral
#To pass each person collected to method "pessoa"
#for index, nome in enumerate(nomes):
#    pessoa(nome=nomes[index],photo=fotos[index],date=datas[index],id=ids[index],age=ages[index],adress=adress[index],funeral=funeral[index])
