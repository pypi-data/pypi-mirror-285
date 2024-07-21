import argparse
import os
import shutil
import zipfile

import wget

# setting up arguments:
parser =  argparse.ArgumentParser(prog='python -m medimage')
argparse.ArgumentParser(description='Download dataset for MEDimage package tests, tutorials and other demos.')
parser.add_argument("--download-data", default=False, action='store_true',
    help="If specified, downloads MEDimage data for testing, \
        tutorials and demo then organizes it in the right folders.")
parser.add_argument("--full-sts", default=False, action='store_true',
    help="If specified, will download the full STS dataset used in tutorials. Defaults to False.")
parser.add_argument("--sts-subset", default=True, action='store_true',
    help="If specified, will download a subset of the STS dataset for the tutorials. Defaults to True.")
parser.add_argument("--download-tutorials", default=False, action='store_true',
    help="If specified, will download the notebook tutorials \
        from the package repository and organize it locally. Defaults to False.")
args = parser.parse_args()

if args.download_data:
    # download no-sts data (IBSI and glioma test data)
    print("\n================================ Downloading IBSI data ================================")
    try:
        wget.download(
        "https://sandbox.zenodo.org/record/1106515/files/MEDimage-Dataset-No-STS.zip?download=1",
        out=os.getcwd())
    except Exception as e:
        print("MEDimage-Dataset-No-STS.zip download failed, error:", e)
    
    # unzip data
    print("\n================================ Extracting IBSI data  ================================")
    try:
        with zipfile.ZipFile(os.getcwd() + "/MEDimage-Dataset-No-STS.zip", 'r') as zip_ref:
            zip_ref.extractall(os.getcwd())
        # delete zip file after extraction
        os.remove(os.getcwd() + "/MEDimage-Dataset-No-STS.zip")
    except Exception as e:
        print("MEDimage-Dataset-No-STS.zip extraction failed, error:", e)
    
    # Organize data in the right folders
    # IBSI tests data organization
    print("\n============================= Organizing data in folders  =============================")
    try:
        shutil.move(os.getcwd() + "/ibsi-test-data" + "/CTimage", 
                    os.getcwd() + "/notebooks" + "/ibsi" + "/data/CTimage")
    except Exception as e:
        print("Failed to move ibsi-test-data/CTimage folder, error:", e)
    try:
        shutil.move(os.getcwd() + "/ibsi-test-data" + "/Filters", 
                    os.getcwd() + "/notebooks" + "/ibsi" + "/data/Filters")
    except Exception as e:
        print("Failed to move ibsi-test-data/Filters folder, error:", e)
    try:
        shutil.move(os.getcwd() + "/ibsi-test-data" + "/Phantom", 
                    os.getcwd() + "/notebooks" + "/ibsi" + "/data/Phantom")
    except Exception as e:
        print("Failed to move ibsi-test-data/Phantom folder, error:", e)
    try:
        shutil.rmtree(os.getcwd() + "/ibsi-test-data")
    except Exception as e:
        print("Failed to delete ibsi-test-data folder, error:", e)
    
    # tutorials data organization
    try:
        shutil.move(os.getcwd() + "/tutorials-data" + "/DICOM", 
                    os.getcwd() + "/notebooks" + "/tutorial" + "/data/DICOM")
    except Exception as e:
        print("Failed to move tutorials-data/DICOM folder, error:", e)
    try:
        shutil.move(os.getcwd() + "/tutorials-data" + "/IBSI-CT", 
                    os.getcwd() + "/notebooks" + "/tutorial" + "/data/IBSI-CT")
    except Exception as e:
        print("Failed to move tutorials-data/IBSI-CT folder, error:", e)
    try:
        shutil.move(os.getcwd() + "/tutorials-data" + "/NIfTI", 
                    os.getcwd() + "/notebooks" + "/tutorial" + "/data/NIfTI")
    except Exception as e:
        print("Failed to move tutorials-data/NIfTI folder, error:", e)
    try:
        shutil.rmtree(os.getcwd() + "/tutorials-data")
    except Exception as e:
        print("Failed to remove tutorials-data folder, error:", e)

    # download sts data (multi-scans tutorial data)
    if args.full_sts:
        # get data online
        print("\n============================ Downloading full STS dataset  ============================")
        try:
            wget.download(
            "https://sandbox.zenodo.org/record/1106516/files/MEDimage-STS-Dataset.zip?download=1",
            out=os.getcwd())
        except Exception as e:
            print("MEDimage-STS-Dataset.zip download failed, error:", e)
        
        # unzip data
        print("\n============================ Extracting full STS dataset   ============================")
        try:
            with zipfile.ZipFile(os.getcwd() + "/MEDimage-STS-Dataset.zip", 'r') as zip_ref:
                zip_ref.extractall(os.getcwd())
                # remove zip file after extraction
            os.remove(os.getcwd() + "/MEDimage-STS-Dataset.zip")
        except Exception as e:
            print("MEDimage-STS-Dataset.zip extraction failed, error:", e)
        
        # organize data in the right folder
        print("\n============================= Organizing data in folders  =============================")
        try:
            shutil.move(os.getcwd() + "/DICOM-STS-Organized", 
                    os.getcwd() + "/notebooks" + "/tutorial" + "/data" + "/DICOM-STS")
        except Exception as e:
            print("Failed to move DICOM-STS-Organized folder, error:", e)

    elif args.sts_subset:
        # get data online
        print("\n==================== Downloading second part of data (STS subset) =====================")
        try:
            wget.download(
            "https://sandbox.zenodo.org/record/1106515/files/MEDimage-Dataset-STS-McGill-001-005.zip?download=1",
            out=os.getcwd())
        except Exception as e:
            print("MEDimage-Dataset-STS-McGill-001-005.zip download failed, error:", e)
        
        # unzip data
        print("\n===================== Extracting second part of data (STS subset) =====================")
        try:
            with zipfile.ZipFile(os.getcwd() + "/MEDimage-Dataset-STS-McGill-001-005.zip", 'r') as zip_ref:
                zip_ref.extractall(os.getcwd())
                # remove zip file after extraction
            os.remove(os.getcwd() + "/MEDimage-Dataset-STS-McGill-001-005.zip")
        except Exception as e:
            print("MEDimage-Dataset-STS-McGill-001-005.zip extraction failed, error:", e)
        
        # organize data in the right folder
        print("\n============================= Organizing data in folders  =============================")
        try:
            shutil.move(os.getcwd() + "/STS-McGill-001-005", 
                    os.getcwd() + "/notebooks" + "/tutorial" + "/data" + "/DICOM-STS")
        except Exception as e:
            print("Failed to move STS-McGill-001-005 folder, error:", e)

if args.download_tutorials:
    # get data online
    print("\n======================== Downloading notebooks from repository ========================")
    try:
        wget.download(
            "https://drive.google.com/uc?export=download&id=1B-8DD6QxEV-yE-PlRDr45PV6fu5slRnZ&confirm=t&uuid=9dc786da-ed31-4818-a77f-e7ff6f4038c2",
            out=os.getcwd())
    except Exception as e:
        print("Notebooks download failed, error:", e)
    # unzip data
    print("\n============================ Extracting notebooks zip file ============================")
    try:
        with zipfile.ZipFile(os.getcwd() + "/notebooks.zip", 'r') as zip_ref:
            zip_ref.extractall(os.getcwd())
            # remove zip file after extraction
        os.remove(os.getcwd() + "/notebooks.zip")
    except Exception as e:
        print("notebooks.zip extraction failed, error:", e)
