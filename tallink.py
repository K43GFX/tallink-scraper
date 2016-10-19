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
query = 'https://booking.tallink.com/?voyageType=SHUTTLE&eveningDeparture=true&withVehicle=false&from=tal&to=sto&adults=4&children=0&juniors=0&youths=0&date=2016-10-28&locale=et&country=EE&marketUntilDate=2017-12-22&_ga=1.98495196.218069809.1475764556'

#Valjumiskuupaev
date = "2016-10-28"

#Millisest summast peab hind vaiksem olema (tavahind, mitte Club One hind)
price = 136

#Kontrollimise intervall minutites
interval = 5

#------------------------------------------------------------
#Kui sul on Ubuntu, siis uue hinna puhul saab skript saata notify-send kaudu teate (testitud 16.04 keskkonnas)
notifications = "true"
#Saada hinnateade iga kontrolli puhul
alert_every_price = "false"
#------------------------------------------------------------

def checkPrice(query, date, price):
	render = webdriver.PhantomJS()
	render.get(query)
	time.sleep(2)
	html_source = render.page_source
	render.close()
	render.quit()
	os.system('pkill -9 phantomjs')

	parser = BeautifulSoup(html_source, 'html.parser')

	last_price = ""
	for hit in parser.findAll(attrs={'datetime' : date}):
		parser = BeautifulSoup(str(hit), 'html.parser')
		hind = parser.find(attrs={'class' : 'price'}).text

		if(int(hind.split(" ")[0]) < price):
			print("\033[91m [" + str(datetime.datetime.now()) + "] - Hind: " + str(hind.split(" ")[0]) + "€ - hind soodsam!")
		else:
			print("\033[93m [" + str(datetime.datetime.now()) + "] - Hind: " + str(hind.split(" ")[0]) + "€ - hind sama või kallim")

		if(notifications == "true"):
			if(int(hind.split(" ")[0]) < price):
				os.system('notify-send "Tallink kruiis" "HIND ON ODAVAM! Uus hind on ' + str(hind.split(" ")[0]) + '€"')
			elif(alert_every_price == "true"):
				os.system('notify-send "Tallink kruiis" "Hetkel on kruiisi hind ' + str(hind.split(" ")[0]) + '€"')


while(1):
	checkPrice(query, date, price)
	print("\033[90mOotan intervalli...");
	time.sleep(interval*60)
