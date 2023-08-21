import os
import argparse
import numpy as np
from datetime import datetime
import pandas as pd
import shutil
import geopandas as gpd
import rasterio
import errno
from rasterio.features import shapes
from concurrent.futures import ProcessPoolExecutor, as_completed, wait
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry import MultiPolygon, Polygon, LineString, Point
import warnings

from shared_functions import get_changelog_version
from shared_variables import (R2F_OUTPUT_DIR_METRIC, R2F_OUTPUT_DIR_SIMPLIFIED_GRIDS, 
                              R2F_OUTPUT_DIR_FINAL, R2F_OUTPUT_DIR_Metric_Rating_Curves)

warnings.simplefilter(action='ignore',category=FutureWarning)


def produce_geocurves(feature_id, huc, rating_curve, depth_grid_list, version, geocurves_dir, polys_dir):
    """
    For a single feature_id, the function produces a version of a RAS2FIM rating curve 
    which includes the geometry of the extent for each stage/flow.
    
    Args:
        feature_id (str): National Water Model feature_id.
        huc (str): Derived from the directory names of the 05_hec_ras outputs which are organized by HUC12.
        rating_curve(str): The path to the feature_id-specific rating curve generated by RAS2FIM.
        depth_grid_list (list): A list of paths to the depth grids generated by RAS2FIM for the feature_id.
        version (str): The version number.
        output_folder (str): Path to output folder where geo version of rating curve will be written.
        polys_dir (str or Nonetype): Can be a path to a folder where polygons will be written, or None.
        
    """

    # Read rating curve for feature_id
    rating_curve_df = pd.read_csv(rating_curve)

    # Loop through depth grids and store up geometries to collate into a single rating curve.
    iteration = 0
    for depth_grid in depth_grid_list:
        # Interpolate flow from given stage.
        stage_mm = float(os.path.split(depth_grid)[1].split('-')[1].strip('.tif'))
        
        with rasterio.open(depth_grid) as src:
            # Open inundation_raster using rasterio.
            image = src.read(1)
            
            # Use numpy.where operation to reclassify depth_array on the condition that the pixel values are > 0.
            reclass_inundation_array = np.where((image>0) & (image != src.nodata), 1, 0).astype('uint8')

            # Aggregate shapes
            results = ({'properties': {'extent': 1}, 'geometry': s} for i, (s, v) in enumerate(shapes(reclass_inundation_array, 
                       mask=reclass_inundation_array>0,transform=src.transform)))
    
            # Convert list of shapes to polygon, then dissolve
            extent_poly = gpd.GeoDataFrame.from_features(list(results), crs='EPSG:5070')
            try:
                extent_poly_diss = extent_poly.dissolve(by='extent')
                extent_poly_diss["geometry"] = [MultiPolygon([feature]) if type(feature) == Polygon else feature for 
                                feature in extent_poly_diss["geometry"]]
                
            except AttributeError:  # TODO why does this happen? I suspect bad geometry. Small extent?
                continue

            # -- Add more attributes -- #
            extent_poly_diss['version'] = version
            extent_poly_diss['feature_id'] = feature_id
            extent_poly_diss['stage_mm_join'] = stage_mm
            if polys_dir != None:
                inundation_polygon_path = os.path.join(polys_dir, feature_id + '_' + huc + '_' + str(int(stage_mm)) + '_mm'+ '.gpkg')
                extent_poly_diss['filename'] = os.path.split(inundation_polygon_path)[1]
                
            if iteration < 1:  # Initialize the rolling huc_rating_curve_geo
                feature_id_rating_curve_geo = pd.merge(rating_curve_df, extent_poly_diss, left_on='stage_mm', right_on='stage_mm_join', how='right')
            else:
                rating_curve_geo_df = pd.merge(rating_curve_df, extent_poly_diss, left_on='stage_mm', right_on='stage_mm_join', how='right')
                feature_id_rating_curve_geo = pd.concat([feature_id_rating_curve_geo, rating_curve_geo_df])
            
            # Produce polygon version of flood extent if directed by user
            if polys_dir != None:
                extent_poly_diss['stage_m'] = stage_mm/1000.0
                extent_poly_diss = extent_poly_diss.drop(columns=['stage_mm_join'])
                extent_poly_diss['version'] = version
                extent_poly_diss.to_file(inundation_polygon_path, driver='GPKG')
            
            iteration += 1 
            
    feature_id_rating_curve_geo.to_csv(os.path.join(geocurves_dir, feature_id + '_' + huc + '_rating_curve_geo.csv'))


def manage_geo_rating_curves_production(ras2fim_output_dir, version, job_number, output_folder, overwrite, produce_polys):
    """
    This function sets up the multiprocessed generation of geo version of feature_id-specific rating curves.
    
    Args:
        ras2fim_output_dir (str): Path to top-level directory storing RAS2FIM outputs for a given run.
        version (str): Version number for RAS2FIM version that produced outputs.
        job_number (int): The number of jobs to use when parallel processing feature_ids.
        output_folder (str): The path to the output folder where geo rating curves will be written.
    """
    
    overall_start_time = datetime.now()
    dt_string = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    print (f"Started: {dt_string}")
            
    # Check job numbers and raise error if necessary
    total_cpus_available = os.cpu_count() - 1
    if job_number > total_cpus_available:
        raise ValueError('The job number, {}, '\
                          'exceeds your machine\'s available CPU count minus one ({}). '\
                          'Please lower the job_number.'.format(job_number, total_cpus_available))
    
    # Set up output folders.
    if not os.path.exists(ras2fim_output_dir):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), ras2fim_output_dir)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    else:
        if not overwrite:
            print("The output directory, " + output_folder + ", already exists. Use the overwrite flag (-o) to overwrite.")
            quit()
        else:
            shutil.rmtree(output_folder)
            os.mkdir(output_folder)
            
    # Make geocurves_dir
    geocurves_dir = os.path.join(output_folder, 'geocurves')
    if not os.path.exists(geocurves_dir):
        os.mkdir(geocurves_dir)

    # Create polys_dir if directed by user
    if produce_polys:
        polys_dir = os.path.join(output_folder, 'polys')
        if not os.path.exists(polys_dir):
            os.makedirs(polys_dir)
    else:
        polys_dir = None
            
    # Check version arg input.
    if os.path.isfile(version):
        version = get_changelog_version(version)
        print("Version found: " + version)
        
    # Define paths outputs
    simplified_depth_grid_parent_dir = os.path.join(ras2fim_output_dir, R2F_OUTPUT_DIR_METRIC, R2F_OUTPUT_DIR_SIMPLIFIED_GRIDS)  
    rating_curve_parent_dir = os.path.join(ras2fim_output_dir, R2F_OUTPUT_DIR_METRIC, R2F_OUTPUT_DIR_Metric_Rating_Curves)  
    
    # Create dictionary of files to process
    proc_dictionary = {}
    local_dir_list = os.listdir(simplified_depth_grid_parent_dir)
    for huc in local_dir_list:
        full_huc_path = os.path.join(simplified_depth_grid_parent_dir, huc)
        if not os.path.isdir(full_huc_path):
            continue
        feature_id_list = os.listdir(full_huc_path)
        for feature_id in feature_id_list:
            feature_id_depth_grid_dir = os.path.join(simplified_depth_grid_parent_dir, huc, feature_id)
            feature_id_rating_curve_path = os.path.join(rating_curve_parent_dir, huc, feature_id, feature_id + '_rating_curve.csv')
            try:
                depth_grid_list = os.listdir(feature_id_depth_grid_dir)
            except FileNotFoundError:
                continue
            full_path_depth_grid_list = []
            for depth_grid in depth_grid_list:
                full_path_depth_grid_list.append(os.path.join(feature_id_depth_grid_dir, depth_grid))
            proc_dictionary.update({feature_id: {'huc': huc, 'rating_curve': feature_id_rating_curve_path, 'depth_grids': full_path_depth_grid_list}})
        
    # Process either serially or in parallel depending on job number provided
    if job_number == 1:
        print("Serially processing " + str(len(proc_dictionary)) + " feature_ids...")
        for feature_id in proc_dictionary:
            produce_geocurves(feature_id, proc_dictionary[feature_id]['huc'], proc_dictionary[feature_id]['rating_curve'], 
                                      proc_dictionary[feature_id]['depth_grids'], version, geocurves_dir, polys_dir)
    
    else:
        print("Multiprocessing " + str(len(proc_dictionary)) + " feature_ids using " + str(job_number) + " jobs...")
        with ProcessPoolExecutor(max_workers=job_number) as executor:
            for feature_id in proc_dictionary:
                executor.submit(produce_geocurves, feature_id, proc_dictionary[feature_id]['huc'], 
                                proc_dictionary[feature_id]['rating_curve'], proc_dictionary[feature_id]['depth_grids'], 
                                version, geocurves_dir, polys_dir)
            
    # Calculate duration
    end_time = datetime.now()
    dt_string = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    print (f"Ended: {dt_string}")
    time_duration = end_time - overall_start_time
    print(f"Duration: {str(time_duration).split('.')[0]}")
    print()


if __name__ == '__main__':
    
    # Parse arguments
    parser = argparse.ArgumentParser(description = 'Produce Geo Rating Curves for RAS2FIM')
    parser.add_argument('-f', '--ras2fim_output_dir', help='Path to directory containing RAS2FIM outputs',
                        required=True)
    parser.add_argument('-v', '--version', help='RAS2FIM Version number, or supply path to repo Changelog',
                        required=False, default='Unspecified')
    parser.add_argument('-j','--job_number',help='Number of processes to use', required=False, default=1, type=int)
    parser.add_argument('-t', '--output_folder', help = 'Target: Where the output folder will be', required = True)
    parser.add_argument('-o','--overwrite', help='Overwrite files', required=False, action="store_true")
    parser.add_argument('-p','--produce_polys', help='Produce polygons in addition to geocurves.', required=False, default=False, action="store_true")
        
    args = vars(parser.parse_args())
    manage_geo_rating_curves_production(**args)