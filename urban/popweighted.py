from osgeo import gdal
from osgeo import gdal_array
import numpy as np
import time
import random
import geopy
import geopy.distance
import geopandas as gpd
import pandas as pd
import matplotlib
import matplotlib.pyplot
from datetime import datetime
import math

# (62976, 430711)
# [0.0, 878.58935546875, 11.17971419935, 15.080766955253]
# {'STATISTICS_APPROXIMATE': 'YES', 'STATISTICS_MAXIMUM': '878.58935546875',
# 'STATISTICS_MEAN': '11.17971419935', 'STATISTICS_MINIMUM': '0',
# 'STATISTICS_STDDEV': '15.080766955253', 'STATISTICS_VALID_PERCENT': '0.2701'}
gdal.UseExceptions()
dataset = gdal.Open("usa_ppp_2020_constrained.tif", gdal.GA_ReadOnly)
(upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = dataset.GetGeoTransform()
print(dataset.GetRasterBand(1).GetStatistics(True, True))
print(dataset.GetRasterBand(1).GetMetadata())

# total locs to generate
totalStars = 100

kmWide = 75.56

# total pop
# 321392026 old number
totalPopulation = 301960220

rands = [0] * totalStars
randsFound = [0] * totalStars
r = 0
while (r < totalStars):
    rands[r] = np.random.randint(1, totalPopulation)
    randsFound[r] = 0
    r += 1

resultInt = 0
resultX = [0] * totalStars
resultY = [0] * totalStars
densityValues = [0] * totalStars

i = 0
runningTotal = 0
find = 3150000000
while (i < 62976):
    print(i, '/', 62976)
    j = 1000
    if (i == 62000):
        j = 976
    data = dataset.GetRasterBand(1).ReadAsArray(0, i, 430711, j)
    #masked_data = np.ma.masked_equal(data, dataset.GetRasterBand(1).GetNoDataValue())
    #valid_data = masked_data.compressed();
    (y_index, x_index) = np.nonzero(data > 0)

    k = 0
    l = 0
    imax = len(data[(y_index, x_index)])
    #while (i < imax):
    for (y, x) in zip(*(y_index, x_index)):
        value = data[y, x]
        #print(value)

        runningTotal = runningTotal + value
        randLoop = 0
        while (randLoop < totalStars):
            if (runningTotal > rands[randLoop]):
                if (randsFound[randLoop] == 0):
                    # found
                    randsFound[randLoop] = 1
                    x_coords = x * x_size + upper_left_x + (x_size / 2) # add half the cell size
                    y_coords = (y + i) * y_size + upper_left_y + (y_size / 2) # to center the point
                    noiseX = random.random() * x_size - (x_size / 2) # add some noise
                    noiseY = random.random() * y_size - (y_size / 2)
                    x_coords = x_coords + noiseX
                    y_coords = y_coords + noiseY
                    #print(y, x)

                    if (x != 62975 and y != 999 and x != 0 and y != 0):
                        value = value + max(0, data[y-1, x]) + max(0, data[y-1, x-1]) + max(0, data[y, x-1]) + max(0, data[y, x+1]) + max(0, data[y+1, x+1]) + max(0, data[y+1, x]) + max(0, data[y-1, x+1]) + max(0, data[y+1, x-1])
                    else:
                        value = value * 5

                    densityValues[resultInt] = max(1, math.sqrt(value) / 10)
                    
                    print("Found", y_coords, x_coords, value)
                    
                    resultX[resultInt] = x_coords
                    resultY[resultInt] = y_coords
                    resultInt += 1
            randLoop += 1
                
    #print("Total:", runningTotal)
    print(runningTotal)
    #while (k < 430711):
    #    while (l < j):
    #        if (masked_data[l, k] != 0):
    #            print(masked_data[l, k])
    #        l += 1
    #    k += 1
    #print(total)
    #print(i)
    i += 1000

rrr = 0
while (rrr < totalStars):
    print(resultY[rrr], " ", resultX[rrr])
    rrr += 1

#
#
#

points = gpd.GeoSeries()

kml = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
"""

def generateShapes():
    x = 0
    # generate star for each point
    while (x < totalStars):
        i = 0
        j = 2

        kmWidePerStar = kmWide / densityValues[x]

        # alaska debuff / make the fewer stars larger
        if (resultY[x] > 50):
            if (np.random.random() < 0.75):
                continue
            else:
                kmWidePerStar *= 1.5

        start = geopy.Point(resultY[x], resultX[x])

        global kml
        kml = kml + "<Placemark><name>Star " + str(x + 1) + """</name><Style><IconStyle><Icon/></IconStyle><LineStyle><color>ff0000ff</color><width>1</width></LineStyle></Style><LineString><tessellate>1</tessellate>
        <coordinates>
        """
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

print(len(points), "coords generated with", str(totalStars), "needed")

generateShapes();

print("Shapes generated");

kml = kml + """
</Document>
</kml>"""

filename = "output/" + datetime.now().strftime('%Y%m%d_%H%M%S') + "_" + str(totalStars) + "s_" + str(kmWide).replace(".", "-") + "km.kml"

with open(filename, "a") as f:
    f.write(kml);
