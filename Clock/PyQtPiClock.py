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
#import cssutils
import re
import shutil
import glob
import codecs



import urllib
# import re

from PyQt5 import QtGui, QtCore, QtNetwork, QtWidgets
from PyQt5.QtGui import QPixmap, QBrush, QColor
from PyQt5.QtGui import QPainter, QImage, QFont
from PyQt5.QtCore import QUrl, QThread, pyqtSignal, QObject, QBuffer
from PyQt5.QtCore import Qt, QRunnable
from PyQt5.QtNetwork import QNetworkReply
from PyQt5.QtNetwork import QNetworkRequest
from subprocess import Popen
from pdf2image import convert_from_path, convert_from_bytes


sys.dont_write_bytecode = True
#sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

from GoogleMercatorProjection import getCorners, getPoint, getTileXY, LatLng  # NOQA

#File ApiKeys with tokens to access the weather and radar data
import ApiKeys                                              # NOQA
global objimage2, firsttime 

#Second by second clock definition
def tick():
    global hourpixmap, minpixmap, secpixmap
    global hourpixmap2, minpixmap2, secpixmap2
    global lastmin, lastday, lasttimestr
    global clockrect
    global datex, datex2, datey2, pdy
    global meuBotao

    if Config.DateLocale != "":
        try:
            locale.setlocale(locale.LC_TIME, Config.DateLocale)
        except:
            pass

    now = datetime.datetime.now()
    if Config.digital:
        timestr = Config.digitalformat.format(now)
        if Config.digitalformat.find("%I") > -1:
            if timestr[0] == '0':
                timestr = timestr[1:99]
        if lasttimestr != timestr:
            clockface.setText(timestr.lower())
        lasttimestr = timestr
    else:
        angle = now.second * 6
        ts = secpixmap.size()
        secpixmap2 = secpixmap.transformed(
            QtGui.QMatrix().scale(
                float(clockrect.width()) / ts.height(),
                float(clockrect.height()) / ts.height()
            ).rotate(angle),
            Qt.SmoothTransformation
        )
        sechand.setPixmap(secpixmap2)
        ts = secpixmap2.size()
        sechand.setGeometry(
            clockrect.center().x() - ts.width() / 2,
            clockrect.center().y() - ts.height() / 2,
            ts.width(),
            ts.height()
        )
        if now.minute != lastmin:
            lastmin = now.minute
            angle = now.minute * 6
            ts = minpixmap.size()
            minpixmap2 = minpixmap.transformed(
                QtGui.QMatrix().scale(
                    float(clockrect.width()) / ts.height(),
                    float(clockrect.height()) / ts.height()
                ).rotate(angle),
                Qt.SmoothTransformation
            )
            minhand.setPixmap(minpixmap2)
            ts = minpixmap2.size()
            minhand.setGeometry(
                clockrect.center().x() - ts.width() / 2,
                clockrect.center().y() - ts.height() / 2,
                ts.width(),
                ts.height()
            )

            angle = ((now.hour % 12) + now.minute / 60.0) * 30.0
            ts = hourpixmap.size()
            hourpixmap2 = hourpixmap.transformed(
                QtGui.QMatrix().scale(
                    float(clockrect.width()) / ts.height(),
                    float(clockrect.height()) / ts.height()
                ).rotate(angle),
                Qt.SmoothTransformation
            )
            hourhand.setPixmap(hourpixmap2)
            ts = hourpixmap2.size()
            hourhand.setGeometry(
                clockrect.center().x() - ts.width() / 2,
                clockrect.center().y() - ts.height() / 2,
                ts.width(),
                ts.height()
            )

    dy = Config.digitalformat2.format(now)
    if Config.digitalformat2.find("%I") > -1:
        if dy[0] == '0':
            dy = dy[1:99]
    if dy != pdy:
        pdy = dy
        datey2.setText(dy)

    if now.day != lastday:
        lastday = now.day
        # date
        sup = 'th'
        if (now.day == 1 or now.day == 21 or now.day == 31):
            sup = 'st'
        if (now.day == 2 or now.day == 22):
            sup = 'nd'
        if (now.day == 3 or now.day == 23):
            sup = 'rd'
        if Config.DateLocale != "":
            sup = ""
        ds = "{0:%A}, {0.day}<sup>{1}</sup>  {0:%B} {0.year}".format(now, sup)
        ds2 = "{0:%A}, {0.day}<sup>{1}</sup> {0:%B} {0.year}".format(now, sup)
        datex.setText(ds.title())
        if Config.AppMode == "teste":
            ds = "{0:%d}<sup>{1}</sup>/{0:%m}/{0.year}".format(now, sup)
            datex2.setText(ds.title())
        else:
            datex2.setText(ds2.title())

#Internal temperature definition
def tempfinished():
    global tempreply, temp
    if tempreply.error() != QNetworkReply.NoError:
        return
    tempstr = str(tempreply.readAll())
    tempdata = json.loads(tempstr)
    if tempdata['temp'] == '':
        return
    if Config.metric:
        s = Config.LInsideTemp + \
            "%3.1f" % ((float(tempdata['temp']) - 32.0) * 5.0 / 9.0)
        if tempdata['temps']:
            if len(tempdata['temps']) > 1:
                s = ''
                for tk in tempdata['temps']:
                    s += ' ' + tk + ':' + \
                        "%3.1f" % (
                            (float(tempdata['temps'][tk]) - 32.0) * 5.0 / 9.0)
    else:
        s = Config.LInsideTemp + tempdata['temp']
        if tempdata['temps']:
            if len(tempdata['temps']) > 1:
                s = ''
                for tk in tempdata['temps']:
                    s += ' ' + tk + ':' + tempdata['temps'][tk]
    temp.setText(s)

#Unit onversions
def tempm(f):
    return (f - 32) / 1.8


def speedm(f):
    return f * 0.621371192


def pressi(f):
    return f * 0.029530


def heightm(f):
    return f * 25.4

#Moon Phases
def phase(f):
    pp = Config.Lmoon1          # 'New Moon'
    if (f > 0.9375):
            pp = Config.Lmoon1  # 'New Moon'
    elif (f > 0.8125):
            pp = Config.Lmoon8  # 'Waning Crecent'
    elif (f > 0.6875):
            pp = Config.Lmoon7  # 'Third Quarter'
    elif (f > 0.5625):
            pp = Config.Lmoon6  # 'Waning Gibbous'
    elif (f > 0.4375):
            pp = Config.Lmoon5  # 'Full Moon'
    elif (f > 0.3125):
            pp = Config.Lmoon4  # 'Waxing Gibbous'
    elif (f > 0.1875):
            pp = Config.Lmoon3  # 'First Quarter'
    elif (f > 0.0625):
            pp = Config.Lmoon2  # 'Waxing Crescent'
    return pp

#Wind bearing
def bearing(f):
    wd = 'N'
    if (f > 22.5):
        wd = 'NE'
    if (f > 67.5):
        wd = 'E'
    if (f > 112.5):
        wd = 'SE'
    if (f > 157.5):
        wd = 'S'
    if (f > 202.5):
        wd = 'SW'
    if (f > 247.5):
        wd = 'W'
    if (f > 292.5):
        wd = 'NW'
    if (f > 337.5):
        wd = 'N'
    return wd

#Get inside temperature
def gettemp():
    global tempreply
    host = 'localhost'
    if platform.uname()[1] == 'KW81':
        host = 'piclock.local'  # this is here just for testing
    r = QUrl('http://' + host + ':48213/temp')
    r = QNetworkRequest(r)
    tempreply = manager.get(r)
    tempreply.finished.connect(tempfinished)

#Define text for labels of obituary section after obituary photo defined

###To change name of method and variables inside
###To conclude with remaining labels

def obituaryPhotoDisplayFinished(photoNumber):

        obituaryPerson = obituaryList[photoNumber]
        obituaryPersonNameLabel.setText(obituaryPerson["name"])


        obituaryPersonDateAndAgeLabel.setText(obituaryPerson["date"] + "   " + "Idade: " + obituaryPerson["age"])

        #Remove 17 characters from end, ", vale de cambra"
        ##2020 version
        #obituaryPersonAdressLabel.setText((obituaryPerson["adress"][:-44])[33 :])
        obituaryPersonAdressLabel.setText((obituaryPerson["adress"][:-17]))
        
        ###print (str(len(obituaryPerson["funeral"])))

        if (len(obituaryPerson["funeral"]) < 45):
            obituaryPersonFuneralLabel.setText(obituaryPerson["funeral"] + "\n" + "Hora a definir")
        else:
            SepararFuneral1 = obituaryPerson["funeral"][:-19]
            SepararFuneral2 = obituaryPerson["funeral"][-17:]
#        print SepararFuneral1
#        print SepararFuneral2

            obituaryPersonFuneralLabel.setText(SepararFuneral1 + "\n" + SepararFuneral2 )



#Definition of weather conditions after weatehr request
def wxfinished():
    global wxreply, wxdata
    global wxicon, temper, wxdesc, press, humidity
    global wind, wind2, wdate, bottom, forecast
    global wxicon2, temper2, wxdesc

    attribution2.setText("")
    try:
        # For Python 3.0 and later
        from urllib.request import urlopen
    except ImportError:
        # Fall back to Python 2's urllib2
        from urllib2 import urlopen

    myurl=  (str(wxurl))
    
    #Try to get weather data online, if not possible use test weather
    
    try:
        response = urlopen(myurl)
        data = response.read().decode("utf-8")
        wxdata = json.loads(data)
        f = wxdata['currently']
    except:
        print ("Not possible to colect weather data")
        
        with open('weatherSample.txt') as json_file:
            wxdata = json.load(json_file)
            f = wxdata['currently']

    
    wxiconpixmap = QtGui.QPixmap(Config.icons + "/" + f['icon'] + ".png")
    wxicon.setPixmap(wxiconpixmap.scaled(
        wxicon.width(), wxicon.height(), Qt.IgnoreAspectRatio,
        Qt.SmoothTransformation))
    #wxicon2.setPixmap(wxiconpixmap.scaled(wxicon.width(),wxicon.height(),Qt.IgnoreAspectRatio,Qt.SmoothTransformation))
    wxdesc.setText(f['summary'])
    #wxdesc2.setText(f['summary'])

    if Config.metric:
        temper.setText('%.1f' % (tempm(f['temperature'])) + u'°C')
        #temper2.setText('%.1f' % (tempm(f['temperature'])) + u'°C')
        press.setText(Config.LPressure + '%.1f' % f['pressure'] + 'mb')
        humidity.setText(Config.LHumidity + '%.0f%%' % (f['humidity']*100.0))
        wd = bearing(f['windBearing'])
        if Config.wind_degrees:
            wd = str(f['windBearing'])
	# + u'°'
        wind.setText(Config.LWind +
                     wd + ' ' +
                     '%.1f' % (speedm(f['windSpeed'])) + 'kmh' +
                     Config.Lgusting +
                     '%.1f' % (speedm(f['windGust'])) + 'kmh')
        wind2.setText(Config.LFeelslike +
                      '%.1f' % (tempm(f['apparentTemperature'])) + u'°C')
        wdate.setText("Last Weather Update {0:%H:%M}".format(datetime.datetime.fromtimestamp(
            int(f['time']))))

    else:
        temper.setText('%.1f' % (f['temperature']) + u'°F')
        #temper2.setText('%.1f' % (f['temperature']) + u'°F')
        press.setText(Config.LPressure + '%.2f' % pressi(f['pressure']) + 'in')
        humidity.setText(Config.LHumidity + '%.0f%%' % (f['humidity']*100.0))
        wd = bearing(f['windBearing'])
        if Config.wind_degrees:
            wd = str(f['windBearing']) + u'°'
        wind.setText(Config.LWind +
                     wd + ' ' +
                     '%.1f' % (f['windSpeed']) + 'mph' +
                     Config.Lgusting +
                     '%.1f' % (f['windGust']) + 'mph')
        wind2.setText(Config.LFeelslike +
                      '%.1f' % (f['apparentTemperature']) + u'°F')
        wdate.setText("{0:%H:%M}".format(datetime.datetime.fromtimestamp(
            int(f['time']))))


    bottomText = ""
    if "sunriseTime" in wxdata["daily"]["data"][0]:
        bottomText += (Config.LSunRise +
                       "{0:%H:%M}".format(datetime.datetime.fromtimestamp(
                        wxdata["daily"]["data"][0]["sunriseTime"])) +
                       Config.LSet +
                       "{0:%H:%M}".format(datetime.datetime.fromtimestamp(
                        wxdata["daily"]["data"][0]["sunsetTime"])))

    if "moonPhase" in wxdata["daily"]["data"][0]:
        bottomText += (Config.LMoonPhase +
                       phase(wxdata["daily"]["data"][0]["moonPhase"]))

    bottom.setText(bottomText)

    for i in range(0, 3):
        f = wxdata['hourly']['data'][i * 3 + 2]
        fl = forecast[i]
        icon = fl.findChild(QtWidgets.QLabel, "icon")
        wxiconpixmap = QtGui.QPixmap(
            Config.icons + "/" + f['icon'] + ".png")
        icon.setPixmap(wxiconpixmap.scaled(
            icon.width(),
            icon.height(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation))
        wx = fl.findChild(QtWidgets.QLabel, "wx")
        day = fl.findChild(QtWidgets.QLabel, "day")
        dayText =  ("{0:%A %H:%M%p}".format(datetime.datetime.fromtimestamp(int(f['time']))))
        day.setText (dayText.title())
        s = ''
        pop = 0
        ptype = ''
        paccum = 0
        if ('precipProbability' in f):
            pop = float(f['precipProbability']) * 100.0
        if ('precipAccumulation' in f):
            paccum = float(f['precipAccumulation'])
        if ('precipType' in f):
            ptype = f['precipType']

        if (pop > 0.0 or ptype != ''):
            s += '%.0f' % pop + '% '
        if Config.metric:
            if (ptype == 'snow'):
                if (paccum > 0.05):
                    s += Config.LSnow + '%.0f' % heightm(paccum) + 'mm '
            else:
                if (paccum > 0.05):
                    s += Config.LRain + '%.0f' % heightm(paccum) + 'mm '
            s += '%.0f' % tempm(f['temperature']) + u'°C'
        else:
            if (ptype == 'snow'):
                if (paccum > 0.05):
                    s += Config.LSnow + '%.0f' % paccum + 'in '
            else:
                if (paccum > 0.05):
                    s += Config.LRain + '%.0f' % paccum + 'in '
            s += '%.0f' % (f['temperature']) + u'°F'

        wx.setStyleSheet("#wx { font-size: " + str(int(25 * xscale)) + "px; }")
        wx.setText(f['summary'] + "\n" + s)

    for i in range(3, 9):
        f = wxdata['daily']['data'][i - 3]
        fl = forecast[i]
        icon = fl.findChild(QtWidgets.QLabel, "icon")
        wxiconpixmap = QtGui.QPixmap(Config.icons + "/" + f['icon'] + ".png")
        icon.setPixmap(wxiconpixmap.scaled(
            icon.width(),
            icon.height(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation))
        wx = fl.findChild(QtWidgets.QLabel, "wx")
        day = fl.findChild(QtWidgets.QLabel, "day")
        dayText = ("{0:%A}".format(datetime.datetime.fromtimestamp(
            int(f['time']))))
        day.setText (dayText.title())
        s = ''
        pop = 0
        ptype = ''
        paccum = 0
        if ('precipProbability' in f):
            pop = float(f['precipProbability']) * 100.0
        if ('precipAccumulation' in f):
            paccum = float(f['precipAccumulation'])
        if ('precipType' in f):
            ptype = f['precipType']

        if (pop > 0.05 or ptype != ''):
            s += '%.0f' % pop + '% '
        if Config.metric:
            if (ptype == 'snow'):
                if (paccum > 0.05):
                    s += Config.LSnow + '%.0f' % heightm(paccum) + 'mm '
            else:
                if (paccum > 0.05):
                    s += Config.LRain + '%.0f' % heightm(paccum) + 'mm '
            s += 'M.' + '%.0f' % tempm(f['temperatureHigh']) + ' m.' + \
                 '%.0f' % tempm(f['temperatureLow'])
        else:
            if (ptype == 'snow'):
                if (paccum > 0.05):
                    s += Config.LSnow + '%.1f' % paccum + 'in '
            else:
                if (paccum > 0.05):
                    s += Config.LRain + '%.1f' % paccum + 'in '
            s += 'M.' + '%.0f' % f['temperatureHigh'] + ' m.' + \
                 '%.0f' % f['temperatureLow']

        wx.setStyleSheet("#wx { font-size: " + str(int(19 * xscale)) + "px; }")
        wx.setText(f['summary'] + "\n" + s)

#Get weather response
def getwx():
    global wxurl
    global wxreply
#    print "getting current and forecast:" + time.ctime()
    wxurl = 'https://api.darksky.net/forecast/' + \
        ApiKeys.dsapi + \
        '/'
    wxurl += str(Config.location.lat) + ',' + \
        str(Config.location.lng)
    wxurl += '?units=us&lang=' + Config.Language.lower()
    wxurl += '&r=' + str(random.random())
    wxfinished()


#Get weatehr data
def getallwx():
    getwx()


#START FUNCTION
#will request to update all weatehr, inside temperature, run clock, all start all slideshows
#important to define order of methods
def qtstart():
    global ctimer, wxtimer, temptimer
    global manager
    global objradar1
    global objradar2
    global meuBotao

    meuBotao = False
    ###print ("Meu botao inicial e: " + str(meuBotao))

    getallwx()

    gettemp()


    objradar2.start(Config.radar_refresh * 60)
    objradar2.wxstart()
    
    objimage5.startBible(Config.bibleTime)

    ctimer = QtCore.QTimer()
    ctimer.timeout.connect(tick)
    ctimer.start(1000)

    wxtimer = QtCore.QTimer()
    wxtimer.timeout.connect(getallwx)
    wxtimer.start(1000 * Config.weather_refresh *
                  60 + random.uniform(1000, 10000))

    temptimer = QtCore.QTimer()
    temptimer.timeout.connect(gettemp)
    temptimer.start(1000 * 10 * 60 + random.uniform(1000, 10000))

    if Config.useslideshow:
        objimage1.start(Config.slide_time)

###Change name of donwloadPhotos
    if Config.obituaryPhotos:
###Change name of time_to_fetch to time_to_scape_obituary
        objimage3.startFetching(Config.time_to_fetch)

    #TO REWORK
    #if Config.usephotoshow:
        #objimage2.startPhoto(Config.photo_time)
        #print ("user Has photoshow")





## Class to run Main Slideshow (in the center of screen)
class SlideShow(QtWidgets.QLabel):
    def __init__(self, parent, rect, myname):
        self.myname = myname
        self.rect = rect
        QtWidgets.QLabel.__init__(self, parent)

        self.pause = False
        self.count = 0
        self.img_list = []
        self.img_inc = 1

        self.get_images()
        self.setObjectName("slideShow")
        self.setGeometry(rect)
        self.setStyleSheet("#slideShow { background-color: " +
                           Config.slide_bg_color + "; }")
        self.setAlignment(Qt.AlignHCenter | Qt.AlignCenter)

    def start(self, interval):
        #print (str(interval))
        #print "method start called vai chamar run_ss"
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run_ss)
        self.timer.start(1000 * interval + random.uniform(1, 10))
        self.run_ss()

    def stop(self):
        try:
            self.timer.stop()
            self.timer = None
        except Exception:
            pass

    def run_ss(self):
        self.get_images()
        self.switch_image()


    def switch_image(self):
        if self.img_list:
            if not self.pause:
                self.count += self.img_inc
                if self.count >= len(self.img_list):
                    self.count = 0
		#print str(self.img_list[self.count])
                self.show_image(self.img_list[self.count])
                self.img_inc = 1

    def show_image(self, image):
        image = QtGui.QImage(image)
        bg = QtGui.QPixmap.fromImage(image)
        self.setPixmap(bg.scaled(
                self.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation))

    def get_images(self):
            self.get_local(Config.slides)


    def play_pause(self):
        if not self.pause:
            self.pause = True
        else:
            self.pause = False

    def prev_next(self, direction):
        self.img_inc = direction
        self.timer.stop()
        self.switch_image()
        self.timer.start()

    #get local images in slideshow folder
    def get_local(self, path):
        try:
            dirContent = os.listdir(path)
        except OSError:
            print("path '%s' doesn't exists." % path)
            
        self.img_list = []
        for each in dirContent:
            fullFile = os.path.join(path, each)
            if os.path.isfile(fullFile) and (fullFile.lower().endswith('png')
               or fullFile.lower().endswith('jpg')):
                    self.img_list.append(fullFile)




#Class to fetch all data
##To change name to Scrape_obituary
class Fetch(QtCore.QObject):
    
    ###print (datetime.datetime.now())

    signalStatus = QtCore.pyqtSignal(str)

    def startFetching(self, interval):
        global firsttime
        print ("Manda iniciar a pesquisa de falecimentos")
        
        
        

        
        self.createWorkerThread()
        self._connectSignals()
        
        
        if firsttime == True:
            print ("1st")
            self.inicioFalecimentos() 

            
            firsttime= False
        else:
            print ("2nd")
            intervalo = interval
   
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.worker.fetch_photos)
        self.timer.start(1000 * interval + random.uniform(1, 10))

            
    def createWorkerThread(self):
        self.worker = Worker()
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.start()
        
    def _connectSignals(self):
        
        self.worker.finished.connect(self.updateStatus)
        self.thread.started.connect(self.worker.fetch_photos)


            
    def updateStatus (self):
        print ("Actualiza ecra com novos dados")
        objimage2.play_pause()
        objimage2.startPhoto(Config.photo_time)
        objimage4.play_pause()
        objimage4.startPhoto(Config.photo_time)


    def inicioFalecimentos(self):
        print ("Actualizando Falecimentos versao inicial")
        


        #Obituary source
        ### To change to config file
        if meuBotao == False:
            source = requests.get('https://www.infofunerais.pt/pt/?op=search&pesquisaFalecimentos=1&tipo=&onde=&quem=&onde_txt=vale+de+cambra').text

        if meuBotao == True:
            print ("VILA CHA")
            source = requests.get('https://www.infofunerais.pt/pt/?op=search&pesquisaFalecimentos=1&tipo=freguesia&onde=3238&quem=&onde_txt=VILA+CHÃ%2C+VALE+DE+CAMBRA%2C+AVEIRO').text

        soup = BeautifulSoup(source, 'html5lib')

### To change all names below
        global nomes
        global fotos
        global datas
        global ids
        global ages
        global adress
        global obituaryList
        global funeral
        global paperLinks


        nomes = []
        fotos = []
        datas = []
        ids = []
        ages = []
        adress = []
        obituaryList = []
        funeral = []
        paperLinks = []



        print (datetime.datetime.now())
        print ("Inicia o processo de dados de falecimentos")
        
        for falecimentos in soup.find_all('span',class_='nome',limit=Config.limit):
        	nomes.append(falecimentos.text)

        for result in  soup.find_all('div',attrs={'class':'f_bloc_img','style':True},limit=Config.limit):
        	pattern = r"(?<=url\().*(?='\))"
        	url = re.search(pattern, result["style"]).group(0)
        	url= url[1:]
        	fotos.append(str(url))
            


        for obito in soup.find_all('span',class_='idade', limit=Config.limit):
        	datas.append(obito.text)


        for result in  soup.find_all('div',class_='f_bloc',limit=Config.limit):
        	for link in result.find_all('a', attrs={'href': re.compile("^https://")}):
        		idfinal = link.get('href')[-5:]
        		ids.append(idfinal)

        for local in soup.find_all('span',class_='local',limit=Config.limit):
        	adress.append(local.text)

        for id in ids:

        	soure = requests.get('https://www.infofunerais.pt/pt/funerais.html?id=' +  id).text

        	soup2 =BeautifulSoup(soure, 'html5lib')

        	for idade in soup2.find_all('span',class_='idade-detail',limit=Config.limit):
                    ages.append(idade.text.strip())

        for id in ids:
            soure = requests.get('https://www.infofunerais.pt/pt/funerais.html?id=' +  id).text
            soup2 =BeautifulSoup(soure, 'html5lib')
            try:
           	    funeral.append(soup2.find_all('span',class_='italic')[-1].get_text(strip=True))
            except:
                funeral.append(str("Data a definir"))
                
        for id in ids:
            soure = requests.get('https://www.infofunerais.pt/pt/funerais.html?id=' +  id).text
            soup2 =BeautifulSoup(soure, 'html5lib')
            for result in soup2.find_all("ul", {"id": "folhetos"}):
                url = re.findall(r'(?<=<a href=")[^"]*',str(result))
                url1 = (str(url)[2:][:-2])
                print (url1)
                paperLinks.append(url1)
                
                
                
	    #To pass each person collected to method "pessoa"
        for index, nome in enumerate(nomes):
            pessoa(nome=nomes[index],photo=fotos[index],date=datas[index],id=ids[index],age=ages[index],adress=adress[index],funeral=funeral[index], paperlink=paperLinks[index])
        print (datetime.datetime.now())
        print ("Termina o processo de dados falecimentos ")

        for photo in fotos:
            i = fotos.index(photo)
            extensao = photo[-3:]
    	    #to convert jpeg to jpg
            if extensao == "peg":
                extensao = "jpg"

	    #link to save new picture
            link = ("/home/pi/PiClock/Clock/images/photoshow/{}.{}".format(str(i),extensao))
            linkReduced = link[-5:]
            linkReduced2 = linkReduced [:1]

	    #old picture link
            fil = glob.glob('/home/pi/PiClock/Clock/images/photoshow/{}*'.format(str(i)))

	    #to check for old picture and delete to later replace for new one
            if linkReduced2==str(i): #check picture number
                if (fil): #check if folder is not empty
                    if (os.path.isfile(fil[0])): #pick old picture
                        os.unlink(fil[0]) #delete old picture
                else:
                    print ("fil is empty")
            else:
                print ("Old picture link not found")
            f = open(link,'wb')
            f.write(requests.get(photo).content)
            f.close()
        
        
        images=[]
        for paperlink in paperLinks:
            i = paperLinks.index(paperlink)
            extensao = paperlink[-3:]
            

    	
	    #link to save new 
            link = ("/home/pi/PiClock/Clock/images/paperlinks/{}.{}".format(str(i),extensao))
            linkReduced = link[-5:]
            linkReduced2 = linkReduced [:1]
            
        
	    #old picture link
            fil = glob.glob('/home/pi/PiClock/Clock/images/paperlinks/{}*'.format(str(i)))

	    #to check for old picture and delete to later replace for new one
            if linkReduced2==str(i): #check picture number
                if (fil): #check if folder is not empty
                    if (os.path.isfile(fil[0])): #pick old picture
                        os.unlink(fil[0]) #delete old picture
                else:
                    print ("fil is empty")
            else:
                print ("Old picture link not found")
            f = open(link,'wb')
            f.write(requests.get(paperlink).content)
            print (str(link[-3:]))
            newimage = convert_from_path(link)
            for image in newimage:
                newimage[0].save(link[:-3]+"png", 'PNG')
            f.close()            


        #print ("all photos added")
        

        
        print ("Dados iniciais de falecimentos prontos")
        self.updateStatus()
        
# Step 1: Create a worker class
class Worker(QObject):
    finished = pyqtSignal()
    signalStatus = QtCore.pyqtSignal(str)
    
    def __init__(self, *args, **kwargs):
        QThread.__init__(self, *args, **kwargs)

    def fetch_photos(self):
        print ("Actualizando Falecimentos thread")
        objimage2.play_pause()
        objimage4.play_pause()


        #Obituary source
        ### To change to config file
        if meuBotao == False:
            source = requests.get('https://www.infofunerais.pt/pt/?op=search&pesquisaFalecimentos=1&tipo=&onde=&quem=&onde_txt=vale+de+cambra').text

        if meuBotao == True:
            print ("VILA CHA")
            source = requests.get('https://www.infofunerais.pt/pt/?op=search&pesquisaFalecimentos=1&tipo=freguesia&onde=3238&quem=&onde_txt=VILA+CHÃ%2C+VALE+DE+CAMBRA%2C+AVEIRO').text

        soup = BeautifulSoup(source, 'html5lib')

### To change all names below
        global nomes
        global fotos
        global datas
        global ids
        global ages
        global adress
        global obituaryList
        global funeral
        global paperLinks


        nomes = []
        fotos = []
        datas = []
        ids = []
        ages = []
        adress = []
        obituaryList = []
        funeral = []
        paperLinks = []



        print (datetime.datetime.now())
        print ("Inicia o processo de dados de falecimentos")
        
        for falecimentos in soup.find_all('span',class_='nome',limit=Config.limit):
        	nomes.append(falecimentos.text)

        for result in  soup.find_all('div',attrs={'class':'f_bloc_img','style':True},limit=Config.limit):
        	pattern = r"(?<=url\().*(?='\))"
        	url = re.search(pattern, result["style"]).group(0)
        	url= url[1:]
        	fotos.append(str(url))
            


        for obito in soup.find_all('span',class_='idade', limit=Config.limit):
        	datas.append(obito.text)


        for result in  soup.find_all('div',class_='f_bloc',limit=Config.limit):
        	for link in result.find_all('a', attrs={'href': re.compile("^https://")}):
        		idfinal = link.get('href')[-5:]
        		ids.append(idfinal)

        for local in soup.find_all('span',class_='local',limit=Config.limit):
        	adress.append(local.text)

        for id in ids:

        	soure = requests.get('https://www.infofunerais.pt/pt/funerais.html?id=' +  id).text

        	soup2 =BeautifulSoup(soure, 'html5lib')

        	for idade in soup2.find_all('span',class_='idade-detail',limit=Config.limit):
                    ages.append(idade.text.strip())

        for id in ids:
            soure = requests.get('https://www.infofunerais.pt/pt/funerais.html?id=' +  id).text
            soup2 =BeautifulSoup(soure, 'html5lib')
            try:
           	    funeral.append(soup2.find_all('span',class_='italic')[-1].get_text(strip=True))
            except:
                funeral.append(str("Data a definir"))
                
        for id in ids:
            soure = requests.get('https://www.infofunerais.pt/pt/funerais.html?id=' +  id).text
            soup2 =BeautifulSoup(soure, 'html5lib')
            for result in soup2.find_all("ul", {"id": "folhetos"}):
                url = re.findall(r'(?<=<a href=")[^"]*',str(result))
                url1 = (str(url)[2:][:-2])
                print (url1)
                paperLinks.append(url1)
                
                
                
	    #To pass each person collected to method "pessoa"
        for index, nome in enumerate(nomes):
            pessoa(nome=nomes[index],photo=fotos[index],date=datas[index],id=ids[index],age=ages[index],adress=adress[index],funeral=funeral[index], paperlink=paperLinks[index])
        print (datetime.datetime.now())
        print ("Termina o processo de dados falecimentos ")

        for photo in fotos:
            i = fotos.index(photo)
            extensao = photo[-3:]
    	    #to convert jpeg to jpg
            if extensao == "peg":
                extensao = "jpg"

	    #link to save new picture
            link = ("/home/pi/PiClock/Clock/images/photoshow/{}.{}".format(str(i),extensao))
            linkReduced = link[-5:]
            linkReduced2 = linkReduced [:1]

	    #old picture link
            fil = glob.glob('/home/pi/PiClock/Clock/images/photoshow/{}*'.format(str(i)))

	    #to check for old picture and delete to later replace for new one
            if linkReduced2==str(i): #check picture number
                if (fil): #check if folder is not empty
                    if (os.path.isfile(fil[0])): #pick old picture
                        os.unlink(fil[0]) #delete old picture
                else:
                    print ("fil is empty")
            else:
                print ("Old picture link not found")
            f = open(link,'wb')
            f.write(requests.get(photo).content)
            f.close()
        
        
        images=[]
        for paperlink in paperLinks:
            i = paperLinks.index(paperlink)
            extensao = paperlink[-3:]
            

    	
	    #link to save new 
            link = ("/home/pi/PiClock/Clock/images/paperlinks/{}.{}".format(str(i),extensao))
            linkReduced = link[-5:]
            linkReduced2 = linkReduced [:1]
            
        
	    #old picture link
            fil = glob.glob('/home/pi/PiClock/Clock/images/paperlinks/{}*'.format(str(i)))

	    #to check for old picture and delete to later replace for new one
            if linkReduced2==str(i): #check picture number
                if (fil): #check if folder is not empty
                    if (os.path.isfile(fil[0])): #pick old picture
                        os.unlink(fil[0]) #delete old picture
                else:
                    print ("fil is empty")
            else:
                print ("Old picture link not found")
            f = open(link,'wb')
            f.write(requests.get(paperlink).content)
            print (str(link[-3:]))
            newimage = convert_from_path(link)
            for image in newimage:
                newimage[0].save(link[:-3]+"png", 'PNG')
            f.close()                    

        
        print ("Dados thread falecimentos prontos")
    
        self.finished.emit()



## Class to run BibleSlideshow (frame2)
class BibleSlide(QtWidgets.QLabel):


    def __init__(self, parent, rect, myname):
        self.myname = myname
        self.rect = rect
        QtWidgets.QLabel.__init__(self, parent)

        self.pause = True
        self.count = 0
        self.img_list = []
        self.img_inc = 1

        self.setObjectName("slideShow")
        self.setGeometry(rect)
        self.setStyleSheet("#slideShow { background-color: " +
                           Config.photo_bg_color + "; }")
        self.setAlignment(Qt.AlignHCenter | Qt.AlignCenter)

    def startBible(self, interval):
        print ("startBible")
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run_bible)
        self.timer.start(1000 * interval + random.uniform(1, 10))
        self.run_bible()

    def stop(self):
        try:
            self.timer.stop()
            self.timer = None
            print ("stopped startPhoto")
        except Exception:
            pass

    def run_bible(self):
        #print ("run bible")
        self.get_chapter()



    def show_chapter(self, image):
        wxdesc2.setText(image)
        return


    def prev_next(self, direction):
        self.img_inc = direction
        self.timer.stop()
        self.get_chapter()
        self.timer.start()

    def get_chapter(self):




        with open('acf.json') as f:
            content = f.read()
            if content.startswith(u'\ufeff'):
                content = content.encode('utf8')[3:].decode('utf8')
            
            d = json.loads(content)
            
        #n = random.random()
        numeroLivros=len(d)
        livroRandom = random.randint(0, len(d) -1)
        
        print (str(livroRandom))
        testee = d[livroRandom]['chapters']
        print ("teste lengt" + str(len(testee)))
        numeroCap = random.randint(0, len(testee)-1 )
        print (str(numeroCap))
        testef = (d[livroRandom]['chapters'][numeroCap])

        textocomp= ""
        for line in testef:
            #textocomp = textocomp + '\n' + line
            textocomp = textocomp  + line

        self.show_chapter(textocomp)
        #print (textocomp)



        




## Class to run Obituary Slideshow (in the left of screen)
class ObituarySlide(QtWidgets.QLabel):


    def __init__(self, parent, rect, myname):
        self.myname = myname
        self.rect = rect
        QtWidgets.QLabel.__init__(self, parent)

        self.pause = True
        self.count = 0
        self.img_list = []
        self.img_inc = 1

        self.setObjectName("slideShow")
        self.setGeometry(rect)
        self.setStyleSheet("#slideShow { background-color: " +
                           Config.photo_bg_color + "; }")
        self.setAlignment(Qt.AlignHCenter | Qt.AlignCenter)

    def startPhoto(self, interval):
        ###print ("startPhoto")
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.run_ss2)
        self.timer.start(1000 * interval + random.uniform(1, 10))
        self.run_ss2()

    def stop(self):
        try:
            self.timer.stop()
            self.timer = None
            print ("stopped startPhoto")
        except Exception:
            pass

    def run_ss2(self):
        #print ("run ss2")
        self.get_images()
        self.switch_image()


    def switch_image(self):
        print ("Altera pessoa na janela falecimentos")

        if self.img_list:
            if not self.pause:
                self.count += self.img_inc
                if self.count >= len(self.img_list):
                 
                    self.count = 0
                #Mostra imagem no obituario frame1
                if self.myname == "image2":
                    self.show_image(self.img_list[self.count])
                #Mostra folha obito frame 2
                else:
                    self.show_image(self.img_list[self.count])
                    
		#to get number of photo based on saved name
		#select last 5 characters, remove the . and extension (3chars)
	        #print ((self.img_list[self.count])[-5:])[:1]
		#this variable is the number of the photo to be passed as index for all the arrays of data of person in obituary
                self.img_inc = 1
                try:
                    obituaryPhotoNumber = int(((self.img_list[self.count])[-5:])[:1])
                    obituaryPhotoDisplayFinished(obituaryPhotoNumber)
                except:
                    print ("Ainda nao tem fotos de falecimentos")
                
        else:
            print ("No image Available in image List")

    def show_image(self, image):
        image = QtGui.QImage(image)

        bg = QtGui.QPixmap.fromImage(image)
        self.setPixmap(bg.scaled(
                self.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation))

    def get_images(self):
        if self.myname == "image2":
            self.get_local(Config.photos)
        else:
            self.get_local(Config.paperLinks)



    def play_pause(self):
        if not self.pause:
            self.pause = True

        else:
            self.pause = False


    def prev_next(self, direction):
        self.img_inc = direction
        self.timer.stop()
        self.switch_image()
        self.timer.start()

    def get_local(self, path):

        try:
            dirContent = os.listdir(path)
        except OSError:
            print("path '%s' doesn't exists." % path)

        self.img_list = []
        for each in dirContent:
            fullFile = os.path.join(path, each)
            if os.path.isfile(fullFile) and (fullFile.lower().endswith('png')
               or fullFile.lower().endswith('jpg')):
                    self.img_list.append(fullFile)



        



#Method do receive obituary persons 1 by 1 and convert it into dictionary
#Create list with all dictinary
#List will be ordered according scrapping
### To rework, is it neede d all conversion from array do dict.......
def pessoa(nome, photo, date, id, age,adress,funeral,paperlink):


    global dicionario

    dicionario = {
        "name" : nome,
        "photo" : photo,
        "date" : date,
        "id" : id,
        "age" : age,
        "adress" : adress,
        "funeral" : funeral,
        "paperlink": paperlink
        }

    #print dicionario
    obituaryList.append(dicionario)


#Radar definition
class Radar(QtWidgets.QLabel):

    def __init__(self, parent, radar, rect, myname):
        global xscale, yscale
        self.myname = myname
        self.rect = rect
        self.anim = 5
        self.zoom = radar["zoom"]
        self.point = radar["center"]
        self.radar = radar
        self.baseurl = self.mapurl(radar, rect)
#        print "map base url: " + self.baseurl
        QtWidgets.QLabel.__init__(self, parent)
        self.interval = Config.radar_refresh * 60
        self.lastwx = 0
        self.retries = 0
        self.corners = getCorners(self.point, self.zoom,
                                  rect.width(), rect.height())
        self.baseTime = 0
        self.cornerTiles = {
         "NW": getTileXY(LatLng(self.corners["N"],
                                self.corners["W"]), self.zoom),
         "NE": getTileXY(LatLng(self.corners["N"],
                                self.corners["E"]), self.zoom),
         "SE": getTileXY(LatLng(self.corners["S"],
                                self.corners["E"]), self.zoom),
         "SW": getTileXY(LatLng(self.corners["S"],
                                self.corners["W"]), self.zoom)
        }
        self.tiles = []
        self.tiletails = []
        self.totalWidth = 0
        self.totalHeight = 0
        self.tilesWidth = 0
        self.tilesHeight = 0

        self.setObjectName("radar")
        self.setGeometry(rect)
        self.setStyleSheet("#radar { background-color: grey; }")
        self.setAlignment(Qt.AlignCenter)

        self.wwx = QtWidgets.QLabel(self)
        self.wwx.setObjectName("wx")
        self.wwx.setStyleSheet("#wx { background-color: transparent; }")
        self.wwx.setGeometry(0, 0, rect.width(), rect.height())

        self.wmk = QtWidgets.QLabel(self)
        self.wmk.setObjectName("mk")
        self.wmk.setStyleSheet("#mk { background-color: transparent; }")
        self.wmk.setGeometry(0, 0, rect.width(), rect.height())

        for y in range(int(self.cornerTiles["NW"]["Y"]),
                       int(self.cornerTiles["SW"]["Y"])+1):
            self.totalHeight += 256
            self.tilesHeight += 1
            for x in range(int(self.cornerTiles["NW"]["X"]),
                           int(self.cornerTiles["NE"]["X"])+1):
                tile = {"X": x, "Y": y}
                self.tiles.append(tile)
                if 'color' not in radar:
                    radar['color'] = 6
                if 'smooth' not in radar:
                    radar['smooth'] = 1
                if 'snow' not in radar:
                    radar['snow'] = 1
                tail = "/256/%d/%d/%d/%d/%d_%d.png" % (self.zoom, x, y,
                                                       radar['color'],
                                                       radar['smooth'],
                                                       radar['snow'])
                if 'oldcolor' in radar:
                    tail = "/256/%d/%d/%d.png?color=%d" % (self.zoom, x, y,
                                                           radar['color']
                                                           )
                self.tiletails.append(tail)
        for x in range(int(self.cornerTiles["NW"]["X"]),
                       int(self.cornerTiles["NE"]["X"])+1):
            self.totalWidth += 256
            self.tilesWidth += 1
        self.frameImages = []
        self.frameIndex = 0
        self.displayedFrame = 0
        self.ticker = 0
        self.lastget = 0

    def rtick(self):
        if time.time() > (self.lastget + self.interval):
            print ("Refresh time")
            self.get(time.time())
            self.lastget = time.time()
        if len(self.frameImages) < 1:
            #print ("Rtick Frameimages <1")
            return
        if self.displayedFrame == 0:
            #print ("displayedFrame == 0")
            self.ticker += 1
            #print ("self ticker=")
            #print (str(self.ticker))
            if self.ticker < 5:
                #print ("ticker <5")
                return
        self.ticker = 0
        f = self.frameImages[self.displayedFrame]
        #print (str(f))
        self.wwx.setPixmap(f["image"])
        self.displayedFrame += 1
        #print ("displayed frame")
        #print (str(self.displayedFrame))
        if self.displayedFrame >= len(self.frameImages):
            self.displayedFrame = 0

    def get(self, t=0):
        #print ("metodo get - inicia a procura de radar")
        t = int(t / 600)*600
        #print (str(t))
        if t > 0 and self.baseTime == t:
            #print ("if t > 0 and self.baseTime == t: --- WILL RETURN" )
            return
        if t == 0:
            t = self.baseTime
            #print ("t = 0 entao t = self.baseTime" )
        else:
            self.baseTime = t
            #print ("self.baseTime = t" )
        newf = []
        for f in self.frameImages:
            #print ("f" + (str(f)))
            if f["time"] >= (t - self.anim * 600):
                newf.append(f)
                #print ("newf")
                #print (str(newf))
        self.frameImages = newf
        #print ("self.frameimages = new f")
        #print (str(self.frameImages))
        firstt = t - self.anim * 600
        for tt in range(firstt, t+1, 600):
#            print "get... " + str(tt) + " " + self.myname
            gotit = False
            for f in self.frameImages:
                if f["time"] == tt:
                    gotit = True
            if not gotit:
                self.getTiles(tt)
                break

    def getTiles(self, t, i=0):
        t = int(t / 600)*600
        self.getTime = t
        self.getIndex = i
        if i == 0:
            self.tileurls = []
            self.tileQimages = []
            for tt in self.tiletails:
                tileurl = "https://tilecache.rainviewer.com/v2/radar/%d/%s" \
                    % (t, tt)
                self.tileurls.append(tileurl)
#        print self.myname + " " + str(self.getIndex) + " " + self.tileurls[i]
        self.tilereq = QNetworkRequest(QUrl(self.tileurls[i]))
        self.tilereply = manager.get(self.tilereq)
        #QtCore.QObject.connect(self.tilereply, QtCore.SIGNAL("finished()"), self.getTilesReply)
        self.tilereply.finished.connect(self.getTilesReply)
        
    def getTilesReply(self):
#        print "getTilesReply " + str(self.getIndex)
        if self.tilereply.error() != QNetworkReply.NoError:
                return
        self.tileQimages.append(QImage())
        self.tileQimages[self.getIndex].loadFromData(self.tilereply.readAll())
        self.getIndex = self.getIndex + 1
        if self.getIndex < len(self.tileurls):
            self.getTiles(self.getTime, self.getIndex)
        else:
            self.combineTiles()
            #print ("Vai chamar o get sem tempo")
            self.get()

    def combineTiles(self):
        global radar1
        ii = QImage(self.tilesWidth*256, self.tilesHeight*256,
                    QImage.Format_ARGB32)
        painter = QPainter()
        painter.begin(ii)
        painter.setPen(QColor(255, 255, 255, 255))
        painter.setFont(QFont("Arial", 10))
        i = 0
        xo = self.cornerTiles["NW"]["X"]
        xo = int((int(xo) - xo)*256)
        yo = self.cornerTiles["NW"]["Y"]
        yo = int((int(yo) - yo)*256)
        for y in range(0, self.totalHeight, 256):
            for x in range(0, self.totalWidth, 256):
                if self.tileQimages[i].format() == 5:
                    painter.drawImage(x, y, self.tileQimages[i])
                # painter.drawRect(x, y, 255, 255)
                # painter.drawText(x+3, y+12, self.tiletails[i])
                i += 1
        painter.end()
        painter = None
        self.tileQimages = []
        ii2 = ii.copy(-xo, -yo, self.rect.width(), self.rect.height())
        ii = None
        painter2 = QPainter()
        painter2.begin(ii2)
        timestamp = "{0:%H:%M} rainvewer.com".format(
                    datetime.datetime.fromtimestamp(self.getTime))
        painter2.setPen(QColor(63, 63, 63, 255))
        painter2.setFont(QFont("Arial", 8))
        painter2.setRenderHint(QPainter.TextAntialiasing)
        painter2.drawText(3-1, 12-1, timestamp)
        painter2.drawText(3+2, 12+1, timestamp)
        painter2.setPen(QColor(255, 255, 255, 255))
        painter2.drawText(3, 12, timestamp)
        painter2.drawText(3+1, 12, timestamp)
        painter2.end()
        painter2 = None
        ii3 = QPixmap(ii2)
        ii2 = None
        self.frameImages.append({"time": self.getTime, "image": ii3})
        ii3 = None

    def mapurl(self, radar, rect):
        mb = 0
        try:
            mb = Config.usemapbox
        except:
            pass
        if mb:
            return self.mapboxurl(radar, rect)
        else:
            return self.googlemapurl(radar, rect)

    def mapboxurl(self, radar, rect):
        #  note we're using google maps zoom factor.
        #  Mapbox equivilant zoom is one less
        #  They seem to be using 512x512 tiles instead of 256x256
        style = 'mapbox/satellite-streets-v10'
        if 'style' in radar:
            style = radar['style']
        return 'https://api.mapbox.com/styles/v1/' + \
               style + \
               '/static/' + \
               str(radar['center'].lng) + ',' + \
               str(radar['center'].lat) + ',' + \
               str(radar['zoom']-1) + ',0,0/' + \
               str(rect.width()) + 'x' + str(rect.height()) + \
               '?access_token=' + ApiKeys.mbapi

    def googlemapurl(self, radar, rect):
        urlp = []
        if len(ApiKeys.googleapi) > 0:
            urlp.append('key=' + ApiKeys.googleapi)
        urlp.append(
            'center=' + str(radar['center'].lat) +
            ',' + str(radar['center'].lng))
        zoom = radar['zoom']
        rsize = rect.size()
        if rsize.width() > 640 or rsize.height() > 640:
            rsize = QtCore.QSize(rsize.width() / 2, rsize.height() / 2)
            zoom -= 1
        urlp.append('zoom=' + str(zoom))
        urlp.append('size=' + str(rsize.width()) + 'x' + str(rsize.height()))
        urlp.append('maptype=hybrid')

        return 'http://maps.googleapis.com/maps/api/staticmap?' + \
            '&'.join(urlp)

    def basefinished(self):
        if self.basereply.error() != QNetworkReply.NoError:
            return
        self.basepixmap = QPixmap()
        self.basepixmap.loadFromData(self.basereply.readAll())
        if self.basepixmap.size() != self.rect.size():
            self.basepixmap = self.basepixmap.scaled(self.rect.size(),
                                                     Qt.KeepAspectRatio,
                                                     Qt.SmoothTransformation)
        self.setPixmap(self.basepixmap)

        # make marker pixmap
        self.mkpixmap = QPixmap(self.basepixmap.size())
        self.mkpixmap.fill(Qt.transparent)
        br = QBrush(QColor(Config.dimcolor))
        painter = QPainter()
        painter.begin(self.mkpixmap)
        painter.fillRect(0, 0, self.mkpixmap.width(),
                         self.mkpixmap.height(), br)
        for marker in self.radar['markers']:
            if 'visible' not in marker or marker['visible'] == 1:
                pt = getPoint(marker["location"], self.point, self.zoom,
                              self.rect.width(), self.rect.height())
                mk2 = QImage()
                mkfile = 'teardrop'
                if 'image' in marker:
                    mkfile = marker['image']
                if os.path.dirname(mkfile) == '':
                    mkfile = os.path.join('markers', mkfile)
                if os.path.splitext(mkfile)[1] == '':
                    mkfile += '.png'
                mk2.load(mkfile)
                if mk2.format != QImage.Format_ARGB32:
                    mk2 = mk2.convertToFormat(QImage.Format_ARGB32)
                mkh = 80  # self.rect.height() / 5
                if 'size' in marker:
                    if marker['size'] == 'small':
                        mkh = 64
                    if marker['size'] == 'mid':
                        mkh = 70
                    if marker['size'] == 'tiny':
                        mkh = 40
                if 'color' in marker:
                    c = QColor(marker['color'])
                    (cr, cg, cb, ca) = c.getRgbF()
                    for x in range(0, mk2.width()):
                        for y in range(0, mk2.height()):
                            (r, g, b, a) = QColor.fromRgba(
                                           mk2.pixel(x, y)).getRgbF()
                            r = r * cr
                            g = g * cg
                            b = b * cb
                            mk2.setPixel(x, y, QColor.fromRgbF(r, g, b, a)
                                         .rgba())
                mk2 = mk2.scaledToHeight(mkh, 1)
                painter.drawImage(pt.x-mkh/2, pt.y-mkh/2, mk2)

        painter.end()

        self.wmk.setPixmap(self.mkpixmap)

    def getbase(self):
        global manager
        self.basereq = QNetworkRequest(QUrl(self.baseurl))
        self.basereply = manager.get(self.basereq)
        #QtCore.QObject.connect(self.basereply, QtCore.SIGNAL("finished()"), self.basefinished)
        self.basereply.finished.connect(self.basefinished)

    def start(self, interval=0):
        global firsttime
        firsttime = True
        print ("Inicia a aplicacao")
        if interval > 0:
            self.interval = interval
        self.getbase()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.rtick)
        self.lastget = time.time() - self.interval + random.uniform(3, 10)

    def wxstart(self):
#        print "wxstart for " + self.myname
        self.timer.start(200)

    def wxstop(self):
#        print "wxstop for " + self.myname
        self.timer.stop()

    def stop(self):
        try:
            self.timer.stop()
            self.timer = None
        except Exception:
            pass

#Quit app
def realquit():
    QtGui.QApplication.exit(0)

#stop all items
def myquit(a=0, b=0):
    global objradar1, objradar2, objradar3, objradar4
    global ctimer, wtimer, temptimer

    #objradar1.stop()
    objradar2.stop()
    
    #objradar3.stop()
    #objradar4.stop()
    ctimer.stop()
    wxtimer.stop()
    temptimer.stop()
    if Config.useslideshow:
        objimage1.stop()

    if Config.usephotoshow:
        objimage2.stop()

    if Config.obituaryPhotos:
        objimage3.stop()

    QtCore.QTimer.singleShot(30, realquit)

#Related with radar
def fixupframe(frame, onoff):
    for child in frame.children():
        if isinstance(child, Radar):
            if onoff:
                # print "calling wxstart on radar on ",frame.objectName()
                child.wxstart()
            else:
                # print "calling wxstop on radar on ",frame.objectName()
                child.wxstop()

#Change frames in app
def nextframe(plusminus):
    global frames, framep
    frames[framep].setVisible(False)
    fixupframe(frames[framep], False)
    framep += plusminus
    if framep >= len(frames):
        framep = 0
    if framep < 0:
        framep = len(frames) - 1
    frames[framep].setVisible(True)
    fixupframe(frames[framep], True)


def changeState():
    global meuBotao
    print ("Changing state")
    if meuBotao == True:
        print ("era Vila Cha")
        meuBotao = False
        print ("agora e VLC " +str(meuBotao))
    else:
        print ("era VLC")
        meuBotao = True
        print ("agora e Vila Cha " +str(meuBotao))

#Main class to listem for keyboarda nd click modification
class myMain(QtWidgets.QWidget):

    def keyPressEvent(self, event):
        global weatherplayer, lastkeytime
        if isinstance(event, QtGui.QKeyEvent):
            # print event.key(), format(event.key(), '08x')
            if event.key() == Qt.Key_F4:
                myquit()
            if event.key() == Qt.Key_Space:
                nextframe(1)
            if event.key() == Qt.Key_Left:
                nextframe(-1)
            if event.key() == Qt.Key_Right:
                nextframe(1)
            if event.key() == Qt.Key_F6:  # Previous Image
                objimage1.prev_next(-1)
            if event.key() == Qt.Key_F7:  # Next Image
                objimage1.prev_next(1)
                objimage5.prev_next(1)
            if event.key() == Qt.Key_F8:  # Play/Pause
                objimage1.play_pause()
            if event.key() == Qt.Key_F10:
                print ("Vai chamar changing state")
                changeState()
            if event.key() == Qt.Key_F9:  # Foreground Toggle
                if foreGround.isVisible():
                    foreGround.hide()
                else:
                    foreGround.show()

#    def mousePressEvent(self, event):
#        if type(event) == QtGui.QMouseEvent:
#            nextframe(1)


configname = 'Config'

if len(sys.argv) > 1:
    configname = sys.argv[1]

if not os.path.isfile(configname + ".py"):
    print ("Config file not found %s" % configname + ".py")
    exit(1)

Config = __import__(configname)

# define default values for new/optional config variables.
###To add new values added to config file

try:
    Config.location
except AttributeError:
    Config.location = Config.wulocation

try:
    Config.metric
except AttributeError:
    Config.metric = 0

try:
    Config.weather_refresh
except AttributeError:
    Config.weather_refresh = 30   # minutes

try:
    Config.radar_refresh
except AttributeError:
    Config.radar_refresh = 10    # minutes

try:
    Config.fontattr
except AttributeError:
    Config.fontattr = ''

try:
    Config.dimcolor
except AttributeError:
    Config.dimcolor = QColor('#000000')
    Config.dimcolor.setAlpha(0)

try:
    Config.DateLocale
except AttributeError:
    Config.DateLocale = ''

try:
    Config.wind_degrees
except AttributeError:
    Config.wind_degrees = 0

try:
    Config.digital
except AttributeError:
    Config.digital = 0

try:
    Config.Language
except AttributeError:
    try:
        Config.Language = Config.wuLanguage
    except AttributeError:
        Config.Language = "en"

try:
    Config.LPressure
except AttributeError:
    Config.LPressure = "Pressure "
    Config.LHumidity = "Humidity "
    Config.LWind = "Wind "
    Config.Lgusting = " gusting "
    Config.LFeelslike = "Feels like "
    Config.LPrecip1hr = " Precip 1hr:"
    Config.LToday = "Today: "
    Config.LSunRise = "Sun Rise:"
    Config.LSet = " Set: "
    Config.LMoonPhase = " Moon Phase:"
    Config.LInsideTemp = "Inside Temp "
    Config.LRain = " Rain: "
    Config.LSnow = " Snow: "

try:
    Config.Lmoon1
    Config.Lmoon2
    Config.Lmoon3
    Config.Lmoon4
    Config.Lmoon5
    Config.Lmoon6
    Config.Lmoon7
    Config.Lmoon8
except AttributeError:
    Config.Lmoon1 = 'New Moon'
    Config.Lmoon2 = 'Waxing Crescent'
    Config.Lmoon3 = 'First Quarter'
    Config.Lmoon4 = 'Waxing Gibbous'
    Config.Lmoon5 = 'Full Moon'
    Config.Lmoon6 = 'Waning Gibbous'
    Config.Lmoon7 = 'Third Quarter'
    Config.Lmoon8 = 'Waning Crecent'

try:
    Config.digitalformat2
except AttributeError:
    Config.digitalformat2 = "{0:%H:%M:%S}"

try:
    Config.useslideshow
except AttributeError:
    Config.useslideshow = 0

try:
    Config.usephotoshow
except AttributeError:
    Config.usephotoshow = 0
    
try:
    Config.AppMode
except AttributeError:
    Config.AppMode = "release"

#
# Check if Mapbox API key is set, and use mapbox if so
try:
    if ApiKeys.mbapi[:3].lower() == "pk.":
        Config.usemapbox = 1
except AttributeError:
    pass

#Variables
lastmin = -1
lastday = -1
pdy = ""
lasttimestr = ""
weatherplayer = None
lastkeytime = 0
lastapiget = time.time()


#PyQT Definitions
app = QtWidgets.QApplication(sys.argv)
desktop = app.desktop()
rec = desktop.screenGeometry()

if Config.AppMode == "teste":
    print ("Mode test activated - Window size according to raspberry pi desktop")
    height = rec.height() *0.8533
    width = rec.width() *0.66667
else:
    print ("Mode release activated - Window size 1280X1024")
    height = rec.height() 
    width = rec.width()
     
    
signal.signal(signal.SIGINT, myquit)

w = myMain()
w.setWindowTitle(os.path.basename(__file__))
w.setStyleSheet("QWidget { background-color: black;}")

# fullbgpixmap = QtGui.QPixmap(Config.background)
# fullbgrect = fullbgpixmap.rect()
# xscale = float(width)/fullbgpixmap.width()
# yscale = float(height)/fullbgpixmap.height()


xscale = float(width) / 1440.0 
yscale = float(height) / 900.0 

xScaleOffset = 0.88
yScaleOffset = 1

#print ("xscale "  + str(xscale))
#print ("yscale" + str(yscale))

#PyQt Desings
frames = []
framep = 0

frame1 = QtWidgets.QFrame(w)
frame1.setObjectName("frame1")
frame1.setGeometry(0, 0, width, height)
frame1.setStyleSheet("#frame1 { background-color: black; border-image: url(" +
                     Config.background + ") 0 0 0 0 stretch stretch;}")
frames.append(frame1)




frame2 = QtWidgets.QFrame(w)
frame2.setObjectName("frame2")
frame2.setGeometry(0, 0, width, height)
frame2.setStyleSheet("#frame2 { background-color: black; border-image: url(" +
                     Config.background + ") 0 0 0 0 stretch stretch;}")
frame2.setVisible(False)
frames.append(frame2)

# frame3 = QtGui.QFrame(w)
# frame3.setObjectName("frame3")
# frame3.setGeometry(0,0,width,height)
# frame3.setStyleSheet("#frame3 { background-color: blue; border-image:
#       url("+Config.background+") 0 0 0 0 stretch stretch;}")
# frame3.setVisible(False)
# frames.append(frame3)

foreGround = QtWidgets.QFrame(frame1)
foreGround.setObjectName("foreGround")
foreGround.setStyleSheet("#foreGround { background-color: transparent; }")
foreGround.setGeometry(0, 0, width, height)

if Config.useslideshow:
    imgRect = QtCore.QRect(310 * xscale , 120, width - (620 * xscale) , height-120)
    objimage1 = SlideShow(frame1, imgRect, "image1")

if Config.obituaryPhotos:
    objimage3 = Fetch()

if Config.usephotoshow:
    photoRect = QtCore.QRect(3 * xscale , 344 * yscale, 300 * xscale , 200 * yscale)
    objimage2 = ObituarySlide(foreGround, photoRect, "image2")
    
if Config.usephotoshow:
    photoRect = QtCore.QRect( 0 * xscale , 0, width - (620 * xscale) , height)
    objimage4 = ObituarySlide(frame2, photoRect, "image4")
    
if Config.bibleShow:
    photoRect = QtCore.QRect( 800 * xscale , 110, width - (700 * xscale) , height)
    objimage5 = BibleSlide(frame2, photoRect, "image5")


squares1 = QtWidgets.QFrame(foreGround)
squares1.setObjectName("squares1")
squares1.setGeometry(0, height - yscale * 600, xscale * 340, yscale * 600)
squares1.setStyleSheet(
    "#squares1 { background-color: transparent; border-image: url(" +
    Config.squares1 +
    ") 0 0 0 0 stretch stretch;}")

squares2 = QtWidgets.QFrame(foreGround)
squares2.setObjectName("squares2")
squares2.setGeometry(width - xscale * 340, 0, xscale * 340, yscale * 900)
squares2.setStyleSheet(
    "#squares2 { background-color: transparent; border-image: url(" +
    Config.squares2 +
    ") 0 0 0 0 stretch stretch;}")

if not Config.digital:
    clockface = QtWidgets.QFrame(foreGround)
    clockface.setObjectName("clockface")
    clockrect = QtCore.QRect(
        width / 2 - height * .4,
        height * .45 - height * .4,
        height * .8,
        height * .8)
    clockface.setGeometry(clockrect)
    clockface.setStyleSheet(
        "#clockface { background-color: transparent; border-image: url(" +
        Config.clockface +
        ") 0 0 0 0 stretch stretch;}")

    hourhand = QtWidgets.QLabel(foreGround)
    hourhand.setObjectName("hourhand")
    hourhand.setStyleSheet("#hourhand { background-color: transparent; }")

    minhand = QtWidgets.QLabel(foreGround)
    minhand.setObjectName("minhand")
    minhand.setStyleSheet("#minhand { background-color: transparent; }")

    sechand = QtWidgets.QLabel(foreGround)
    sechand.setObjectName("sechand")
    sechand.setStyleSheet("#sechand { background-color: transparent; }")

    hourpixmap = QtGui.QPixmap(Config.hourhand)
    hourpixmap2 = QtGui.QPixmap(Config.hourhand)
    minpixmap = QtGui.QPixmap(Config.minhand)
    minpixmap2 = QtGui.QPixmap(Config.minhand)
    secpixmap = QtGui.QPixmap(Config.sechand)
    secpixmap2 = QtGui.QPixmap(Config.sechand)
else:
    clockface = QtWidgets.QLabel(foreGround)
    clockface.setObjectName("clockface")
    clockrect = QtCore.QRect(
        width / 2 - height * .88,
        height * .15 - height * .514,
        height * .8,
        height * .8)
    clockface.setGeometry(clockrect)
    dcolor = QColor(Config.digitalcolor).darker(0).name()
    lcolor = QColor(Config.digitalcolor).lighter(120).name()
    clockface.setStyleSheet(
        "#clockface { background-color: transparent; font-family:sans-serif;" +
        " font-weight: light; color: " +
        lcolor +
        "; background-color: transparent; font-size: " +
        str(int(Config.digitalsize * xscale)) +
        "px; " +
        Config.fontattr +
        "}")
    clockface.setAlignment(Qt.AlignCenter)
    clockface.setGeometry(clockrect)
    glow = QtWidgets.QGraphicsDropShadowEffect()
    glow.setOffset(0)
    glow.setBlurRadius(50)
    glow.setColor(QColor(dcolor))
    clockface.setGraphicsEffect(glow)



radar2rect = QtCore.QRect(3 * xscale, 622 * yscale, 300 * xscale, 275 * yscale)
objradar2 = Radar(foreGround, Config.radar2, radar2rect, "radar2")




datex = QtWidgets.QLabel(foreGround)
datex.setObjectName("datex")
datex.setStyleSheet("#datex { font-family:sans-serif; color: " +
                    Config.textcolor +
                    "; background-color: transparent; font-size: " +
                    str(int(50 * xscale)) +
                    "px; " +
                    Config.fontattr +
                    "}")
datex.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
datex.setGeometry(0, 10, width, 100)

#data frame2
datex2 = QtWidgets.QLabel(frame2)
datex2.setObjectName("datex2")
datex2.setStyleSheet("#datex2 { font-family:sans-serif; color: " +
                     Config.textcolor +
                     "; background-color: black; font-size: " +
                     str(int(50* xscale)) + "px; " +
                     Config.fontattr +
                     "}")
datex2.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
datex2.setGeometry(840* xscale, 20 * yscale, 300 * xscale, 100)

#hora frame 2
datey2 = QtWidgets.QLabel(frame2)
datey2.setObjectName("datey2")
datey2.setStyleSheet("#datey2 { font-family:sans-serif; color: " +
                     Config.textcolor +
                     "; background-color: transparent; font-size: " +
                     str(int(50 * xscale)) +
                     "px; " +
                     Config.fontattr +
                     "}")
datey2.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
datey2.setGeometry(1150 * xscale, 20 * yscale, 300 * xscale, 50)

obituaryPersonNameLabel = QtWidgets.QLabel(foreGround)
obituaryPersonNameLabel.setObjectName("obituaryPersonNameLabel")
obituaryPersonNameLabel.setStyleSheet("#obituaryPersonNameLabel { " +
                          " background-color: transparent; color: " +
                          Config.textcolor +
                          "; font-size: " +
                          str(int(15 * xscale * xScaleOffset)) +
                          "px; " +
                          Config.fontattr + "font-weight: bold;" +
                          "}")
obituaryPersonNameLabel.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
obituaryPersonNameLabel.setGeometry(6 * xscale, 545 * yscale , 300 * xscale, 100)

###Change deffine all other obituary labels
obituaryPersonDateAndAgeLabel = QtWidgets.QLabel(foreGround)
obituaryPersonDateAndAgeLabel.setObjectName("obituaryPersonDateAndAgeLabel")
obituaryPersonDateAndAgeLabel.setStyleSheet("#obituaryPersonDateAndAgeLabel { " +
                          " background-color: transparent; color: " +
                          Config.textcolor +
                          "; font-size: " +
                          str(int(16 * xscale * xScaleOffset)) +
                          "px; " +
                          Config.fontattr + "font-weight: bold;" +
                          "}")
obituaryPersonDateAndAgeLabel.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
obituaryPersonDateAndAgeLabel.setGeometry(6 * xscale, 557 * yscale , 300 * xscale, 100)

obituaryPersonAdressLabel = QtWidgets.QLabel(foreGround)
obituaryPersonAdressLabel.setObjectName("obituaryPersonAdressLabel")
obituaryPersonAdressLabel.setStyleSheet("#obituaryPersonAdressLabel { " +
                          " background-color: transparent; color: " +
                          Config.textcolor +
                          "; font-size: " +
                          str(int(15 * xscale * xScaleOffset)) +
                          "px; " +
                          Config.fontattr + "font-weight: bold;" +
                          "}")
obituaryPersonAdressLabel.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
obituaryPersonAdressLabel.setGeometry(20 * xscale, 559* yscale , 300 * xscale * xScaleOffset, 100)

obituaryPersonFuneralLabel = QtWidgets.QLabel(foreGround)
obituaryPersonFuneralLabel.setObjectName("obituaryPersonFuneralLabel")
obituaryPersonFuneralLabel.setStyleSheet("#obituaryPersonFuneralLabel { " +
                          " background-color: transparent; color: " +
                          Config.textcolor +
                          "; font-size: " +
                          str(int(14.8 * xscale * xScaleOffset )) +
                          "px; " +
                          Config.fontattr + "font-weight: bold;" +
                          "}")
obituaryPersonFuneralLabel.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
obituaryPersonFuneralLabel.setGeometry(6 * xscale, 583 * yscale , 300 * xscale , 200)

ypos = -25
wxicon = QtWidgets.QLabel(foreGround)
wxicon.setObjectName("wxicon")
wxicon.setStyleSheet("#wxicon { background-color: transparent; }")
wxicon.setGeometry(0 * xscale, 80 * yscale, 150 * xscale * xScaleOffset, 140 * yscale)

attribution2 = QtWidgets.QLabel(frame2)
attribution2.setObjectName("attribution2")
attribution2.setStyleSheet("#attribution2 { " +
                           "background-color: transparent; color: " +
                           Config.textcolor +
                           "; font-size: " +
                           str(int(12 * xscale)) +
                           "px; " +
                           Config.fontattr +
                           "}")
attribution2.setAlignment(Qt.AlignTop)
attribution2.setGeometry(6 * xscale, 880 * yscale, 100 * xscale, 100)

# wxicon2 = QtWidgets.QLabel(frame2)
# wxicon2.setObjectName("wxicon2")
# wxicon2.setStyleSheet("#wxicon2 { background-color: yellow; }")
# wxicon2.setGeometry(0 * xscale, 750 * yscale, 150 * xscale, 150 * yscale)

ypos += 130
wxdesc = QtWidgets.QLabel(foreGround)
wxdesc.setObjectName("wxdesc")
wxdesc.setStyleSheet("#wxdesc { background-color: transparent; color: " +
                     Config.textcolor +
                     "; font-size: " +
                     str(int(30 * xscale)) +
                     "px; " +
                     Config.fontattr +
                     "}")
wxdesc.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
wxdesc.setGeometry(5.625 * xscale, 52.73 * yscale, 300 * xscale, 100)

##TEXTO BIBLIA
wxdesc2 = QtWidgets.QLabel(frame2)
wxdesc2.setObjectName("wxdesc2")
wxdesc2.setWordWrap(True)

wxdesc2.setStyleSheet("#wxdesc2 { background-transparent: black; color: white" +
                      "; font-size: " +
                      str(int(15 * xscale)) +
                      "px; " +
                      Config.fontattr +
                      "}")
wxdesc2.setAlignment(Qt.AlignLeft | Qt.AlignCenter)
wxdesc2.setGeometry(820 * xscale, 80 * yscale, 620 * xscale, height -80)

ypos += 25
temper = QtWidgets.QLabel(foreGround)
temper.setObjectName("temper")
temper.setStyleSheet("#temper { background-color: transparent; color: " +
                     Config.textcolor +
                     "; font-size: " +
                     str(int(55 * xscale)) +
                     "px; " +
                     Config.fontattr +
                     "}")
temper.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
temper.setGeometry(72 * xscale, 105.46 * yscale, 300 * xscale, 100)

# temper2 = QtWidgets.QLabel(frame2)
# temper2.setObjectName("temper2")
# temper2.setStyleSheet("#temper2 { background-color: blue; color: " +
                      # Config.textcolor +
                      # "; font-size: " +
                      # str(int(70 * xscale)) +
                      # "px; " +
                      # Config.fontattr +
                      # "}")
# temper2.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
# temper2.setGeometry(140 * xscale, 780 * yscale, 300 * xscale, 100)

ypos += 80
press = QtWidgets.QLabel(foreGround)
press.setObjectName("press")
press.setStyleSheet("#press { background-color: transparent; color: " +
                    Config.textcolor +
                    "; font-size: " +
                    str(int(20 * xscale)) +
                    "px; " +
                    Config.fontattr +
                    "}")
press.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
press.setGeometry(3 * xscale, ypos * yscale, 300 * xscale, 100)

ypos += 30
humidity = QtWidgets.QLabel(foreGround)
humidity.setObjectName("humidity")
humidity.setStyleSheet("#humidity { background-color: transparent; color: " +
                       Config.textcolor +
                       "; font-size: " +
                       str(int(20 * xscale)) +
                       "px; " +
                       Config.fontattr +
                       "}")
humidity.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
humidity.setGeometry(3 * xscale, ypos * yscale, 300 * xscale, 100)

ypos += 30
wind = QtWidgets.QLabel(foreGround)
wind.setObjectName("wind")
wind.setStyleSheet("#wind { background-color: transparent; color: " +
                   Config.textcolor +
                   "; font-size: " +
                   str(int(15 * xscale)) +
                   "px; " +
                   Config.fontattr +
                   "}")
wind.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
wind.setGeometry(3 * xscale, ypos * yscale, 300 * xscale, 100)

ypos += 20
wind2 = QtWidgets.QLabel(foreGround)
wind2.setObjectName("wind2")
wind2.setStyleSheet("#wind2 { background-color: transparent; color: " +
                    Config.textcolor +
                    "; font-size: " +
                    str(int(18 * xscale)) +
                    "px; " +
                    Config.fontattr +
                    "}")
wind2.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
wind2.setGeometry(3 * xscale, ypos * yscale, 300 * xscale, 100)

ypos += 20
wdate = QtWidgets.QLabel(foreGround)
wdate.setObjectName("wdate")
wdate.setStyleSheet("#wdate { background-color: transparent; color: " +
                    Config.textcolor +
                    "; font-size: " +
                    str(int(15 * xscale)) +
                    "px; " +
                    Config.fontattr +
                    "}")
wdate.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
wdate.setGeometry(3 * xscale, ypos * yscale, 300 * xscale, 100)

bottom = QtWidgets.QLabel(foreGround)
bottom.setObjectName("bottom")
bottom.setStyleSheet("#bottom { font-family:sans-serif; color: " +
                     Config.textcolor +
                     "; background-color: transparent; font-size: " +
                     str(int(25 * xscale)) +
                     "px; " +
                     Config.fontattr +
                     "}")
bottom.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
bottom.setGeometry(0, 60, width, 100)

temp = QtWidgets.QLabel(foreGround)
temp.setObjectName("temp")
temp.setStyleSheet("#temp { font-family:sans-serif; color: " +
                   Config.textcolor +
                   "; background-color: transparent; font-size: " +
                   str(int(30 * xscale)) +
                   "px; " +
                   Config.fontattr +
                   "}")
temp.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
temp.setGeometry(0, 60, width, 50)


forecast = []
for i in range(0, 9):
    lab = QtWidgets.QLabel(foreGround)
    lab.setObjectName("forecast" + str(i))
    lab.setStyleSheet("QWidget { background-color: transparent; color: " +
                      Config.textcolor +
                      "; font-size: " +
                      str(int(20 * xscale)) +
                      "px; " +
                      Config.fontattr +
                      "}")
    lab.setGeometry(1137 * xscale, i * 100 * yscale,
                    300 * xscale, 100 * yscale)

    icon = QtWidgets.QLabel(lab)
    icon.setStyleSheet("#icon { background-color: transparent; }")
    icon.setGeometry(0, 5, 95 * xscale, 95 * yscale)
    icon.setObjectName("icon")

    wx = QtWidgets.QLabel(lab)
    wx.setStyleSheet("#wx { background-color: transparent; }")
    wx.setGeometry(100 * xscale, 5 * yscale, 200 * xscale, 120 * yscale)
    wx.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    wx.setWordWrap(True)
    wx.setObjectName("wx")

    day = QtWidgets.QLabel(lab)
    day.setStyleSheet("#day { background-color: transparent; }")
    day.setGeometry(100 * xscale, 75 * yscale, 200 * xscale, 25 * yscale)
    day.setAlignment(Qt.AlignRight | Qt.AlignBottom)
    day.setObjectName("day")

    forecast.append(lab)

manager = QtNetwork.QNetworkAccessManager()

# proxy = QNetworkProxy()
# proxy.setType(QNetworkProxy.HttpProxy)
# proxy.setHostName("localhost")
# proxy.setPort(8888)
# QNetworkProxy.setApplicationProxy(proxy)


stimer = QtCore.QTimer()
stimer.singleShot(10, qtstart)

# print radarurl(Config.radar1,radar1rect)

w.show()
#w.showFullScreen()


sys.exit(app.exec_())
