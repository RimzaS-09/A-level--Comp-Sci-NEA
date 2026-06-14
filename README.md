# A-level--Comp-Sci-NEA
The code, tests, and documentation for my A level Computer Science NEA, based off the AQA spec.

Licenced under MIT.

## What is my project about?
This project is a **navigation software** that is designed to allow the user to do three main tasks:

- View a **locally stored** map of the UK, and save specific locations (like their home or workplace)
- Allow for **simple pathfinding** to give the user the shortest route between two points
- Create a **complex route-planner** for connecting multiple different points in the shortest path possible (AKA the *travelling salesman problem*)

A more thorough breakdown can be viewed on my writeup.

## How is Geodata handled?
Geodata is handled via `MBTiles`, an open source file specification standard by [Mapbox](https://github.com/mapbox/mbtiles-spec "View the spec here") that combines a traditional relational database structure (SQL) containing metadata for the tiles, with a gzipped compressed binary format to hold tile data within. Each row in the `tiles` table of the database contains data and metadata for 1 specific tile on the map grid.

A *tile* in this case refers to a square section of a map grid that can contain either raster or vector information of that specific area. Each tile can contain a subtile for further division.

My program specifically uses vector tilesets to represent this information. More information of this can be viewed in Mapbox's [website](https://docs.mapbox.com/data/tilesets/guides/vector-tiles-introduction/) or their [vector tile specification](https://github.com/mapbox/vector-tile-spec)

## Getting started
> [!WARNING]
> This code was tested using python version `3.13`. Ensure you have this version installed to avoid potential errors.




### Getting the geodata
First, you'll need some map data for the program to use. You can load any `.mbtiles` file into the program, so long as it uses **mapbox vector tiles** within the SQL table for the data, and follows version **1.3** of the mbtile spec

However I strongly recommend that you use the vector tiles database that is provided by `ordinance survey`, as it provides a basemap for the whole of the UK. You can download it (for free!) [here](https://www.ordnancesurvey.co.uk/products/os-open-zoomstack)

Once you download it, you can simply move it into `/data/map/` and the program should be able to read it.

### Prerequirements
Before you can continue, ensure you have these prerequirements installed:
* [Python](https://www.python.org/downloads/release/python-31314/) version 3.13
* [PySide6](https://pypi.org/project/PySide6/) (Via PIP)
* [Google protobuf](https://pypi.org/project/protobuf/#description) (Via PIP)
* (Optional) If you want to benchmark some of the solutions as well, you'll need the [PyPerf](https://github.com/psf/pyperf) library as well

### Running the program
Once everything's installed, you should be able to start the program by running `runscript.bat` for windows, or `runscript.sh` for linux \:D