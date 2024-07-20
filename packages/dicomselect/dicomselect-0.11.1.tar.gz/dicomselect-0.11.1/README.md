# dicomselect: DICOM database and conversion software

**dicomselect** is a Python tool that simplifies the process of creating [SQLite](https://www.sqlite.org/) databases from directories containing `.dcm` files. Once the database is created, you can easily perform SQL-like queries on the data directly within Python. Additionally, **dicomselect** allows you to convert query results into various file formats supported by [SimpleITK](https://simpleitk.org/), providing flexibility in working with your DICOM data.

## Installation

**Python 3.10 or higher.** You can install this project using `pip`. If you haven't already, it's recommended to create a virtual environment to isolate project dependencies.

```bash
pip install dicomselect
```

## Documentation

Read the [documentation](https://diagnijmegen.github.io/dicomselect/).

## Example

Clone this repo, install **dicomselect**, then run this example in the repo.

```python
from dicomselect import Database
from pathlib import Path

db_path = Path('tests/output/example.db')
db_path.parent.mkdir(exist_ok=True)

# initialize the Database object with a path to the to-be-created SQLite database file
db = Database(db_path)

# create the .db file, using test data as the input directory.
db.create('tests/input/ProstateX', max_workers=4)

with db as query:
    # we only want to convert images with patient_id "ProstateX-0000" and image_direction "transverse"
    query_0000 = query.where('patient_id', '=', 'ProstateX-0000'
                             ).where('image_direction', '=', 'transverse')

    # print out a detailed extraction of our query
    print(query_0000)

# initialize the Plan object, with a template of DICOM headers for our conversion
# (note: dcm to dcm conversion is possible, if you only need restructuring of your data)
plan = db.plan('{patient_id}/prostateX_{series_description}_{instance_creation_time}', query_0000)

# ensure these properties are set
plan.target_dir = 'tests/output/example'
plan.extension = '.mha'
plan.max_workers = 4

# print out a detailed structure of our intended conversion
print(plan.to_string())

plan.execute()
```

Check out the results in `tests/output/example`.