## TECHNICAL DETAILS

For the scripts in the Data_Processor to work, json files get generated which are used to specify and describe the 
formats of the input files and template files. The two kinds are described below:

###Json specification for input files
It has the following structure:

    {
      "formats": {}, 
      "header_row": 1, 
      "mappings": {
        "wind_speed": 18, 
        "satellite": 8, 
        "vdop": 10, 
        "elevation": 4, 
        ...
      }, 
      "header_list": [
        "datetime", 
        "longitude_decdeg", 
        "elevation", 
        "heading", 
        "speed_m/s", 
        ...
      ]
    }

The *"formats"* key points to an object will hold any specified formats for date/time fields.

The *"header_row"* key points to the specification for which row contains the column headers in the input file.

The *"mappings"* key points to an object in which each key represents a column header in the template file,
 and the value represents the column number where that data is located in the input file.
 
*For example if the template file has a column called "datetime" and the column which contains datetime data 
in the input file is called "readingDate" and it is column 8, the mappings object will have a key value pair*

    {"datetime": 8}
    
The *"header_list"* key points a list of all the headers which are in the template file that the data from the input file 
will be loaded into.

###Json specification file for templates
It has the following structure:

    {
        "fields": {
            "beacon_alarm_state": {
                "type": null, 
                "column_letter": "AP", 
                "column_number": 42
            }, 
            "fix": {
                "type": null, 
                "column_letter": "AD", 
                "column_number": 30
            }, 
            "speed_calculated": {
                "type": null, 
                "column_letter": "Z", 
                "column_number": 26
            }, 
            "temp_internal_f": {
                "type": null, 
                "column_letter": "AO", 
                "column_number": 41
            }, 
            "wind_direction": {
                "type": null, 
                "column_letter": "AT", 
                "column_number": 46
            }, 
            ...
        }, 
        "header_row": "1", 
        "header_list": [
            "beacon_id", 
            "short_id", 
            "julian_day", 
            "datetime", 
            "unix_timestamp", 
            "date", 
            "year", 
            "month", 
            "day", 
            "hour", 
            "minute", 
            ...
        ], 
        "row_template": {
            "beacon_alarm_state": null, 
            "fix": null, 
            "speed_calculated": null, 
            "temp_internal_f": null, 
            "wind_direction": null, 
            "satellite": null, 
            "datetime": null, 
            "modem_voltage": null, 
            "temp_internal_c": null, 
            ...
        }
    }

The *"fields"* key points to an object in which every key is named after a column in the template file.
Each key in the object points to a nested object which will have 3 fields:

* "type": which is supposed to represent the data type that that field should hold but will be null for all fields,
 as that feature is not implemented yet.
* "column_letter": which represents the excel style letter combination where that column is in the template file.
* "column_number": which represents the number of the column in the template file where the field is located. 

The *"header_row"* key points to the specification for which row contains the column headers in the template file.
    
The *"header_list"* key points a list of all the headers which are in the template file.

The *"row_template"* key points to a json object which represents what a row from the template would look like,
 if it were converted into a json object. All the keys will always point to null.
 
**In order for any of the code in this to work, these files need to be generated and the format needs to be maintained.**


        
    