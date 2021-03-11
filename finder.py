from datetime import datetime
import json
import re
import pycurl
from StringIO import StringIO
import time

def checkVaccineJsonUpdate():
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'https://heb-ecom-covid-vaccine.hebdigital-prd.com/vaccine_locations.json')
    c.setopt(c.NOBODY, True)
    c.setopt(c.WRITEHEADER, buffer)
    c.perform()
    c.close()

    return buffer.getvalue()

def getVaccineJSON():
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, 'https://heb-ecom-covid-vaccine.hebdigital-prd.com/vaccine_locations.json')
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()

    return json.loads(buffer.getvalue())

def getVaccineLocationsForCity(locations, cities):
    return filter(lambda l: l["city"].upper() in cities, locations)

def getLocationsWithAppointments(locations):
    return filter(lambda l: l["openAppointmentSlots"] > 0, locations)

def locationToLineItem(location):
    return '<li><a href="{url}">{name}</a> at {street} {city} {zip} Open Appointment Slots: {slots}</li>'.format(url = location["url"], name = location["name"].title(), street = location["street"].title(), city= location["city"].title(), zip= location["zip"], slots = location["openAppointmentSlots"])

def createHtmlFile(locationLineItems, now):
    with open('finder.html', 'r') as template:
        htmlString = template.read()
        return htmlString.replace("%%last_found%%", now.strftime("%d/%m/%Y %H:%M:%S")).replace("%%locations%%", locationLineItems)


lastUpdated = ""

while(True):
    vaccineHeaders = checkVaccineJsonUpdate()
    newLastUpdated = str(re.search(r"Last-Modified: (.*)", vaccineHeaders, re.IGNORECASE).group(1))
    
    if (lastUpdated != newLastUpdated):
        lastUpdated = newLastUpdated

        ## Load vaccine json file
        vaccineJSON = getVaccineJSON()

        ## Get the locations array
        locations = vaccineJSON["locations"]

        ## Get locations with appointments
        availableAppointments = getLocationsWithAppointments(locations)

        ## Get locations we want by city
        wantedAppointments = getVaccineLocationsForCity(availableAppointments, ["AUSTIN", "ROUND ROCK", "PFLUGERVILLE"])

        ## Translate to html line items
        locationLineItems = ""
        for loc in wantedAppointments: locationLineItems += locationToLineItem(loc)

        ## Generate html string
        now = datetime.now()
        html = createHtmlFile(locationLineItems, now)

        with open('test.html', 'w') as test:
            test.write(html)
        
        print("Updated: ", now)

        #test = availableAppointments

        #print(json.dumps(test, sort_keys=True, indent=4))

        #print(locationToLineItem(test[0]))

        #print(json.dumps(getVaccineLocationsForCity(locations, ["AUSTIN", "ROUND ROCK", "PFLUGERVILLE"]), sort_keys=True, indent=4))
    
    ## Wait 2 seconds before checking again
    time.sleep(2)