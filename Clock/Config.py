#!/usr/bin/python
# -*- coding: utf-8 -*-

from GoogleMercatorProjection import LatLng
from PyQt5.QtGui import QColor

##App mode - Test in Raspberry Pi Desktop or Release in 1280x1200 screen
AppMode = "teste"

# LOCATION(S)
# Further radar configuration (zoom, marker location) can be
# completed under the RADAR section
primary_coordinates = 40.8495924, -8.3942413  # Change to your Lat/Lon

location = LatLng(primary_coordinates[0], primary_coordinates[1])
primary_location = LatLng(primary_coordinates[0], primary_coordinates[1])
noaastream = 'http://www.urberg.net:8000/tim273/edina'
background = 'images/black2.png'
squares1 = 'images/squares1-jean.png'
squares2 = 'images/squares2-jean.png'
icons = 'icons-color'
textcolor = '#ffffff'
textcolor2 = '#000000'
clockface = 'images/clockface3.png'
hourhand = 'images/hourhand.png'
minhand = 'images/minhand.png'
sechand = 'images/sechand.png'

# SlideShow
useslideshow = 1            # 1 to enable, 0 to disable
slide_time = 10             # in seconds, 3600 per hour
slides = 'images/slideshow'   # the path to your local images
slide_bg_color = "#000000"       # https://htmlcolorcodes.com/  black #000

digital = 1                 # 1 = Digtal Clock, 0 = Analog Clock

#downloadPhotos

obituaryPhotos = 1
limit = 6
# usephotoshow
usephotoshow = 1
photo_time = 30
photos = 'images/photoshow'
paperLinks = 'images/paperlinks'
photo_bg_color = '#ffffff'
time_to_fetch = 60

# Goes with light blue config (like the default one)
digitalcolor = "#ffffff"
digitalformat = "{0:%H:%M:%S}"  # Format of the digital clock face
digitalsize = 70

# The above example shows in this way:
#  https://github.com/n0bel/PiClock/blob/master/Documentation/Digital%20Clock%20v1.jpg
# ( specifications of the time string are documented here:
#  https://docs.python.org/2/library/time.html#time.strftime )

# digitalformat = "{0:%I:%M}"
# digitalsize = 250
#  The above example shows in this way:
#  https://github.com/n0bel/PiClock/blob/master/Documentation/Digital%20Clock%20v2.jpg

digitalformat2 = "{0:%H:%M:%S}"  # Format of the digital time on second screen

usemapbox = 1   # Use Mapbox.com for maps, needs api key (mbapi in ApiKeys.py)
metric = 1  # 0 = English, 1 = Metric
radar_refresh =  1     # minutes
weather_refresh = 10    # minutes
# Wind in degrees instead of cardinal 0 = cardinal, 1 = degrees
wind_degrees = 0

# gives all text additional attributes using QT style notation
# example: fontattr = 'font-weight: bold; '
fontattr = ''

# These are to dim the radar images, if needed.
# see and try Config-Example-Bedside.py
dimcolor = QColor('#000000')
dimcolor.setAlpha(0.5)

# Language Specific wording
# DarkSky Language code
#  (https://darksky.net/dev/docs under lang=)
Language = "PT"

# The Python Locale for date/time (locale.setlocale)
#  '' for default Pi Setting
# Locales must be installed in your Pi.. to check what is installed
# locale -a
# to install locales
# sudo dpkg-reconfigure locales
DateLocale = 'PT'

# Language specific wording
LPressure = "Pressao: "
LHumidity = "Humidade: "
LWind = "Vento: "
Lgusting = " Rajadas: "
LFeelslike = "Temperatura sentida: "
LPrecip1hr = "Chuva 1hora: "
LToday = "Hoje: "
LSunRise = "Nascer do sol:"
LSet = " Por do sol:"
LMoonPhase = " Lua:"
LInsideTemp = "Temperatura interior: "
LRain = " Chuva: "
LSnow = " Neve: "
Lmoon1 = 'Quarto Minguante'
Lmoon2 = 'Lua nova'
Lmoon3 = 'Quarto Crescente'
Lmoon4 = 'Quarto Crescente'
Lmoon5 = 'Quarto Crescente'
Lmoon6 = 'Lua cheia'
Lmoon7 = 'Quarto Minguante'
Lmoon8 = 'Quarto Minguante'

# RADAR
# By default, primary_location entered will be the
#  center and marker of all radar images.
# To update centers/markers, change radar sections
# below the desired lat/lon as:
# -FROM-
# primary_location,
# -TO-
# LatLng(44.9764016,-93.2486732),
radar1 = {
    'center': primary_location,  # the center of your radar block
    'zoom': 13,  # this is a maps zoom factor, bigger = smaller area
    'style': 'mapbox/satellite-streets-v10',  # optional style (mapbox only)
    'color': 6,  # rainviewer radar color style:
                 # https://www.rainviewer.com/api.html#colorSchemes
    'smooth': 1,  # rainviewer radar smoothing
    'snow': 1,  # rainviewer radar show snow as different color
    'markers': (   # google maps markers can be overlayed
        {
            'visible': 1,  # 0 = hide marker, 1 = show marker
            'location': primary_location,
            'color': 'red',
            'size': 'small',
            'image': 'teardrop-dot',  # optional image from the markers folder
        },          # dangling comma is on purpose.
    )
}


radar2 = {
    'center': primary_location,
    'zoom': 8,
    'style': 'mapbox/satellite-streets-v10',
    'color': 6,
    'smooth': 1,
    'snow': 1,
    'markers': (
        {
            'visible': 1,
            'location': primary_location,
            'color': 'red',
            'size': 'small',
            'image': 'teardrop-dot',
        },
    )
}


radar3 = {
    'center': primary_location,
    'zoom': 15,
    'style': 'mapbox/satellite-streets-v10',
    'color': 6,
    'smooth': 1,
    'snow': 1,
    'markers': (
        {
            'visible': 1,
            'location': primary_location,
            'color': 'red',
            'size': 'small',
            'image': 'teardrop-dot',
        },
    )
}

radar4 = {
    'center': primary_location,
    'zoom': 8,
    'style': 'mapbox/satellite-streets-v10',
    'color': 6,
    'smooth': 1,
    'snow': 1,
    'markers': (
        {
            'visible': 1,
            'location': primary_location,
            'color': 'red',
            'size': 'small',
            'image': 'teardrop-dot',
        },
    )
}
