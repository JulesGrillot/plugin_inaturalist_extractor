# {{ plugin_name }} - Documentation

> **Description:** {{ description }}  
> **Author and contributors:** {{ author }}  
> **Plugin version:** {{ version }}  
> **QGIS minimum version:** {{ qgis_version_min }}  
> **QGIS maximum version:** {{ qgis_version_max }}  
> **Source code:** {{ repo_url }}  
> **Last documentation update:** {{ date_update }}

----

## What's the point
This tool allows you to extract specific data from IGN's BD TOPO®. The extraction is based on either an extent drawned by the user on the map canvas or a layer's extent. The data is based on the WFS service published by IGN with the [Géoplateforme](https://www.ign.fr/geoplateforme).

## How to use it

Only 4 steps are required to use the BD TOPO® Extractor :

1. [Select the extent you want to use to extract data.](https://julesgrillot.github.io/plugin_bd_topo_extractor/index.html#select-an-extent)

1. [Select the output CRS for you exported data.](https://julesgrillot.github.io/plugin_bd_topo_extractor/index.html#select-output-crs)


1. [Select if you want to save the result or not, and if so the output folder and output format.](https://julesgrillot.github.io/plugin_bd_topo_extractor/index.html#select-output-format)

### User Interface

<p align="center">
  <img src="https://raw.githubusercontent.com/JulesGrillot/plugin_inaturalist_extractor/main/inaturalist_extractor/resources/images/plugin_ui.png?raw=true" alt="user_interface"/>
</p>

### 1. Select an extent

You can either draw a rectangle on the map (default) or select a layer in your project and use it's extent.

#### Choose your weapon

2 checkboxes allow you to select how you want to get the extent used for the data extraction :

- `Draw an extent to extract data :` if you want to use a drawned extent. Then you have to click the `Draw an extent` button and create a rectangle on the map.

- `Use layer extent to extract data :` if you want to use a layer's extent. Check it and then use the combobox to select the layer you want to use.

#### Error messages

The selected layer or extent cover more than 10K observations, this is the maximum number of observations you can extract at a time.

<p align="center">
  <img src="https://raw.githubusercontent.com/JulesGrillot/plugin_inaturalist_extractor/main/inaturalist_extractor/resources/images/too_many_obs_error.png?raw=true" alt="too_many_obs_error"/>
</p>

### 2. Select output CRS

You can select a Coordinate Reference System (default is the one from the QGIS project)

### 3. Select output format

#### Save result as temporary layer

If you don't want to save the extracted data as layers (default) you only have to select the output crs with the combobox.

#### Save result as layer

If you want to save the extracted data as layers you have to :

- select the output crs with the combobox.
- check the `Save the results :` checkbox.
- select if you want to add the exported data to the project (default) or not.
- select the output format, `GeoPackage` (default), `Shapefile` or `GeoJSon`.
- select the output folder to save the new layers inside a folder called `iNaturalist_Export_yyyymmdd_HHMM`.

### Launch the extraction

The extraction begin when you press the `OK` button.

## Additional tools

By clicking the iNaturalist button, you'll be redirected to iNaturalist’s website. By clicking the `Documentation` button, you'll be redirected to this page. By clicking the `Metadata` button, you'll be redirected to the about page of iNaturalist. An OpenStreeMap basemap is automatically added to the project if there is no layer in it. So the user can draw a rectangle.

```{toctree}
---
caption: Usages
maxdepth: 1
---
Installation <usage/installation>
```

```{toctree}
---
caption: Contribution guide
maxdepth: 1
---
development/contribute
development/environment
development/documentation
development/translation
development/packaging
development/testing
development/history
```
