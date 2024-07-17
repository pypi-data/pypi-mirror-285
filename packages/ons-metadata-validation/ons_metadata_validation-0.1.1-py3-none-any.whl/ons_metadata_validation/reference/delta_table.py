"""
Add changes here, all are run sequentially so v2.1 is run then v2.2 etc

DELTA_TABLE = {
    "v2.1": {
        "DatasetFile_column_seperator": {
            "name": "Column Separator",
        }
    }
    # if we made a mistake and reverted back to the original spelling
    # the changes would be applied
    "v2.2": {
        "DatasetFile_column_seperator": {
            "name": "Column Seperator",
        }
    }
}

empty dict means nothing is changed
"""

DELTA_TABLE = {
    "v2.1": {
        "DatasetFile_file_format": {
            "enum": ["CSV", "JSON", "Parquet", "JSON Multi-Line"]
        },
        "DatasetFile_column_seperator": {"name": "Column Seperator"},
        "Variables_variable_length_precision": {
            "name": "Variable precision/scale"
        },
        "BackOffice_restrictions_for_access": {
            "enum": [
                "The data may only be accessed by specific individuals",
                "No additional conditions",
            ]
        },
        "BackOffice_research_outputs": {
            "enum": [
                "Data owner must be sent all research outputs",
                "Data owner must approve all research outputs",
                "No conditions",
            ]
        },
        "BackOffice_project_approval": {
            "enum": [
                "Data owner must give approval to projects applications",
                "Data owner must be informed of project applications",
            ]
        },
        "BackOffice_disclosure_control": {
            "enum": [
                "No additional conditions, standard statistical disclosure control to apply",
                "Special statistical disclosure rules apply",
            ]
        },
        "BackOffice_research_disclaimer": {
            "enum": [
                "Data source requires a special disclaimer when outputs are sent to researchers",
                "No conditions",
            ]
        },
    }
}
