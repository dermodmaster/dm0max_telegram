import simplekml
import sys
path='dump1090-127_0_0_1-190619.txt'

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

didifoundyourdesiredairplane = False
while (not didifoundyourdesiredairplane):
    eingabe = input("KML für welche HEXIDENT erstellen?  ").upper()
    try:
        myairplaneindex = airplanes.index(eingabe)
        didifoundyourdesiredairplane = True
        print("Flug Objekt hat die ID: "+myairplaneindex)
    except:
        print("Dieses Flugobjekt gibt es nicht")

#KML LINE GENERATOR
filename = input("Wie soll ich deine KML Datei nennen? ")
kml = simplekml.Kml()
planecoords=[]
for datarow in airplanedata[myairplaneindex]:
    planecoords.append((datarow[3],datarow[2],datarow[1]))
print(planecoords)

lin = kml.newlinestring(name=airplanedata[myairplaneindex][0][11],
                        description=airplanedata[myairplaneindex][0][4]+" "+airplanedata[myairplaneindex][0][5]+" "+airplanedata[myairplaneindex][0][0],
                        coords=planecoords)
lin.extrude = 0
lin.altitudemode = simplekml.AltitudeMode.relativetoground
kml.save(filename+"_LINES.kml")

#KML POINT GENERATOR
kmlpoint = simplekml.Kml()
style = simplekml.Style()
style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
for datarow in airplanedata[myairplaneindex]:
    pnt = kmlpoint.newpoint()
    pnt.name=""
    pnt.description = datarow[11]+" "+datarow[4]+" "+datarow[5]+" "+datarow[0]+" Höhe:"+datarow[1]+" Lat. "+datarow[2]+" Long. "+datarow[3]
    pnt.coords = [(datarow[3],datarow[2],datarow[1])]
    pnt.style = style
    pnt.altitudemode = simplekml.AltitudeMode.relativetoground
kmlpoint.save(filename+"_POINTS.kml")
