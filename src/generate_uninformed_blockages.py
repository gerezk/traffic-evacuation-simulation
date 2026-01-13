import generate_cars as gc
import xml.etree.ElementTree as ET

taz_file = "./tmp/DangerTAZ.taz.xml"
tree = ET.parse(taz_file)
root = tree.getroot()

dangerRoads = gc.getEdgesFromTaz(root, "Danger_Zone_0")

print(dangerRoads)