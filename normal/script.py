import geopy
import geopy.distance
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot
from datetime import datetime
import math
import random

points = gpd.GeoSeries()

kml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
"""
pointsKml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<name>Pins</name><Style id="icon-1899-F9A825-nodesc-normal"><IconStyle><color>ff25a8f9</color><scale>1</scale><Icon><href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href></Icon><hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/></IconStyle><LabelStyle><scale>0</scale></LabelStyle><BalloonStyle><text><![CDATA[<h3>$[name]</h3>]]></text></BalloonStyle></Style><Style id="icon-1899-F9A825-nodesc-highlight"><IconStyle><color>ff25a8f9</color><scale>1</scale><Icon><href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href></Icon><hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/></IconStyle><LabelStyle><scale>1</scale></LabelStyle><BalloonStyle><text><![CDATA[<h3>$[name]</h3>]]></text></BalloonStyle></Style><StyleMap id="icon-1899-F9A825-nodesc"><Pair><key>normal</key><styleUrl>#icon-1899-F9A825-nodesc-normal</styleUrl></Pair><Pair><key>highlight</key><styleUrl>#icon-1899-F9A825-nodesc-highlight</styleUrl></Pair></StyleMap>
"""

totalStars = 100
kmWide = 200
genPoints = False

def getCoordsInUS():
    # print initial info
    print("--- Settings ---")
    print("Total stars:", totalStars)
    print("Star width:", kmWide)
    print("Generate pins on stars:", genPoints)
    print("--- Settings ---")
    print();
    # grab shape within which to sample
    url = "cb_2018_us_nation_20m.zip"
    us = gpd.read_file(url).explode()
    print(url, "loaded")
    ## filter out parts of the US that east of PR (no guam etc)
    #us = us.loc[us.geometry.apply(lambda x: x.exterior.bounds[2])<-60]

    # grab bounding box within which to generate random numbers
    x_min,y_min,x_max,y_max = us.geometry.union_all().bounds
    #print(x_min, y_min, x_max, y_max)

    # the sampling
    N = (totalStars * 24) # enough points to reliably meet the desired number
    rndn_sample = pd.DataFrame({'x':np.random.uniform(x_min,x_max,N),'y':generateLats(y_min,y_max,N)}) # actual generation
    # re-save results in a geodataframe
    rndn_sample = gpd.GeoDataFrame(rndn_sample, geometry = gpd.points_from_xy(x=rndn_sample.x, y=rndn_sample.y),crs = us.crs)
    print('Generating coords...')
    # filtering
    inUS = rndn_sample['geometry'].apply(lambda s: s.within(us.geometry.union_all())) # check if within the U.S. bounds
    global points
    points = rndn_sample.loc[inUS,:].geometry
    #print(type(points))
    #for x in points:
        #print(x.x, x.y)

def generateLats(y_min,y_max,N):
    i = 0
    lats = np.empty([N])
    #print(lats)
    while (i < N):
        lat = generateLat();
        if (lat > y_min and lat < y_max):
            lats[i] = lat
            i += 1
            continue
    #print(lats)
    return lats

def generateLat():
    pi = math.pi
    cf = 180.0 / pi  # radians to degrees correction factor

    # get a random Gaussian 3D vector:
    gx = random.gauss(0.0, 1.0)
    gy = random.gauss(0.0, 1.0)
    gz = random.gauss(0.0, 1.0)

    # normalize to an equidistributed (x,y,z) point on the unit sphere:
    norm2 = gx*gx + gy*gy + gz*gz
    norm1 = 1.0 / math.sqrt(norm2)
    #x = gx * norm1
    #y = gy * norm1
    z = gz * norm1

    # latitude in radians
    radLat = math.asin(z)

    return round(cf*radLat, 5)

def generateShapes():
    x = 0
    # generate star for each point
    for point in points:
        i = 0
        j = 2

        kmWidePerStar = kmWide

        # alaska debuff / make the fewer stars larger
        if (point.y > 50):
            if (np.random.random() < 0.75):
                continue
            else:
                kmWidePerStar *= 1.5

        start = geopy.Point(point.y, point.x)

        global kml
        kml = kml + "<Placemark><name>Star " + str(x + 1) + """</name><Style><IconStyle><Icon/></IconStyle><LineStyle><color>ff0000ff</color><width>1</width></LineStyle></Style><LineString><tessellate>1</tessellate>
        <coordinates>
        """
        global pointsKml
        pointsKml = pointsKml + """<Placemark><name>Star """ + str(x + 1) + """</name><styleUrl>#icon-1899-F9A825-nodesc</styleUrl><Point>
        <coordinates>"""
        pointsKml = pointsKml + str(point.x) + ',' + str(point.y) + ",0.0"
        pointsKml = pointsKml + "</coordinates></Point></Placemark>"
        
        # we get the points for the star here
        randTurn = np.random.random() * 360
        while (i < 11):
            d = geopy.distance.geodesic(kilometers = (j * (kmWidePerStar / 4)))
            sPoint = d.destination(point=start, bearing=(randTurn + (i * 36)))
            kml = kml + str(sPoint.longitude) + ',' + str(sPoint.latitude) + """,0.0
            """
            if (j == 2):
                j = 0.75
            else:
                j = 2
            i += 1
        kml = kml + """</coordinates></LineString></Placemark>"""
        x += 1
        if (x % 25 == 0):
            print(str(x), "generated of", str(totalStars))
        if (x == totalStars):
            break


getCoordsInUS()

print(len(points), "coords generated with", str(totalStars), "needed")

generateShapes();

print("Shapes generated");

kml = kml + """
</Document>
</kml>"""
pointsKml = pointsKml + """</Document>
</kml>"""

filename = "output/" + datetime.now().strftime('%Y%m%d_%H%M%S') + "_" + str(totalStars) + "s_" + str(kmWide).replace(".", "-") + "km.kml"

with open(filename, "a") as f:
    f.write(kml);

if (genPoints):
    filename = "output/" + datetime.now().strftime('%Y%m%d_%H%M%S') + "_" + str(totalStars) + "s_" + str(kmWide).replace(".", "-") + "km_points.kml"
    with open(filename, "a") as f:
        f.write(pointsKml);

print("File generated")
