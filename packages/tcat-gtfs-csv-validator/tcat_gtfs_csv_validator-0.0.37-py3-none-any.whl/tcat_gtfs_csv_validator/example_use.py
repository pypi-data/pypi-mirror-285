# simple example of the use of the gcv validator
 
from tcat_gtfs_csv_validator import gcv_test_release
from tcat_gtfs_csv_validator import exceptions as gcvex

data_type = 'gtfs_pathways'
schema_version = 'v1.0'
path = 'PUT PATH TO ZIP FILE OR DIRECTORY HERE'

print("simple_test: trying calling test_release")

try:
    gcv_test_release.test_release(data_type, schema_version, path)
except gcvex.GCVError as err:
    print("Test Failed\n")
    print(err) 
else: # if no exceptions
    print("Test Succeeded")