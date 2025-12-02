## PBF Fileformat

PBF is a fileformat to store osm files mor efficiently.

You can download pbf's from here [OSM exports for Wien by BBBike.org](https://download.bbbike.org/osm/bbbike/Wien/)

```
osmconvert Wien.osm.pbf --out-osm -o=Wien.osm
```

But I found a better way to do that below.

## Downloading via OSM Webwizzard

This tool is included with sumo

### Windows:

```
PS C:\Program Files (x86)\Eclipse\Sumo\tools> py .\osmWebWizard.py
```

### Linux:

```
> osmWebWizard.py
```

Navigate to the region of interest

Press download (It will log where the exported files will be stored)

For me it's `C:\Users\<username>\Sumo\<date>`

## Generating trips in in this region

generate random trips:

### Linux:
`randomTrips.py`

### Windows:
`python "C:\Program Files (x86)\Eclipse\Sumo\tools\randomTrips.py"`

With parameters:
`-n ./data/neulengbach_sumo-webtools-osm.net.xml.gz -o ./data/routes.rou.xml --end 3600 --period 1.5 --vehicle-class passenger --allow-fringe`

For some reason it does not generate vehicles, so that's all for now. Probably need to do that in python?

## Communication between python and sumo

Just run make in the root of the project to start sumo via python and load the correct files

`make`