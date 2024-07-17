# ONS metadata validation tool

## Background
This project is for automatically validating metadata templates that accompany IDS data deliveries. The fields in a filled metadata template are each checked against a set of defined conditions. 

For example, many fields are mandatory; many have a maximum number of characters; some fields are not allowed to contain spaces or special characters; and so on.

A metadata template with missing mandatory values or other issues with its format or content will prevent the accompanying dataset from being ingested. This then requires the back-and-forth of resubmission, and causes delays.

## What it does

This tool produces an excel report detailing failed validation checks for a given metadata template. There are also two optional outputs:

* A commented version of the input file, where cells with validation issues are highlighted and a mouseover note names each check that has failed.

* An edited version of the input file, where cells with easily-fixed issues such as missing full stops or trailing whitespace have been automatically updated.

*Note that some metadata requirements cannot be programmatically validated. Some human inspection will always be necessary, for example to sense-check free text fields.*

The tool is designed to work with metadata templates from v2.0 onwards. When pointed at a v2.1 file, it should identify the version and update its expectations of the form's format without requiring specific input from the user.

## Documentation

This readme is written for the benefit of end users, such as the CMAR team. It aims to make minimal assuptions about previous experience.

More technical documentation for future developers and maintainers can be found in the documentation folder.

Future versions of this tool will increase the supporting information available in the validation output report, for example by listing the exact set of checks run for each variable.

## Contact

metadata.validation.tool@ons.gov.uk

Please contact us if you wish to report any issues or bugs, or to request features. Which tables of the output report were most useful? Did you prefer the aggregated tables, or the commented version with individual cells highlighted?

Also, we cannot currently guarantee that there will be no false positives or false negatives in the output, so your feedback is very valuable!

Please also contact us if you are using this tool and haven't yet spoken to us, the developers. We wish to keep in contact with our community of users.

# Using the tool

## Installation

*The commands below are for use in a command prompt terminal, such as Anaconda Powershell.*

To install this package:
`pip3 install ons-metadata-validation`

## Basic usage

Default settings have been set so that a general non-technical user will not often need to specify optional parameters.

The only parameter that must be specified each time to tool is used is the location of the filled metadata template to validate. This can be specified as an absolute or relative path.

Thus, to use as CMAR with all default settings:
`python3 -m ons_metadata_validation "path/to/file.xlsx"`

This will produce an excel file reporting on failed validation checks. It will be saved in the same folder as the input file.

Note that the ability to process all metadata templates in a specified folder is planned for a future release.

## Optional configurations

Optional parameters always come after the filename when calling the command.

### variable_check_set
This tool is designed for users of at various pipeline stages and in various contexts. Some template variables are populated later, and therefore might not exist yet for upstream users. This parameter is used to select the appropriate set of variables to check.

* default: "cmar"
* choices: ["cmar", "full"]

Example:
    `python3 -m ons_metadata_validation "path/to/file.xlsx" variable_check_set="full"`

### save_report
Whether or not to save the output report.

* default: True
* choices: True, False

Example:
    `python3 -m ons_metadata_validation "path/to/file.xlsx" save_report=False`

### save_commented_copy
Whether or not to save a copy of the metadata template with invalid cells highlighted and commented. Please note that you must then update and resubmit the original file - do not edit and submit this copy!

* default: True
* choices: True, False

Example:
    `python3 -m ons_metadata_validation "path/to/file.xlsx" save_commented_copy=True`

### save_corrected_copy
Some simple validation issues, such as missing full stops, double spaces, or trailing whitespace, can be fixed programmatically. Setting this parameter to True will save an edited copy of the original file.

* default: True
* choices: True, False

Example:
    `python3 -m ons_metadata_validation "path/to/file.xlsx" save_corrected_copy=True`


### destination_folder
By default, all outputs are saved in the same folder as the input file. However, you can specify a different location if you wish. This is only for specifying the output folder; the *names* of individual outputs combine the input file's name with a description indicating the type of output.

* default: None

Example:
    `python3 -m ons_metadata_validation "path/to/file.xlsx" destination_folder="some/other/directory"`

# Reading the output report

## Types of checks

Validation checks are considered to be "hard", "soft", or "comparative".		
		
Hard checks are conditions that can be conclusively measured automatically. Failing a hard check means that something is definitely wrong and needs changing. This also means that hard check fails will usually also cause an ingest failure if untreated, since the ingest process also has fixed expectations about machine-readable content and formats.		
		
Soft checks are checks that require inspection, but not necessarily action, if they fail. Either they relate to style recommendations  that aren't strict requirements, or they involve checking something that can't be perfectly measured automatically. For example, we may expect a certain style of response most of the time, but there may be corner cases where unusual answers are still acceptable and correct.		
		
Comparative checks involve more than one cell value at a time. For example, a column of table names might require that each name be unique within that column. Or, for consistency, a table name appearing on one sheet might be required to also appear on a list of tables from a previous sheet.		

## Output tables

|            Sheet            |     Variables      |                                                                                                     Description                                                                                                     |
|-----------------------------|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Short % overview            | All mandatory      | each row is a tab & variable name combination; columns list the % of records that are missing or failed at least one check.                                                                                         |
| Long % overview             | All mandatory      | each row is a tab & variable name combination; columns are fail %s for every check.                                                                                                                                 |
| Missing values              | All mandatory      | each row details the cells with missing values for a single variable.                                                                                                                                               |
| Fails by cell               | All mandatory      | each row details the names of all hard and soft checks failed by a single cell.                                                                                                                                     |
| Fails by check              | All mandatory      | each row details the cells of a single variable that have failed a particular hard or soft check.                                                                                                                   |
| Fails by value              | All mandatory      | each row details a value appearing in a variable, all the cells that value appears in, and all the hard and soft checks that value fails. NOTE: this view is experimental and has some known bugs with cell ranges. |
| Comparative checks          | Comparative only   | each row details one instance of a failed comparative check.                                                                                                                                                        |
| Non mandatory fails by cell | Non-mandatory only | each row details the names of all hard and soft checks failed by a single cell, including missing values. Non-mandatory variables only.                                                                             |

