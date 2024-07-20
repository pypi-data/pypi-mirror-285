from PIL import Image
from PIL.ExifTags import TAGS
from shapely.geometry import Point
from datetime import datetime

def get_exif_data(image_file):
    """Read EXIF data"""
    try:
        with Image.open(image_file) as img:
            # verify if image is valid
            img.verify()
            # read exif-data
            exif_data = img._getexif()
            if exif_data is not None:
                return {TAGS.get(tag): value for tag, value in exif_data.items()}
            else:
                return {}
    # if image is not valid
    except (IOError, SyntaxError):
        return {}

def get_if_exist(data, key):
    """Get metadata if exists"""
    return data[key] if key in data else None

def convert_to_degrees(value):
    """Convert exif coordinate to degrees"""
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def get_point(exif_data):
    if 'GPSInfo' in exif_data:

        # Get exif coordinates
        gps_info = exif_data['GPSInfo']
        gps_latitude = get_if_exist(gps_info, 2)
        gps_latitude_ref = get_if_exist(gps_info, 1)
        gps_longitude = get_if_exist(gps_info, 4)
        gps_longitude_ref = get_if_exist(gps_info, 3)
        
        # Convert to point
        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = convert_to_degrees(gps_latitude)
            if gps_latitude_ref != "N":
                lat = -lat
            lon = convert_to_degrees(gps_longitude)
            if gps_longitude_ref != "E":
                lon = -lon
            return Point(lon, lat)

def get_date_time(exif_data):
    """Get datetime from exif metadata"""

    date_time_string = exif_data.get("DateTimeOriginal", None)
    if date_time_string is not None:
        return datetime.strptime(date_time_string, '%Y:%m:%d %H:%M:%S')

def get_image_metadata(image_path):
    """Get all metadata we need for photo-processing"""

    exif_data = get_exif_data(image_path)
    geometry = get_point(exif_data)
    date_time = get_date_time(exif_data)

    if geometry is not None:

        return {
            "geometry": geometry,
            "date_time": date_time
        }
