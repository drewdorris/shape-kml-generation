from osgeo import gdal
from osgeo import gdal_array
import numpy as np
import time
import random

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
total = 100

rands = [0] * total
randsFound = [0] * total
r = 0
while (r < total):
    rands[r] = np.random.randint(1, 321392026)
    randsFound[r] = 0
    r += 1

resultInt = 0
resultX = [0] * total
resultY = [0] * total

densityValues = [0] * total

i = 0
runningTotal = 0
find = 3150000000
found = False
datasetTotal = 321392026
while (i < 62976):
    print(i)
    j = 1000
    if (i == 62000):
        j = 976
    data = dataset.GetRasterBand(1).ReadAsArray(0, i, 430711, j)
    #masked_data = np.ma.masked_equal(data, dataset.GetRasterBand(1).GetNoDataValue())
    #valid_data = masked_data.compressed();
    (y_index, x_index) = np.nonzero(data > 0)
    #print(masked_data)
    #print(np.ma.mean(masked_data))
    #print(masked_data.count())
    #print(type((y_index, x_index)))
    #print(type(y_index))
    #print(len(data[(y_index, x_index)]))
    #print(data[(y_index, x_index)])
    #print((y_index, x_index))
    #print(data[500, i - 1])
    k = 0
    l = 0
    imax = len(data[(y_index, x_index)])
    #while (i < imax):
    for (y, x) in zip(*(y_index, x_index)):
        value = data[y, x]
        #print(value)
        #print(x)
        #print(y)
        runningTotal = runningTotal + value
        randLoop = 0
        while (randLoop < total):
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
                    print(y, x)
                    print("Found", y_coords, x_coords, value)

                    if (x != 62975 and y != 1000 and x != 0 and y != 0):
                        value = value + max(0, data[y-1, x]) + max(0, data[y-1, x-1]) + max(0, data[y, x-1]) + max(0, data[y, x+1]) + max(0, data[y+1, x+1]) + max(0, data[y+1, x]) + max(0, data[y-1, x+1]) + max(0, data[y+1, x-1])
                    else:
                        value = value * 5

                    densityValues[randLoop] = value
                    
                    print("Found", y_coords, x_coords, value)
                    
                    resultX[resultInt] = x_coords
                    resultY[resultInt] = y_coords
                    resultInt += 1
            randLoop += 1
        if (runningTotal > find):
            if (found == False):
                print(value)
                print("WOOOOOO!!!!!!")
                x_coords = x * x_size + upper_left_x + (x_size / 2) # add half the cell size
                y_coords = (y + i) * y_size + upper_left_y + (y_size / 2) # to center the point
                noiseX = random.random() * x_size - (x_size / 2) # add some noise
                noiseY = random.random() * y_size - (y_size / 2)
                x_coords = x_coords + noiseX
                y_coords = y_coords + noiseY
                
                print(x_coords, y_coords)
                print(x, y)
                print(x_size, y_size)
                print(upper_left_x, upper_left_y)
                print(x_rotation, y_rotation)
                
                
                found = True
                
    #print("Total:", runningTotal)
    
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
while (rrr < total):
    print(resultY[rrr], " ", resultX[rrr])
    rrr += 1
