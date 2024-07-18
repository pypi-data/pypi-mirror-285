# support functions for gtfs-csv-validator

# TODO - would like this to be a class

import os as os
import re as re
import sqlite3 as sql
import pandas as pd
from jsonschema import validate as jsvalidate
import json
from pathlib import Path

import tcat_gtfs_csv_validator # need to get module path, maybe there is a better way...
from tcat_gtfs_csv_validator import exceptions as gcvex

# Uses: https://github.com/python-jsonschema/jsonschema

# import a csv file into a sqlite database table
# attribute names will be taken from the header row of the csv file 
# this is a generic function which takes any csv file and imports that
# file into a sqlite table - the table will be named with the filename
# of the csv file
# first argument is the name/path of the csvfile to be converted to the table
# second argument is the name of the table to be created
def csv_to_table(file_name, table_name, con):
    gcv_debug("csv_to_table",2)
    # skipinitialspace skips spaces after (comma) delimiters
    # lines that start with # (commented lines) will be ignored 
    df = pd.read_csv(file_name, skipinitialspace='True', comment="#")
    
    # tablename is first argument, returns number of rows
    df.to_sql(table_name, con, if_exists='fail', index=False) 

# takes as input a schema definition csv file and creates a table
# from it, schema is the name of the data schema - should be pathways,
# flex or osw, version is the version number
# this function will read the file schema_version_schema.csv
# to get the schema definition
def create_schema_tables(data_type, schema_version, con):
    gcv_debug("begin create_schema_tables")

    if(len(tcat_gtfs_csv_validator.__path__) !=1):
        raise Exception("unexpected path length in gcv_support")

    mod_path = Path(tcat_gtfs_csv_validator.__path__[0])
    dir_path = mod_path / 'schemas' / data_type / schema_version

    table_names = []
    if(data_type == 'gtfs_pathways'):
        table_names = ["levels", "pathways", "stops"]
    elif(data_type == 'gtfs_flex'):
        table_names = ["booking_rules", "location_groups", "stop_times"]
    else:
        raise gcvex.GCVUnexpectedDataType(data_type) 

    for table_name in table_names:
        file_path = dir_path / (table_name + "_schema.csv")
        gcv_debug("reading file " + file_path.name,2) 
        df = pd.read_csv(file_path, skipinitialspace='True', comment='#')
        create_table = "CREATE TABLE '" + table_name + "'("  
        for row in df.itertuples(index=True, name=None):
            if row[0] != 0:
                create_table += ", "
            create_table += row[1] + " " + row[4]
        create_table += ");" # strict; // removed strict was causing issues with library version 
      
        gcv_debug("query: " + create_table,2)
        cur = con.cursor()
        cur.execute(create_table)
        gcv_debug("schema table " + table_name + " created")
    
    gcv_debug("schema_tables created")

def check_schema(file_path, schema_table, file_table, con):
    gcv_debug("Checking schema: " + str(file_path))

    # load pathways, flex file into table...
    # file_table contains the data from the csv file to be checked
    # schema_table is the table that matches the appropriate schema
    csv_to_table(file_path, file_table, con)

    cur = con.cursor()

    # figure out which attributes exist in the csv file
    # and create the appropriate insert command
    # get list of col names from schema_table
    # get list of col names from file_name (table)
    # one optoin - PRAGMA table_info(foo)
    # schema table is strange  
    schema_table_info = cur.execute("PRAGMA table_info('" + schema_table + "')").fetchall()
    file_name_info = cur.execute("PRAGMA table_info('" + file_table + "')").fetchall()

    # table_info returns lists of tuples - each row in that list 
    # represents one attr, I want the attr name, which is col 1
    schema_table_attrs = [tuple[1] for tuple in schema_table_info]
    file_name_attrs = [tuple[1] for tuple in file_name_info]

    query = "insert into '" + schema_table + "' select "
    first_attr = True
    for attr in schema_table_attrs:
        if(first_attr == True):
            first_attr = False
        else:
            query += ', '
        
        if(attr in file_name_attrs):  
            query += attr 
        else:
            query += "NULL"

    # add end of query
    query += " from " + file_table 

    gcv_debug(query,2)

    fail = False
    err_msg = ''
    try:
        cur.execute(query)
    except (sql.IntegrityError, sql.DataError) as err:
        ## TODO Raise schema check failed error with whatever part of error as error msg
        fail = True
        err_msg += "Schema check failed on: " + str(file_path.name) + " Error: " + str(err) + "\n\n" 
    except sql.Error as err:
        fail = True
        err_msg += "Unexpected SQL error on: " + str(file_path.name) + " Error: " + str(err) + "\n\n" 

    gcv_debug("finished checking schema on " + str(file_path.name) + " result " + str(fail))

    if(fail == True):
        raise gcvex.GCVSchemaTestError(err_msg)

def check_rules(data_type, schema_version, con, dir_path):
    gcv_debug("begin check rules") 

    if(len(tcat_gtfs_csv_validator.__path__) !=1):
        raise Exception("unexpected path length in gcv_support")

    mod_path = Path(tcat_gtfs_csv_validator.__path__[0])
    rules_file = mod_path / 'rules' / (data_type + "_" + schema_version + "_rules.csv")

    df = pd.read_csv(rules_file, skipinitialspace='True', 
        comment='#')
    cur = con.cursor()

    for row in df.itertuples(index=True, name=None):
        # for each line - read sql, execute sql on appropriate table (tablename?)
        rule_name = row[1]
        fail_msg = row[2]
        rule_sql = row[3]    
        gcv_debug("\tChecking rule: " + rule_name)
        
        gcv_debug("Rule sql: " + rule_sql,2)
        fail = False
        err_msg = ''
        try:
            cur.execute(rule_sql) 
        except (sql.IntegrityError, sql.DataError) as err: #TODO - which errors?
            fail = True
            err_msg += "Rules check failed on: " + str(dir_path.stem) + " Error: " + str(err) + "\n\n" 
            # continue if we get an expected sql error - indicates test failed
        except sql.Error as err:
            fail = True
            err_msg += "Unexpected SQL error on: " + str(dir_path.stem) + " Error: " + str(err) + "\n\n" 
            raise # raise if we get an unexpected sql error - indicates code issue
            
        row = cur.fetchone()
        if row is not None:
            err_msg += "\nFAIL:" + rule_name + " failed " + fail_msg
            err_msg += "\n on row " + str(row)
            fail = True
        else:
            gcv_debug("\t\tSuccess: " + rule_name + " succeeded")

        if(fail == True):
            raise gcvex.GCVRuleTestError(err_msg)

def print_schema_tables(data_type, con):
    cur = con.cursor()
    table_names = []
    if(data_type == 'gtfs_pathways'):
        table_names = ["levels", "pathways", "stops"]
    elif(data_type == 'gtfs_flex'):
        table_names = ["booking_rules", "location_groups", "stop_times"]
    else:
        raise gcvex.GCVUnexpectedDataTypeError(data_type)

    for table_name in table_names:
        cur.execute("Select * from " + table_name)
        gcv_debug(cur.fetchall())


def drop_all_tables(data_type, con):
    cur = con.cursor()
    table_names = []
    if(data_type == 'gtfs_pathways'):
        table_names = ["levels", "pathways", "stops", "levels_file", "pathways_file", "stops_file"]
    elif(data_type == 'gtfs_flex'):
        table_names = ["booking_rules", "location_groups", "stop_times"]
    else:
        raise gcvex.GCVUnexpectedDataTypeError(data_type)
    
    for table_name in table_names:
        try:
            cur.execute("drop table " + table_name)
        except sql.OperationalError as err:
            # skip tables not found error
            pass
    
def check_locations_geojson(data_type, schema_version, ifile_path):
    gcv_debug("Testing geojson file: " + str(ifile_path))
        
    if(len(tcat_gtfs_csv_validator.__path__) !=1):
        raise Exception("unexpected path length in gcv_support")

    mod_path = Path(tcat_gtfs_csv_validator.__path__[0])
    
    # get jsonschema for flex locations.geojson file
    sfile_path = mod_path / 'schemas' / data_type / schema_version / 'locations_geojson_jsonschema.json'
    #sfile_path = sdir_path + "locations_geojson_jsonschema.json" 
    jsonschema_file = open(sfile_path, "r")
    locations_schema = json.load(jsonschema_file)
    jsonschema_file.close()
    gcv_debug(locations_schema,2)

    ifile_path 
    ijsonschema_file = open(ifile_path, "r")
    locations_instance = json.load(ijsonschema_file)
    ijsonschema_file.close()

    try:
        jsvalidate(locations_instance, locations_schema)
    
    except Exception as err:
        raise gcvex.GCVGeoJsonCheckError("test schema check on locations.geojson failed on: " + str(ifile_path.name) + "\n")
    else:
        gcv_debug("flex locations geojson test succeeded")


def test_csv_file(data_type,file_path,con):
    gcv_debug("Testing csv file: " + str(file_path))
    # data_type is pathways, or flex 
    if(data_type == 'gtfs_pathways'):
        if(re.search('levels', file_path.name, re.IGNORECASE) != None):  
            schema_table = 'levels'
            file_table = 'levels_file'
        elif(re.search('pathways', file_path.name, re.IGNORECASE) != None):  
            schema_table = 'pathways'
            file_table = 'pathways_file'
        elif(re.search('stops', file_path.name, re.IGNORECASE) != None):  
            schema_table = 'stops'
            file_table = 'stops_file'
    elif(data_type == 'gtfs_flex'):
        if(re.search('booking_rules', file_path.name, re.IGNORECASE) != None):  
            schema_table = 'booking_rules'
            file_table = 'booking_rules_file'
        elif(re.search('location_groups', file_path.name, re.IGNORECASE) != None):  
            schema_table = 'location_groups'
            file_table = 'location_groups_file'
        elif(re.search('stop_times', file_path.name, re.IGNORECASE) != None):  
            schema_table = 'stop_times'
            file_table = 'stops_times_file'
    else:
        raise gcvex.GCVUnexpectedDataTypeError(data_type)
        
    # file_path, data_type, con
    check_schema(file_path, schema_table, file_table, con)

# debug_log function provides internal support for debugging for the gcv
# intended use is to replace the internals of this function with code 
# to handle debug messages as the dev wants - for example - print statement
# to print debug info to console or leave empty to have no debug messages
# allows multiple levels of priority...
def gcv_debug(log_msg, priority=1):
    """function to support debugging messages for the gcv""" 
    #if(priority == 1):
    #    print(log_msg)

# debug_log function provides internal support for logging for the gcv
# intended use is to replace the internals of this function with code 
# to handle log messages - expect to replace this empty function with 
# calls to logging in the core library
def gcv_log(log_msg):
    """function to support logging for gcv"""

