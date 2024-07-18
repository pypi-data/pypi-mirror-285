"""
Module Name: GoPro GPS Extract Using GPMF and Output to CSV
Author: Rifat Sabbir Mansur
Date: May 27, 2023
Description: This script extracts GPS data from a GoPro 360 video file and writes it to an CSV file.
    The script first converts the GPS data to GPX format, then to XML format, and finally to CSV format.
    Both 360 and MP4 files are supported.

Reference:
    GPXCSV: https://github.com/astrowonk/gpxcsv#installation-and-usage

"""
import sys
import os
import datetime
import gpmf
import gpxpy
import gpxpy.gpx
import xmltodict
import logging
# from gpxcsv import gpxtolist
import csv

# Path to video files
# 360 video file. This contains GPS data.
# VIDEO_FILE = "GS010027-003.360"  

# MP4 file. This contains GPS data.

# This file does not work. Maybe it does not retain the save GPS data from its parent file GH010025-001.mp4 
# VIDEO_FILE = "toy_vid.mp4"    

# This file does not work. Maybe it does not retain the save GPS data from its parent file GH010025-001.mp4
# VIDEO_FILE = "toy_vid_2.mp4"  

# i.e if video of duration 30 seconds, saves 1 frame per second = 30 frames saved in total
# if set to 2 then 15 frames saved in total
FRAMES_AFTER_NUMBER_OF_SECONDS = 1
VIDEO_FILE=''
def extract_metadata(video_file=VIDEO_FILE, output_dir=None, frames_after_number_of_seconds=FRAMES_AFTER_NUMBER_OF_SECONDS):
    sys.stdout.flush()
    # Create a directory for the output with current datetime
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Create the file
    # and output every level since 'DEBUG' is used
    # and remove all headers in the output
    # using empty format=''
    # Set the output directory
    if output_dir is None:
        output_dir = f"metadata_{video_file.replace('.','')}_{timestamp_str}"
    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)
    # Read the binary stream from the file
    try:
        stream = gpmf.io.extract_gpmf_stream(video_file)
    except FileNotFoundError:
        raise 'file not found'
        return
    # Extract GPS low level data from the stream
    gps_blocks = gpmf.gps.extract_gps_blocks(stream)
    # Parse low level data into more usable format
    gps_data = list(map(gpmf.gps.parse_gps_block, gps_blocks))

    # logging.debug(f"Found {len(gps_data)} GPS data points in the video file: {gps_data}")

    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_track.segments.append(gpmf.gps.make_pgx_segment(gps_data))

    # # Converting xml to python dictionary (ordered dict)
    data_dict = xmltodict.parse(gpx.to_xml())

    # logging.debug(f"GPX data in dictionary:\n {data_dict}")

    metadata_dict = data_dict['gpx']['trk']['trkseg']['trkpt']
    print(f'lenght of metadata dict {len(metadata_dict)}')
    # logging.debug(f"Metadata in dictionary:\n {metadata_dict}")

    HEADERS = ['time', 'latitude', 'longitude' ,'altitude', 'sym', 'fix', 'precision', 'speed_2d', 'speed_3d']

    # Creating a list of rows to be written in CSV
    rows = []
    # Creating a list where each element is in 'timestamp_lat_lon' format
    metadata_list = []

    # Opening CSV file for writing
    csv_file_path = os.path.join(output_dir, "metadata.csv")
    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=HEADERS)

        previous_timestamp = 0
        
        writer.writeheader()

        for row in metadata_dict:
            try:
                # Convert string to datetime object
                datetime_obj = datetime.datetime.strptime(row['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                # Convert string to datetime object
                datetime_obj = datetime.datetime.strptime(row['time'], "%Y-%m-%dT%H:%M:%SZ")

            # Convert datetime object to Unix timestamp
            unix_timestamp = int(datetime_obj.timestamp()) 

            # Skip if the difference between the current and previous timestamp is less than the saving rate
            # then continue to the next iteration
            # otherwise, save the current timestamp and continue to the next iteration
            # This is to save only one frames after desired number of seconds
            # if (unix_timestamp - previous_timestamp) < frames_after_number_of_seconds:
            #     continue
            # else:
            #     previous_timestamp = unix_timestamp

            # Append the timestamp, latitude, and longitude in the metadata_list
            metadata_list.append(f"{unix_timestamp}_{row['@lat']}_{row['@lon']}")

            rows.append({
                'time': unix_timestamp,
                'latitude': row['@lat'],
                'longitude': row['@lon'],
                'altitude': row['ele'],
                'sym': row['sym'],
                'fix': row['fix'],
                'precision': row['pdop'],
                'speed_2d': f"{row['extensions']['speed_2d']['value']} {row['extensions']['speed_2d']['unit']}",
                'speed_3d': f"{row['extensions']['speed_3d']['value']} {row['extensions']['speed_3d']['unit']}"
            })

        writer.writerows(rows)
    # Return the metadata list
    return metadata_list

