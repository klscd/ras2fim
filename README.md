# RAS2FIM <img src="https://github.com/NOAA-OWP/ras2fim/blob/main/doc/ras2fim_agency_20211018.png" align="right" alt="ras2fim agency" height="80"> <br> <br>
## <i>Creation of flood inundation raster libraries and rating curves from HEC-RAS models </i>

<img src="https://github.com/NOAA-OWP/ras2fim/blob/main/doc/ras2fim_logo_20211018.png" align="right"
     alt="ras2fim logo" width="160" height="160">

**Description**:  Starting with geospatially attributed one-dimensional HEC-RAS floodplain models, these scripts are used to create a library of flood depth inundation rasters for a range of storm water discharges (flow).  HEC-RAS models are cut to roughly match the limits of the [National Water Model's {NWM}](https://water.noaa.gov/about/nwm) stream designations (hydrofabric).  For each matching NWM stream, a synthetic rating curve is created based on 'reach averaged' flood depths as determined from the HEC-RAS simulations.  The intent it to create a library of flood depth inundation grids with a ccorresponding rating curve that can be paired with the National Water Model's discharges determination and forecasting to create real-time and predictive floodplain mapping from a detailed HEC-RAS 1-D model.

  - **Technology stack**: Scripts were all developed in Python 3.8.11.  Use is intended within a custom 'ras2fim' [Anaconda environment](https://www.anaconda.com/products/individual) running on a Windows OS.  Prior to running these scripts, the user is required to install and run [HEC-RAS v 6.3](https://github.com/HydrologicEngineeringCenter/hec-downloads/releases/download/1.0.25/HEC-RAS_63_Setup.exe).<br><br>
  - **Status**:  Version 1 - Inital release.  Refer to to the [CHANGELOG](CHANGELOG.md).<br><br>
  - **Related Project**:  Inspiration for this repository was to develop flood inundation map libraries to replace Height Above Nearest Drainage (HAND) as calculated with the [FIM inundation mapping](https://github.com/NOAA-OWP/inundation-mapping) repository.<br><br>
  - **Overview Video**: [Link to overview video of ras2fim](https://www.youtube.com/watch?v=TDDTRSUplVA)<br>
          Since the video was first produced, ras2fim has continued to evolve, but there is still valuable information in the video that you want to view. Notes for viewing:<br>
          The total runtime is 5 min and 41 seconds.<br>
          - The first part of the video shows folder pathing that has since been update and this part should be ignored. Updated folder pathing including donwloading from ESIP S3 is discussed later in this document.<br>
          - The second part, at appx 1:00 in, shows examples of how to run ras2fim.py and its parameters. This is also now out of date and should be ignored.<br>
          - When the video gets too appx 1:45 seconds and shows the ras2fim.py actively processing, it is still largely applicable.<br>
<br>

**RAS2FIM Wiki**:
More detail regarding RAS2FIM is located on the project's Wiki page.
<p align="center">
<a href="https://github.com/NOAA-OWP/ras2fim/wiki">
<img src="https://github.com/NOAA-OWP/ras2fim/blob/dev/doc/button_go-to-rasfim-wiki.png" alt="Go To Wiki" width="342">
</a>
</p>

**Overview**:
![](https://github.com/NOAA-OWP/ras2fim/blob/dev/doc/ras2fim_overview.png)
![](https://github.com/NOAA-OWP/ras2fim/blob/dev/doc/ras2fim_sample_output.png)

## Default Folder Structure

While ras2fim.py and other tools have optional parameters allowing pathing to any folder(s), we do recommended folder structure as shown below based on your `c:` drive.

![ras2fim default folder structure image](https://github.com/NOAA-OWP/ras2fim/blob/dev/doc/default_folder_structure.png)

All documentation in this repo are based on the default folder structure.

## Downloading Data from ESIP

<img src="https://github.com/NOAA-OWP/ras2fim/blob/main/doc/esip-logo.png" align="right" alt="esip logo" height="50">There are folders and files that will need to be downloaded locally prior to running the RAS2FIM code.  This data can be found in an Amazon S3 Bucket hosted by [Earth Science Information Partners (ESIP)](https://www.esipfed.org/). The data can be accessed using the AWS Command Line Interface (CLI) tools. AWS CLI installation details are shown below. This S3 Bucket (`s3://noaa-nws-owp-fim`) is set up as a "Requester Pays" bucket. Read more about what that means [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/RequesterPaysBuckets.html).

You will need permission from ESIP to access this data. Please contact Carson Pruitt (carson.pruitt@noaa.gov) or Fernando Salas (fernando.salas@noaa.gov) for assistance.


### Configuring the AWS CLI

1. [Install AWS CLI tools](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
2. [Configure AWS CLI tools](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)

### To test AWS CLI and access to ESIP

To list folders prior to download:
```
aws s3 ls s3://noaa-nws-owp-fim --requester-pays
```

## Output Samples
If you want to review a sample output for ras2fim.py, you can dowload a folder that was generated using five models in 12090301 HUC8.
```
aws s3 sync s3://noaa-nws-owp-fim/ras2fim/output_ras2fim C:\ras2fim_data\output_ras2fim --requester-pays
```

## Prior to Running the Code (if you choose to do some processing)

To do some test processing, you will need to download additional ESIP folders which include the `inputs` and the `OWP_ras_models` folders. We have provided a small sample set of five `models` based on 12090301 HUC8.  The `model` folder includes a number of sub-folders, one per model, that has gone through preprocessing steps to convert some raw HEC-RAS data to data which can be processed by `ras2fim.py`. `ras2fim.py` will create output rating curves, REMs and other output files.

While not yet determined, we may publish more `models` later, however, you are also welcome to create our own `models` and use the `ras2fim.py` tools.

The OWP tools to preprocess HEC-RAS data to OWP_ras_models is not yet available.
<br><br>

### (1) Get AWS Folder - Inputs
<img src="https://github.com/NOAA-OWP/ras2fim/blob/main/doc/AWS_logo.png" align="right" alt="aws logo" height="50"> The downloaded inputs folder is appx 14.3 Gb.
```
aws s3 sync s3://noaa-nws-owp-fim/ras2fim/inputs c:\ras2fim_data\inputs --requester-pays
```
This download will include the following files / folders:

1. Watershed Boundary Dataset (WBD): WBD_National.gpkg
2. The WBD_National.gkpg split into different gpkg files by HUC8: /WBD_HUC8/*
3. National Water Model (NWM) Flowline Hydrofabric: nwm_flows.gpkg
4. National Water Model to Watershed Boundary Lookup: nwm_wbd_lookup.nc
5. National Water Model (NWM) Catchments file: nwm_catchments.gpkg
<br><br>

### (2) Get AWS Folder - OWP_ras_models folder and OWP_ras_models_catalog.csv

At this point, ras2fim.py needs a file named OWP_ras_models_catalog.csv, or similar, and we have loaded a sample for you. It has some meta data that is used in the final output files. While the file must exist with the correct schema, it will not fail if records in it do not match.  This file may become optional at a later point, but for now, please include it and also add the `-mc` argument to `ras2fim.py`. eg. `-mc c:\ras2fim_data\OWP_ras_models\OWP_ras_models_catalog.csv` (or pathing of your choice of course, as is with most arguments).

To download the `OWP_ras_models` folder, you AWS CLI command will be (adjusting for path overrides if you like):
```
aws s3 sync s3://noaa-nws-owp-fim/ras2fim/OWP_ras_models c:\ras2fim_data\OWP_ras_models --requester-pays
```

### (3) Install HEC-RAS verion 6.3
<img src="https://github.com/NOAA-OWP/ras2fim/blob/main/doc/RAS_logo.png" align="right" alt="hec-ras logo" height="80">These RAS2FIM scripts are written to utilize the computational engine and supporting APIs from the U.S Army Corp of Engineers' [Hydrologic Engineering Center's River Analysis System {HEC-RAS}](https://www.hec.usace.army.mil/software/hec-ras/).  Download and install **HEC-RAS version 6.3** to your local machine.  Note: **the version (6.3) matters!**
<br><br>
The install package can be downloaded from [the USACE website](https://github.com/HydrologicEngineeringCenter/hec-downloads/releases/download/1.0.25/HEC-RAS_63_Setup.exe). Once installed, **open HEC-RAS on that machine** to accept the terrms and conditions and ensure that it will function on that machine prior to running any RAS2FIM scripts. Close HEC-RAS.
<br><br>

### (4) Clone the Git-hub repository
<img src="https://github.com/NOAA-OWP/ras2fim/blob/main/doc/Git_logo.png" align="right" alt="git logo" height="80"> Install [git](https://git-scm.com/downloads) onto your Windows machine. Next, clone this ras2fim reporitory on to your Windows machine (see note below). Path to the windows folder of your choice, then type:
```
git clone https://github.com/NOAA-OWP/ras2fim.git (see note below)
```
**Note: ras2fim V2 series has started development as of early November 2023. Initial check-ins for the default branch will fail for the short term future until an advanced version is ready.** When the CHANGELOG.md shows version check-ins starting with the phrase `V2.0.beta.x`, means the branch is not yet operational but you are still welcome to contibute to the new WIP branch. Once the usable versions have been merged, the CHANGELOG.md will start with the number of `v2.0.0.0`.
<br>
**If you want to view the last stable `V1` series, use the following git clone command which will come from the ras2fim `main (V1)` branch.**
```
git clone https://github.com/NOAA-OWP/ras2fim.git -b V1
```

### (5) Building and Testing ras2fim

Detailed instructions on setting up a ras2fim anaconda environment and running the ras2fim script can be in the [INSTALL](doc/INSTALL.md) document.
<br><br>

----
## Dependency Sources

* [HEC-RAS Version 6.3](https://github.com/HydrologicEngineeringCenter/hec-downloads/releases/download/1.0.25/HEC-RAS_63_Setup.exe).
* [Anaconda](https://www.anaconda.com/products/individual) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for Windows.
* National datasets - from AWS - See "Get AWS Folder - Inputs" section above.
* Runs on a Windows OS only - Tested on Windows 10.
* Tested on HEC-RAS 6.3 and default pathing is also set against v6.3.

## Limitations and Assumptions

Details coming soon.

## Known Issues & Getting Help

Please see the issue tracker on GitHub and the [Ras2Fim Wiki](https://github.com/NOAA-OWP/ras2fim/wiki) for known issues and getting help.

## Getting involved

NOAA's National Water Center welcomes anyone to contribute to the RAS2FIM repository to improve flood inundation mapping capabilities. Please contact Carson Pruitt (carson.pruitt@noaa.gov) or Fernando Salas (fernando.salas@noaa.gov) to get started.

----

## Open source licensing info
1. [TERMS](doc/TERMS.md)
2. [LICENSE](LICENSE)


----

## Credits and references

1. [Office of Water Prediction (OWP)](https://water.noaa.gov/)
2. [Goodell, C. R. (2014). Breaking the Hec-Ras Code: A User’s Guide to Automating Hec-Ras. H2ls.](https://www.kleinschmidtgroup.com/breaking-the-hec-ras-code-2/)
3. [Executive Summary, & Guidance, S. (n.d.). InFRM Flood Decision Support Toolbox. Usgs.Gov. Retrieved October 22, 2021](https://webapps.usgs.gov/infrm/pubs/FDST%20Map%20Submission%20Guidelines%20_vDec20.pdf)
4. [Collete, A. (2013). Python and HDF5: Unlocking Scientific Data. O’Reilly Media.](https://www.oreilly.com/library/view/python-and-hdf5/9781491944981/)
5. [Board on Earth Sciences and Resources/Mapping Science Committee, Committee on FEMA Flood Maps, Mapping Science Committee, Board on Earth Sciences & Resources, Water Science and Technology Board, Division on Earth and Life Studies, & National Research Council. (2009). Mapping the zone: Improving flood map accuracy. National Academies Press.](https://www.amazon.com/Mapping-Zone-Improving-Resilience-Preparedness/dp/0309130573)
6. [Dysarz, Tomasz. (2018). Application of Python Scripting Techniques for Control and Automation of HEC-RAS Simulations. Water. 10. 1382. 10.3390/w10101382. ](https://www.mdpi.com/2073-4441/10/10/1382)
7. [Documentation. (n.d.). River Analysis System. Army.Mil.](https://www.hec.usace.army.mil/software/hec-ras/documentation.aspx)

**Special Thanks to:** Cam Ackerman (US Army Corp of Engineers), Kristine Blickenstaff (US Geological Survey), Chris Goodell (Kleinschmidt Associates), Witold Krajewski (Iowa Flood Center), RoseMarie Klee (Texas Department of Transportation), David Maidment (University of Texas), Saul Nuccitelli (Texas Water Development Board), Paola Passalacqua (University of Texas), Jason Stocker (US Geological Survey), Justin Terry (Harris County Flood Control District)




