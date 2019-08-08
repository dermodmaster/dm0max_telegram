import simplekml
import sys
path='dump1090-127_0_0_1-1907261.txt'

inputpath = input("Pfad?")

if inputpath != "":
   path = inputpath


rawdata = open(path,'r')

airplanes = []
airplanedata = []

num_lines = sum(1 for line in open(path,'r'))

print("Reading Data... FOUND "+str(num_lines)+" LINES")
for line in rawdata:
    line = line.rstrip()
    line = line.split(',')

    #CHECK IF PLANE EXISTS
    if line[0] in airplanes:
        planeindex = airplanes.index(line[0])        
    else:
        airplanes.append(line[0])
        airplanedata.append([])
        planeindex = airplanes.index(line[0])   

    airplanedata[planeindex].append(line)
print("Finished!!!")
print("Found "+str(len(airplanes)-1)+" airplanes in Data")
print("===ALL AIRPLANES BY HEXIDENT===")
index=0
for plane in airplanes:
    if index > 0:
        print(str(index)+". "+plane)
    index+=1

maxheight = input("Maximale Höhe?")

#KML POINT GENERATOR
kmlpoint = simplekml.Kml()
style = simplekml.Style()
style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
for i in range(0, len(airplanedata)):
   for datarow in airplanedata[i]:
      if datarow[1] != "altitude(meter)" and int(datarow[1]) < int(maxheight):
         pnt = kmlpoint.newpoint()
         pnt.name=""
         pnt.description = datarow[11]+" "+datarow[4]+" "+datarow[5]+" "+datarow[0]+" Höhe:"+datarow[1]+" Lat. "+datarow[2]+" Long. "+datarow[3]
         pnt.coords = [(datarow[3],datarow[2],datarow[1])]
         pnt.style = style
         pnt.altitudemode = simplekml.AltitudeMode.relativetoground
filename = input("Dateiname?")
kmlpoint.save(filename+"_POINTS.kml")

#KML LINE GENERATOR
kml = simplekml.Kml()
for i in range(0, len(airplanedata)):
   planecoords=[]
   for datarow in airplanedata[i]:
      if datarow[1] != "altitude(meter)" and int(datarow[1]) < int(maxheight):
         planecoords.append((datarow[3],datarow[2],datarow[1]))
         #print(planecoords)

         lin = kml.newlinestring(name=airplanedata[i][0][11],
                                 description=airplanedata[i][0][4]+" "+airplanedata[i][0][5]+" "+airplanedata[i][0][0],
                                 coords=planecoords)
         lin.extrude = 0
         lin.altitudemode = simplekml.AltitudeMode.relativetoground
kml.save(filename+"_LINES.kml")
