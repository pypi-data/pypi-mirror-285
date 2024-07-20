from .tags_generated import version, tags_generated

DEFAULT_DICOM_TAGS = [
    "0008|0005",
    "0008|0008",
    "0008|0012",
    "0008|0013",
    "0008|0016",
    "0008|0018",
    "0008|0020",
    "0008|0021",
    "0008|0022",
    "0008|0023",
    "0008|0030",
    "0008|0031",
    "0008|0032",
    "0008|0033",
    "0008|0050",
    "0008|0060",
    "0008|0070",
    "0008|1010",
    "0008|1030",
    "0008|103e",
    "0008|1040",
    "0008|1090",
    "0010|0020",
    "0010|0030",
    "0010|0040",
    "0010|1010",
    "0010|21b0",
    "0012|0062",
    "0012|0063",
    "0018|0015",
    "0018|0020",
    "0018|0021",
    "0018|0022",
    "0018|0023",
    "0018|0024",
    "0018|0050",
    "0018|0080",
    "0018|0081",
    "0018|0083",
    "0018|0084",
    "0018|0085",
    "0018|0087",
    "0018|0088",
    "0018|0089",
    "0018|0091",
    "0018|0093",
    "0018|0094",
    "0018|1000",
    "0018|1030",
    "0018|1310",
    "0018|1312",
    "0018|1314",
    "0018|1315",
    "0018|5100",
    "0018|9087",
    "0020|000d",
    "0020|000e",
    "0020|0010",
    "0020|0032",
    "0020|0037",
    "0020|0052",
    "0020|1041",
    "0028|0002",
    "0028|0010",
    "0028|0011",
    "0028|0030",
    "0028|0100",
    "0028|0101",
    "0028|0106",
    "0028|0107",
    "0028|1050",
    "0028|1051",
    "0040|0244",
    "0040|0254"
]


table_values_len = max([len(name) for (name, _) in tags_generated.values()])
table_ljust = lambda s: s.ljust(table_values_len, ' ')
table_borders = '=' * table_values_len + ' ========= ========'
table_headers = f"{table_ljust('Name')} Name      Default?"
table_values = '''
'''.join([f'{table_ljust(name)} {tag} {"yes" if tag in DEFAULT_DICOM_TAGS else ""}' for tag, (name, _) in tags_generated.items()])

__doc__ = f"""
The following is an exhaustive list of DICOM tags that **dicomselect** recognizes. Rows marked 'Default' are included
during database creation by default.

**version {version}**

{table_borders}
{table_headers} 
{table_borders}
{table_values}
{table_borders}
"""
