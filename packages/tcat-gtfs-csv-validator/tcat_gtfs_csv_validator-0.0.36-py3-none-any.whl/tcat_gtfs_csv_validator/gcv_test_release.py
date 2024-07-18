# test fncs for gtfs-csv-validator

import fnmatch
import os as os
import re as re
import shutil
from tcat_gtfs_csv_validator import gcv_support as gcvsup
from tcat_gtfs_csv_validator import exceptions as gcvex
import sqlite3 as sql 
from zipfile import is_zipfile
from zipfile import ZipFile
from pathlib import Path

def test_release(data_type, schema_version, input_path):
# input_path may be a zip file or a directory containting a release
# directories can be easier for testing...

    try:
        dir_path = None #
        extracted = False
        con = None
        temp_dir_path = None

        # extract from zip file
        if(is_zipfile(input_path)):
            zf = ZipFile(input_path)
            temp_dir_path = Path.cwd() / 'tempdir'
            zf.extractall(temp_dir_path) # not sure if this takes a path object
            extracted = True
                        
            # this is awkwared, but don't know how to count number of dir entries
            first = True
            for child in temp_dir_path.iterdir():
                if(first == False):
                    raise gcvex.GCVError("too many files in tempdir, zip extraction error") 
                if(child.is_dir() == False):
                    raise gcvex.GCVError("got file not dir in tempdir, zip extraction error")
                if(child.name != '__MACOSX'):
                    dir_path = child
                    first = False 

        else:
            # assume input is a directory
            dir_path = Path(input_path)
        
        # set up sqlite connection
        # create a temp db in RAM
        # schemas are stored in csv files for clarity and ease of maintenance
        con = sql.connect(':memory:') 

        gcvsup.gcv_debug("testing release in directory: " + str(dir_path))

        # create all tables for this particular data_type
        gcvsup.create_schema_tables(data_type, schema_version, con)
        
        gcvsup.gcv_debug("schema tables created")

        # read all files from directory test_files/data_schema/version
        #file_list = os.listdir(dir_path)

        # Do the schema checks
        fail = False
        error_log = ''
        for file_path in dir_path.iterdir():
            try:
                test_file(data_type, schema_version, file_path, con)
            except (gcvex.GCVSchemaTestError, gcvex.GCVGeoJsonCheckError) as err:
                # catch GCV schema test exception
                # add exception message to log with file name
                # continue as long as the exception is a gcv schema test exception
                error_log += str(err)   
                fail = True

        # if schema check failed, pass back log of errors
        if(fail):
            raise gcvex.GCVSchemaTestError(error_log) 

        # else if schema check passed, now check rules
        gcvsup.gcv_debug("checking " + data_type + " rules on " + str(dir_path))

        gcvsup.check_rules(data_type, schema_version, con, dir_path)

    except gcvex.GCVError as err:   
        clean_up(data_type, con, extracted,temp_dir_path) 
        raise gcvex.GCVError(str(err))
    except Exception as err:
        clean_up(data_type, con, extracted,temp_dir_path) 
        raise 
    else:
        if temp_dir_path != None:
            clean_up(data_type, con, extracted,temp_dir_path) 
    
def clean_up(data_type, con, extracted,dir_path): 
    if(con != None):
        gcvsup.drop_all_tables(data_type, con)
        con.close()
    if(extracted):
        shutil.rmtree(dir_path) # remove the temp directory

def test_file(data_type, schema_version, file_path, con):

    if fnmatch.fnmatch(file_path.name, "*.txt"):
        # check schema for csv files
        # loads file_name into schema_table checks for errors
        gcvsup.test_csv_file(data_type, file_path,con)
    elif(data_type == 'gtfs_flex' and fnmatch.fnmatch(file_path.name, "*.geojson")):
        # check the geojson file for flex
        gcvsup.check_locations_geojson(data_type, schema_version, file_path)
    elif(fnmatch.fnmatch(file_path.name, ".*")):
        gcvsup.gcv_log("skipping file: " + str(file_path))
    # ignore files with no extension
    elif(fnmatch.fnmatch(file_path.name, "__*")):
        gcvsup.gcv_log("skipping file: " + str(file_path))
    else:
        raise gcvex.GCVError("unexpected file type - expect .txt or .geojson files (flex only), please be sure to specify the directory containing the release. error from:" + str(file_path))

