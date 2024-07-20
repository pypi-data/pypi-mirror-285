from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime, parseaddr
from PIL import Image
from datetime import datetime
import io
from pathlib import Path
import shutil
import geopandas as gpd
import pandas as pd
from fotoviewer.read_exif import get_image_metadata
from fotoviewer import FOTOVIEWER_DATA_DIR, create_sub_dirs, date_time_file_prefix


def foto_file_name(date_time, img_file_name):
    """Construct new file name from date_time, sender and file_name"""

    # date_time to string
    date_time = date_time_file_prefix(date_time) 

    # create new filename
    img_file_name = Path(img_file_name)
    new_file_name = img_file_name.with_stem(f"{date_time}_{img_file_name.stem}")

    return new_file_name

def eml_file_name(msg_date_time, eml_file_name):
    """Construct new file name from date_time, sender and file_name"""

    if msg_date_time is None:
        date_time = datetime.now()
    else:
        date_time = msg_date_time


    # date_time to string
    date_time = date_time_file_prefix(date_time)

    # create new filename
    eml_file_name = Path(eml_file_name)
    new_eml_file_name = eml_file_name.with_stem(f"{date_time}_{eml_file_name.stem}")

    return new_eml_file_name

def get_date_time(img_date_time, msg_date_time):
        # if we don't have date-time info we use now as datetime
    date_time = img_date_time

    if date_time is None:
        date_time = msg_date_time
    
    if date_time is None:
        date_time = datetime.now()
    
    return date_time


def get_sender(from_header):
    if from_header:
        parsed_from_header = parseaddr(from_header)
        return parsed_from_header[0]


def parse_eml(eml_file: Path, datastore: Path, archive:Path):
    """Parse an eml-file to a list of dict

    Args:
        eml_file (Path): Path to eml-file
        datastore (Path): path to datastore for storing the image attachements
        archive (Path): path to store the eml-file after parsed

    Returns:
        list[dict]: dictionary with all image properties
    """
    data = []
    # Open the EML file
    with open(eml_file, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    # Get the email subject
    subject = msg['subject']

    # Get the email sender
    sender = get_sender(msg['From'])
    if sender is None:
        pass
    
    # Get the mail date_time 
    msg_date_time = msg["Date"]
    msg_date_time = parsedate_to_datetime(msg_date_time) if msg_date_time  else None

    # Get the email body
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get('Content-Disposition'))
            if content_type == 'text/plain' and 'attachment' not in disposition:
                body = part.get_payload(decode=True).decode(part.get_content_charset())
                break
    else:
        body = msg.get_payload(decode=True).decode(msg.get_content_charset())  


    # Parse all attachements as images
    for part in msg.iter_attachments():
        img_file_name = part.get_filename()
        content = part.get_payload(decode=True)

        with io.BytesIO(content) as image_file:
            # read exif from file_objec
            image_metadata = get_image_metadata(image_file)

            # only returns img if file is image and exif is complete
            if image_metadata is None:
                print(f"Attachment '{img_file_name}' is not a valid image with exif gps-info! (ignored)")
                continue
            else:
                
                # read all data from exif
                geometry = image_metadata["geometry"]
                img_date_time = image_metadata["date_time"]
                date_time = get_date_time(img_date_time, msg_date_time)

                # store file with a unique uuid
                img_path = datastore / foto_file_name(date_time, img_file_name)
                image_file.seek(0)
                img_path.write_bytes(image_file.read())
                data += [{"file_name":img_path.name, "sender": sender, "date_time":date_time, "subject":subject, "body": body, "geometry":geometry}]
    
    if eml_file.name.startswith(date_time_file_prefix(msg_date_time)):
        new_eml_file = archive.joinpath(eml_file.name)
    else:
        new_eml_file = archive.joinpath(eml_file_name(msg_date_time, eml_file.name))

    shutil.move(eml_file, new_eml_file)

    return data


def parse_emls(data_dir=FOTOVIEWER_DATA_DIR):
    """Parse emls in a data_directory with at least an 'inbox' sub-folder with emls.

    The sub-directories 'archive' and 'datastore' will be created and filled by this function

    Args:
        data_dir (PathLike, optional): Directory with inbox, datastore and archive. Defaults to FOTOVIEWER_DATA_DIR.    

    Raises:
        ValueError: _description_
        FileNotFoundError: _description_
    """

    # check if data_dir is specified
    if data_dir is None:
        raise ValueError("Value for 'data_dir' is None and should be fotoviewer root-directory (containing, inbox, archive and datastore)")
    else:
        data_dir = Path(data_dir)
    inbox = data_dir / "inbox"

    # if inbox exists we create other dirs
    if not inbox.exists():
        raise FileNotFoundError(f"inbox not found: {inbox}")
    else:
        create_sub_dirs(data_dir)
        archive = data_dir  / "archive"
        datastore = data_dir  / "datastore"

    # parse all emls in inbox
    data = []
    emls = list(inbox.glob("*.eml"))
    if len(emls) == 0:
        print("No emls to parse in {inbox}")

    for eml_file in emls:
        print(eml_file)
        data += parse_eml(eml_file, datastore=datastore, archive=archive)

    # convert to gdf
    
    if data:
        foto_gpkg = datastore.joinpath("fotos.gpkg")

        # define and transform GeoDataFrame
        gdf = gpd.GeoDataFrame(data, crs=4326)
        gdf.to_crs(28992, inplace=True)

        # concat to GeoPackage if allready existent
        if foto_gpkg.exists():
            gdf = pd.concat([gdf, gpd.read_file(foto_gpkg, engine="pyogrio")])
            gdf.drop_duplicates(subset=["file_name"], inplace=True)

        # write gdf to GeoPackage
        gdf.to_file(foto_gpkg, engine="pyogrio")
