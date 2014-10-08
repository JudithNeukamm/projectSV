# Read the CSV file and convert the latitude and longitude into x,y-coordinates into Kilometers.
# Anders Hast 5/6-2013

import vtk

import string
import math
import time


class ReadPointsCSV(object):
    
    def __init__(self):
        self.number = 0
        
    # Computes distance in Kilometers
    def distance(self, lat1, lon1, lat2, lon2):
        R = 6371
        dLat = math.radians(lat2-lat1)
        dLon = math.radians(lon2-lon1)
        lat1 = math.radians(lat1)
        lat2 = math.radians(lat2)
    
        a = math.sin(dLat/2.0) * math.sin(dLat/2.0) + math.sin(dLon/2.0) * math.sin(dLon/2.0) * math.cos(lat1) * math.cos(lat2) 
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) 
        d = R * c
        return d
    
    #Read Points
    def readPoints(self, inputfile):
        
        # all datas
        all_data = {}
        
        # Initialize
        LatMax = 0
        LatMin = 360
        LonMax = 0
        LonMin = 360
        tMin = 99999999999999
    
        # Open the file
        infile = open(inputfile)
        
        # Read one line
        line = infile.readline()
    
        # Loop through lines
        while line:
            
            # Split the line into data
            data = line.split(';')
            # Skip the commented lines
            if data and data[0][0] != '#':
                # Convert data into float
                # print data[0], data[1], data[2], data[3], data[4].split('--')[0]
                date, x, y, z, r = data[0].rstrip(';'), float(data[1].rstrip(';')), float(data[2].rstrip(';')),  float(data[3].rstrip(';')), float(data[4].split('--')[0])

                # Range selection
                # @see: http://www.zhang-liu.com/misl/map.html
                # Latitude (x): from south(deg) 44.3 - north(deg) 45.5
                # Longitude (y): from west(deg) 10.0 - east(deg) 12
                if x < 44.3 or x > 45.5 or y < 10 or y > 12:
                    # read next line
                    line = infile.readline()
                    continue

                # create one dataset for each month
                # date string example: '2014-09-23 18:31:02.300'
                year = date[:4]
                month = date[5:7]
                   
                if not all_data.has_key(year):
                    all_data[year] = {}

                if not all_data.get(year).has_key(month):
                    all_data.get(year)[month] = {
                        'points': vtk.vtkPoints(),
                        'scalar': vtk.vtkFloatArray(),
                        'tid': vtk.vtkFloatArray()
                    }

                row = string.split(date)
                adate = row[0].split('-')
                atime = row[1].split(':')
                temp = atime[2].split('.')
                atime[2] = temp[0]

                if atime[2] == '':
                    atime[2] = '00'
                t = time.mktime([int(adate[0]), int(adate[1]), int(adate[2]), int(atime[0]), int(atime[1]), int(atime[2]), 0, 0, 0])

                if x > LatMax:
                    LatMax = x
                if x < LatMin:
                    LatMin = x
                if y > LonMax:
                    LonMax = y
                if y < LonMin:
                    LonMin = y
                if t < tMin:
                    tMin = t

                # Insert floats into the point array
                all_data.get(year)[month]['points'].InsertNextPoint(x, y, z)
                all_data.get(year)[month]['scalar'].InsertNextValue(r)
                all_data.get(year)[month]['tid'].InsertNextValue(t)
    
            # read next line
            line = infile.readline()
    
        print LatMin, LatMax, LonMin, LonMax
        # Compute the range of the data
        x1 = self.distance(LatMin, LonMin, LatMax, LonMin)
        x2 = self.distance(LatMin, LonMax, LatMax, LonMax)
        y1 = self.distance(LatMin, LonMin, LatMin, LonMax)
        y2 = self.distance(LatMax, LonMin, LatMax, LonMax)
    
        for everyYear in all_data:
            for everyMonth in all_data[everyYear]:

                points = all_data[everyYear][everyMonth]['points']
                xx = x1
                l = points.GetNumberOfPoints()
                i = 0

                while i < l:
                    x, y, z = points.GetPoint(i)
                        
                    u = (x-LatMin)/(LatMax-LatMin)
                    x = (x-LatMin)/(LatMax-LatMin)*xx
            
                    # Not perfect conversion...
                    yy = (1-u)*y1+u*y2
                    y = (y-LonMin)/(LonMax-LonMin)*yy
                    points.SetPoint(i, x, y, z)
                    i += 1

        return all_data
