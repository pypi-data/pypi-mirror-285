import os
import sqlite3
from pathlib import Path

import pytest

import dicomselect
from dicomselect import Database, DICOMImageReader


def prepare(db_path: Path):
    for path in [db_path, db_path.with_suffix('.pending.db')]:
        if path.exists():
            os.remove(path)
    db_path.parent.mkdir(exist_ok=True)


def test_input():
    prepare(db_path := Path('tests/output/test.db'))

    def custom_header_func(reader: DICOMImageReader):
        return {'custom_header': 'text', 'custom_header_int': 23}

    db = Database(db_path)
    db.create('tests/input/ProstateX', max_workers=2, custom_header_func=custom_header_func)

    with sqlite3.connect(db_path) as conn:
        count = conn.execute('SELECT COUNT(*) FROM DATA;').fetchone()[0]
        assert count > 0, f'{db_path} contains no data ({count} > 0)'
        assert count == 111


def test_input_existing():
    prepare(db_path := Path('tests/output/test_existing.db'))

    db = Database(db_path)
    db.create('tests/input/ProstateX', max_workers=2)

    to_delete = 30
    count = lambda: conn.execute('SELECT COUNT(*) FROM DATA;').fetchone()[0]

    with sqlite3.connect(db_path) as conn:
        count_before = count()
        assert count_before == 111
        conn.execute(f'DELETE FROM data WHERE ROWID IN (SELECT ROWID FROM data ORDER BY ROWID LIMIT {to_delete})')
        count_after = count()
        assert count_after == count_before - to_delete

    def custom_header_func(reader: DICOMImageReader):
        return {'custom_header': 'text', 'custom_header_int': 23}

    db.create('tests/input/ProstateX', max_workers=2, custom_header_func=custom_header_func, update=True)

    with sqlite3.connect(db_path) as conn:
        count_after = count()
        assert count_after == count_before


def test_input_empty():
    prepare(db_path := Path('tests/output/test_empty.db'))

    db = Database(db_path)

    with pytest.raises(sqlite3.DataError):
        db.create('tests/input/ProstateX-empty')


def test_input_flat():
    prepare(db_path := Path('tests/output/test_flat.db'))

    db = Database(db_path)
    db.create('tests/input/ProstateX-flat', max_workers=1)

    with sqlite3.connect(db_path) as conn:
        count = conn.execute('SELECT COUNT(*) FROM DATA;').fetchone()[0]
        assert count > 0, f'{db_path} contains no data ({count} > 0)'
        assert count == 9, f'{db_path} contains an unexpected amount of data ({count} != 7)'


def test_input_duplicates():
    for flag, expected in [(1, 7), (2, 8)]:
        prepare(db_path := Path(f'tests/output/test_duplicates_{flag}.db'))

        db = Database(db_path)
        db.prefer_mode = flag
        db.create('tests/input/ProstateX-duplicates', max_workers=1)

        with sqlite3.connect(db_path) as conn:
            count = conn.execute('SELECT COUNT(*) FROM DATA;').fetchone()[0]
            assert count > 0, f'{db_path} contains no data ({count} > 0)'
            assert count == expected, f'{db_path} contains an unexpected amount of data ({count} != {expected})'



@pytest.mark.skipif(not os.path.exists('tests/input/temp') or len(os.listdir('tests/input/temp')) == 0,
                    reason='gitignored tests/input/temp directory is empty')
def test_input_temp():
    prepare(db_path := Path('tests/output/test_temp.db'))

    db = Database(db_path)
    db.verify_dcm_filenames = False
    additional_dicom_tags = {
        '(0018,0031)': 'radiopharmaceutical',
        '(0018,1072)': 'radiopharmaceutical_start_time',
        '(0018,1074)': 'radionuclide_total_dose',
        '(0018,1075)': 'radionuclide_half_life',
        '(0018,1076)': 'radionuclide_positron_fraction',
    }

    def header_func(reader: DICOMImageReader):
        for key in additional_dicom_tags.values():
            assert reader.metadata[key] is not None
            assert reader.metadata[key] != ""

        return {"lol": 1}

    db.create(
        "tests/input/temp",
        max_workers=1,
        max_rows=1000,
        additional_dicom_tags=list(additional_dicom_tags.keys()),
        custom_header_func=header_func,
        reader_prefer_mode=dicomselect.ReaderPreferMode.PreferPydicomImage
        | dicomselect.ReaderPreferMode.PreferPydicomMetadata,
    )
