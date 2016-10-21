#!/usr/bin/env python2
# coding=UTF8

# Autor: Karl Erik Õunapuu
# Kuupäev: 19.10.2016
# Kontrollib kas Tallinki Tallinn - Stockholm - Tallinn kruiisil on äkki kajuti hinnad alla läinud

import urllib2
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import datetime
import os

#Tallinki otsingu URL
url = 'https://booking.tallink.com/?voyageType=SHUTTLE&eveningDeparture=true&withVehicle=false&from=tal&to=sto&adults=4&children=0&juniors=0&youths=0&date=2016-10-28&locale=et&country=EE&marketUntilDate=2017-12-22&_ga=1.98495196.218069809.1475764556'

#Millisest summast peab hind vaiksem olema (tavahind, mitte Club One hind)
price = 136

#Kontrollimise intervall minutites
interval = 5

#Kajuti ID, saab veebilehe lähtekoodist
kajut_id = 'A__ALLERGY'

#------------------------------------------------------------
#Kui sul on Ubuntu, siis uue hinna puhul saab skript saata notify-send kaudu teate (testitud 16.04 keskkonnas)
notify= 1
#------------------------------------------------------------

def getSource(url): #veebilehe lähtekoodi hankimine

	#deklareerime brauseri
	render = webdriver.PhantomJS()

	#läheme vaateme Tallinki lehel ringi
	render.get(url)

	#ootame javascripti
	time.sleep(2)

	#avame spetsiaalsete kajutite nimekirja
	render.find_element_by_class_name('irregularCabinsTitle').click()

	#ootame javascripti
	time.sleep(2)

	#võtame terve lehe source
	source = (render.page_source).encode('utf-8')

	#source otsija deklareerimine
	parser = BeautifulSoup(str(source), 'html.parser')

	#otsime välja divi kus on kõik kajutid
	kajutid = parser.findAll(attrs={'class' : 'travelClass'})

	#ainult 1 div saabki olla sellise nimega, lol
	source = kajutid[0]

	#sulgeme lehitseja
	render.close()

	#protsessi lõpetamine
	render.quit()

	#kui raibe elab veel siis enam mitte
	os.system('pkill -9 phantomjs')

	#tagastame kajutite div htmli
	return source


def kajutiStaatus(source, kajut_id):

	#kajutite otsija deklareerimine
	parser = BeautifulSoup(str(source), 'html.parser')

	#otsime välja vastava kajuti
	kajutid = parser.findAll(attrs={'value' : kajut_id})

	#kajuti hinnaotsija deklareerimine
	parser = BeautifulSoup(str(kajutid[0]), 'html.parser')

	#esimene span väärtus annab kajuti hinna / olemasolu
	saadavus = (parser.find('span').text).encode('utf-8')

	if(saadavus == "Välja müüdud"):
		#kajut välja müüdud
		return "false"
	else:
		#kajut saadaval, sebime hinna
		hind = saadavus.split(" ")[0]

		if(notify):
			os.system('notify-send "Tallink kruiis" "Kajut saadaval! Hind: ' + hind + '€"')

		#tagastame hinna
		return hind


def hindAnalyys(hind, maxHind): #hinna analüüsimine, kas suurem või mitte

	#hind langenud
	if(int(hind) < int(maxHind)):
		#kirjutame konsooli teate
		print(str(datetime.datetime.now().time()) + ' - Kajuti hind on madalam - Uus hind: ' + hind + '€')
		if(notify):
			os.system('notify-send "Tallink kruiis" "Kajuti hind madalam! Uus hind: ' + hind + '€"')
	#hind tõusnud
	elif(int(hind) > int(maxHind)):
		#kirjutame konsooli teate
		print(str(datetime.datetime.now().time()) + ' - Kajuti hind on tõusnud- Uus hind: ' + hind + '€')
		if(notify):
			os.system('notify-send "Tallink kruiis" "Kajuti hind tõusnud! Uus hind: ' + hind + '€"')

	#hind sama
	else:
		#kirjutame konsooli teate
		print(str(datetime.datetime.now().time()) + ' - Kajuti hind pole muutunud - hind: ' + hind + '€')

while(1):

	if(kajutiStaatus(getSource(url), kajut_id) == "false"):
		#kajutit pole
		print(str(datetime.datetime.now().time()) + ' - kajut pole saadaval')
	else:
		#kajut saadaval
		hindAnalyys(kajutiStaatus(getSource(url), kajut_id), price)

	print("Ootan intervalli...");
	time.sleep(interval*60)
