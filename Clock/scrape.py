#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import cssutils
import re 

#source = requests.get('https://www.infofunerais.pt/pt/?op=search&pesquisaFalecimentos=1&tipo=&onde=&quem=&onde_txt=vale+de+cam').text
source = requests.get('https://www.infofunerais.pt/pt/funerais.html?id=38026').text
soup =BeautifulSoup(source, 'html5lib')

#print(soup.prettify())

soup2 =  soup.find('span',class_='italic')

print soup.find_all('span',class_='italic').get_text()


"""
nomes = []
fotos = []
datas = []
ids = []
ages = []


class Pessoa:
        name = ""
        photo = ""
        date = ""
        id = ""
	age = ""


for falecimentos in soup.find_all('span',class_='nome'):
#	print(falecimentos.text.strip())
	nomes.append(falecimentos.text.strip())

for result in  soup.find_all('div',attrs={'class':'f_bloc_img','style':True}):
	pattern = r"(?<=url\().*(?='\))"
	url = re.search(pattern, result["style"]).group(0)
	url= url[1:]
#	print (str(url))
	fotos.append(str(url))


for obito in soup.find_all('span',class_='idade'):
#       print(obito.text.strip())
	datas.append(obito.text.strip())


for result in  soup.find_all('div',class_='f_bloc',limit=3):
	for link in result.find_all('a', attrs={'href': re.compile("^https://")}):
		idfinal = link.get('href')[-5:]
		ids.append(idfinal)
#        	print idfinal



um = Pessoa()
um.name = nomes[0]
um.photo = fotos[0]
um.date = datas[0]
um.id = ids[0]
um.age = ""

dois  = Pessoa()
dois.name = nomes[1]
dois.photo = fotos[1]
dois.date = datas[1]
dois.id = ids[1]
dois.age = ""

tres  = Pessoa()
tres.name = nomes[2]
tres.photo = fotos[2]
tres.date = datas[2]
tres.id = ids[2]
tres.age = ""


for id in ids:
#	print id
	soure = requests.get('https://www.infofunerais.pt/pt/funerais.html?id=' +  id).text

	soup2 =BeautifulSoup(soure, 'html5lib')

#print(soup2.prettify())


	for idade in soup2.find_all('span',class_='idade-detail',limit=3):
#        	print(idade.text.strip())
        	ages.append(idade.text.strip())
	

um.age = ages[0]
dois.age = ages[1]
tres.age = ages[2]

print (um.name +  " " + um.photo + " " + um.date + " " + um.id + " " + um.age)
print (dois.name +  " " + dois.photo + " " + dois.date + " " + dois.id + " " + dois.age)
print (tres.name +  " " + tres.photo + " " + tres.date + " " + tres.id + " " + tres.age)




"""
