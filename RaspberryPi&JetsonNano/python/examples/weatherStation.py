#!/usr/bin/python
# -*- coding:utf-8 -*-
print("Doing imports...")
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
print("Got the following important directories:")
print("{}\n{}\n\n".format(picdir, libdir))
if os.path.exists(libdir):
    print("The libdir exists, adding it to the path!")
    sys.path.append(libdir)
else:
    print("Couldn't find the libdir!\n{}\n\nExiting...".format(libdir))

print("Tricky imports...")
import logging
print("Got logging")
from waveshare_epd import epd2in13_V2
print("Got the waveshare lib...")
import time
print("Got time")
from PIL import Image,ImageDraw,ImageFont
print("Got PIL...")
import traceback
print("Got traceback...")

import pyowm
if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

print("Got all imports!! yaaay")

refresh_delay = 30 * 60 # seconds
owm = pyowm.OWM('76f362fd439dd059a4baa1ae2722375c')

# REPLACE WITH YOUR CITY ID
city_id = 2639388 # Richmond


# An easy way to display icons and artwork on your ePaper display is to use a font like
# Meteocons, which maps font letters to specific icons, so by printing a character "B" you can print
# a Sunny icon!
#
# Open Weather Map has weather codes for the current weather report, that correspond to different
# conditions like sunny, cloudy, etc. Check Weather Condition Codes under 
# https://openweathermap.org/weather-conditions
# for the full list of weather codes. 
#
# Map weather code from OWM to meteocon icons.
#
# This enables us to easily use artwork and icons
# for display by simply using the character corresponding to that icon!
#
# Refer to http://www.alessioatzeni.com/meteocons/ for the mapping of meteocons to characters,
# and modify the dictionary below to change icons you want to use for different weather conditions!
# Meteocons is free to use - you can customize the icons - do consider contributing back to Meteocons!
weather_icon_dict = {200 : "6", 201 : "6", 202 : "6", 210 : "6", 211 : "6", 212 : "6", 
                     221 : "6", 230 : "6" , 231 : "6", 232 : "6", 

                     300 : "7", 301 : "7", 302 : "8", 310 : "7", 311 : "8", 312 : "8",
                     313 : "8", 314 : "8", 321 : "8", 
 
                     500 : "7", 501 : "7", 502 : "8", 503 : "8", 504 : "8", 511 : "8", 
                     520 : "7", 521 : "7", 522 : "8", 531 : "8",

                     600 : "V", 601 : "V", 602 : "W", 611 : "X", 612 : "X", 613 : "X",
                     615 : "V", 616 : "V", 620 : "V", 621 : "W", 622 : "W", 

                     701 : "M", 711 : "M", 721 : "M", 731 : "M", 741 : "M", 751 : "M",
                     761 : "M", 762 : "M", 771 : "M", 781 : "M", 

                     800 : "1", 

                     801 : "H", 802 : "N", 803 : "N", 804 : "Y"
}

logging.basicConfig(level=logging.DEBUG)

n = 0
try:
    epd = epd2in13_V2.EPD()
    while True:
        print("Starting...")
        logging.info("epd2in13_V2 WeatherStation")

        print("Fetching weather...")
        # Get Weather data from OWM
        obs = owm.weather_at_id(city_id)
        location = obs.get_location().get_name()
        weather = obs.get_weather()
        reftime = weather.get_reference_time()
        description = weather.get_detailed_status()
        temperature = weather.get_temperature(unit='celsius')
        humidity = weather.get_humidity()
        pressure = weather.get_pressure()
        clouds = weather.get_clouds()
        wind = weather.get_wind()
        rain = weather.get_rain()
        sunrise = weather.get_sunrise_time()
        sunset = weather.get_sunset_time()
        print("Got weather from OWM!\n")
        
        # Set up our font objects. These will be used to draw text to the screen
        font16 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 16)
        font20 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 20)
        font24 = ImageFont.truetype(os.path.join(picdir, "Font.ttc"), 24)

        # These "fonts" are actually the weather icons
        fontweather = ImageFont.truetype(os.path.join(picdir, 'meteocons-webfont.ttf'), 30)
        fontweatherbig = ImageFont.truetype(os.path.join(picdir, 'meteocons-webfont.ttf'), 40)

        # I want to know how big my main texts are, so lets retieve that
        w1, h1 = font24.getsize(location)
        w2, h2 = font20.getsize(description) 
        w3, h3 = fontweatherbig.getsize(weather_icon_dict[weather.get_weather_code()])

        image = Image.new('1', (epd.height, epd.width), 255) # 255 means all white
        # This is our drawing driver object.
        draw = ImageDraw.Draw(image) 

        ### Construct the weather page ###
        # Show the current location and weather at the top
        draw.text((10, 0), description, font=font24, fill=0)
        draw.text((10, 30), location, font=font20, fill=0)
        # Draw the weather icon
        print("Placing the weather icon at x location {}".format(epd.width-w3))
        print("epd width: {}".format(epd.width))
        print("epd height: {}".format(epd.height))
        print("w3: {}".format(w3))
        draw.text((epd.height-5-w3, 5), weather_icon_dict[weather.get_weather_code()], font=fontweatherbig, fill=0)
        # When was the weather we're displaying updated?
        draw.text((10, 55), "Observed at: {}".format(time.strftime("%I:%M %p", time.localtime(reftime)), font=font16, fill=0))

        # Lets draw the temperature on the display now.
        tempstring = "{:.0f}{}C".format(temperature['temp'], u'\u00b0')
        print("Temperature: {}".format(tempstring))
        w4, h4 = font24.getsize(tempstring)
        draw.text((10, 70), tempstring, font=font24, fill=0)
        # And the min/max temperatures. 
        # Thermometer picture
        draw.text((10+w4, 70), "'", font=fontweather, fill=0)
        draw.text(
            (150, 70), 
            "{:.0f}{} | {:.0f}{}".format(temperature['temp_min'], u'\u00b0', n, u'\u00b0'),# temperature['temp_max'], u'\u00b0'),
            font=font24,
            fill=0
        )

        # Sunrise and sunset times. Start with the icons
        draw.text((10, 100), "A", font=fontweather, fill=0)
        draw.text((130, 100), "J", font=fontweather, fill=0)
        # Draw the actual times
        draw.text(
            (45, 100), 
            time.strftime("%H:%M", time.localtime(sunrise)), 
            font=font20, fill=0
        )
        draw.text(
            (160, 100), 
            time.strftime("%H:%M", time.localtime(sunset)),
            font=font20, fill=0
        )

        # Push to the screen
        if n%10 == 0:
            logging.info("init and Clear")
            epd.init(epd.FULL_UPDATE)
            epd.Clear(0xFF)
            epd.display(epd.getbuffer(image))
        else:
            logging.info("Trying a partial update")
            epd.init(epd.PART_UPDATE)
            epd.display(epd.getbuffer(image))
        n += 1
        time.sleep(10)

except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in13_V2.epdconfig.module_exit()
    exit()
