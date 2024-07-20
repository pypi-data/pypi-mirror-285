import binascii
import os
import re
import time
import shutil
import sqlite3
import traceback
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime
from itertools import islice
from os import PathLike
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional, Union

import pandas as pd
from tqdm import tqdm

from dicomselect.__version__ import __version__
from dicomselect.convert import Convert, Plan
from dicomselect.logger import Logger, progress_duration
from dicomselect.query import Query
from dicomselect.queryfactory import QueryFactory
from dicomselect.reader import DICOMImageReader

CustomHeaderFunction = Callable[[DICOMImageReader], Dict[str, Union[str, int, float]]]
CustomSkipFunction = Callable[[Path], bool]


class Database(Logger):
    """
    A class for creating and interacting with a database of DICOM data header information.

    This class allows for the creation of a database file (.db) which stores DICOM data header information.
    It supports querying the database to filter and retrieve specific data rows, and can convert the results of
    queries into more accessible file formats like mha or nii.gz.

    The database supports context management (`with` statement) for querying, as well as explicit open and close
    methods for database connections. Query objects returned can be manipulated similar to sets to filter down rows in the
    database. These can be used to specify the parameters for a data conversion.

    Args:
        db_path: The file system path where the database file (.db) will be created or accessed.
    """
    def __init__(self, db_path: PathLike):
        super().__init__()

        self._db_path = Path(db_path).absolute()
        if self._db_path.is_dir() or self._db_path.suffix != '.db':
            raise IsADirectoryError('Provide a file path with as extension, .db')
        self._conn: sqlite3.Connection = None
        self._query_factory: QueryFactory = None
        self._db_dir: Path = None
        self._is_warned_outdated_db = False

        self._prefer_mode: int = Database.PreferMode.PreferZipFile
        self._verify_dcm_filenames = False

        self._stop_scan = False
        self._headers: List[str] = None
        self._custom_header_func: CustomHeaderFunction = None
        self._custom_headers: Dict[str, type] = None
        self._additional_dicom_tags: List[str] = None

    class PreferMode:
        """
        See :func:`Database.prefer_mode`.
        """
        PreferZipFile = 1
        PreferDcmFile = 2

    @property
    def path(self) -> Path:
        return self._db_path

    @property
    def data_dir(self) -> Path:
        """
        Path to the dataset directory this database is linked to.
        
        Raises:
            sqlite3.DataError, if no database exists or is corrupt.
        """
        if not self._db_dir:
            try:
                with self:
                    self._db_dir = Path(self._conn.execute('SELECT datadir FROM meta').fetchone()[0])
            except Exception:
                raise sqlite3.DataError(f'No source directory found! Did you create a database at {self.path}?')
        return self._db_dir

    @property
    def version(self) -> str:
        """
        dicomselect version this database is created with.
        """
        if self.path.exists():
            cursor = sqlite3.connect(self.path, timeout=10)
            return cursor.execute('SELECT version FROM meta').fetchone()[0]
        return __version__

    @property
    def prefer_mode(self) -> int:
        """
        Sometimes, a directory may contain both .dcm files and a .zip file containing the same dicom files.
        Set preference for which one to use during database creation using :class:`PreferMode`.
        """
        return self._prefer_mode

    @prefer_mode.setter
    def prefer_mode(self, value: int):
        self._prefer_mode = value
        assert self._prefer_mode > 0, ValueError('Must have a filetype preference')

    @property
    def verify_dcm_filenames(self) -> bool:
        """
        Verify whether .dcm files in a directory are named logically (e.g. 01.dcm, 02.dcm, ..., 11.dcm with none missing)
        Default is False.
        """
        return self._verify_dcm_filenames

    @verify_dcm_filenames.setter
    def verify_dcm_filenames(self, value: bool):
        self._verify_dcm_filenames = value

    def __enter__(self) -> Query:
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self) -> Query:
        with open(self.path, "rb") as f:
            file_header = binascii.hexlify(f.read(16)).decode("utf-8")

        # official sqlite3 file header
        if not file_header.startswith("53514c69746520666f726d6174203300"):
            raise sqlite3.DatabaseError(f'{self.path} does not appear to be a valid database (incorrect header)')

        db_version = __version__.split('.')
        this_db_version = self.version.split('.')
        if db_version[0] != this_db_version[0]:
            raise RuntimeError(f'Error: this database ({this_db_version}) is outdated by a major revision {db_version}')
        if db_version[1] > this_db_version[1] and not self._is_warned_outdated_db:
            print(f'Warning: this database ({this_db_version}) is outdated by a minor revision {db_version}')
            self._is_warned_outdated_db = True

        self._conn = sqlite3.connect(self.path)
        self._query_factory = QueryFactory(self._conn)

        return self._query_factory.create_query(None)

    def close(self):
        self._conn.close()

    def plan(self, filepath_template: str, *queries: Query) -> Plan:
        """
        Prepare a conversion plan, which can convert the results of queries to MHA files.
        You can use {dicomselect_uid} in the filepath_template to guarantee a unique string of

        Args:
            filepath_template:
                Dictates the form of the directory and filename structure, omitting the suffix.
                Use braces along with column names to replace with that column value.
                Use forward slash to create a directory structure.
                (see Query.columns for a full list of available columns).

                Illegal characters will be replaced with '#'.
                Blank column values will be replaced with '(column_name)=blank'
            queries:
                The combined results of the query object will be converted to MHA.

        Examples:
            >>> plan = db.plan('{patient_id}/prostateX_{series_description}_{instance_creation_time}.mha', query_0000)
            >>> plan.target_dir = 'tests/output/example'
            >>> plan.extension = '.mha'  # this is automatic if you provide a suffix to filepath_template as in this example
            >>> plan.execute()
        """
        with self as query:
            cols = query.columns
            requested_cols = [r.group(1) for r in re.finditer(r'{(.+?)}', filepath_template)]
            QueryFactory.check_if_exists('column', cols, *requested_cols)

            ids = set()
            for q in queries:
                ids = ids.union(q._ids)
            self._conn.execute('CREATE TEMPORARY TABLE convert_ids (id INTEGER)')
            self._conn.executemany('INSERT INTO convert_ids (id) VALUES (?)', [(i,) for i in ids])
            converts_fetched = self._conn.execute(
                f'SELECT dicomselect_uid, path, {", ".join(requested_cols)} FROM data JOIN convert_ids ON data.id = convert_ids.id').fetchall()
            converts = [Convert(fetched[0], fetched[1], filepath_template, requested_cols, fetched[2:]) for fetched in
                        converts_fetched]

        if len(converts) == 0:
            raise ValueError('query contains no items!')

        plan = Plan(self.data_dir, converts)

        filepath_template_as_path = Path(filepath_template)
        if filepath_template_as_path.suffix:
            plan.extension = filepath_template_as_path.suffix

        return plan

    def create(self, data_dir: PathLike, update: bool = False, batch_size: int = 10,
               max_workers: int = 4, max_rows: int = -1, max_init: int = 5,
               reader_prefer_mode: Optional[int] = None,
               custom_header_func: Optional[CustomHeaderFunction] = None,
               skip_func: Optional[CustomSkipFunction] = None,
               additional_dicom_tags: list[str] = None):
        """
        Build a database from DICOMs in data_dir.

        Parameters
        ----------
        data_dir: PathLike
            Directory containing .dcm data or dicom.zip data.
        update: bool
            If the db exists and is complete, will force the database to rescan the data_dir for any new data.
        batch_size: int
            Number of DICOMImageReader to process per worker.
        max_workers
            Max number of workers for parallel execution of database creation.
        max_rows
            Max rows sets the maximum number of rows in the database. Useful when doing a test run. -1 to disable.
        max_init
            Max number of items to scout, in order to define the columns for the database. Minimum 1.
        reader_prefer_mode
            By default, DICOM metadata and image data is read using SimpleITK.
            Set preference for which one to use during database creation, see DICOMImageReader.PreferMode.
        custom_header_func
            Create custom headers by returning a dict of [str, str | int | float] using DICOMImageReader.
            Note that using DICOMImageReader.image is a heavy operation and will significantly slow down database
            creation speed
        skip_func
            Filter out certain directories. This function performs an os.walk, directories are skipped for which True is
            returned in this function.
        additional_dicom_tags
            See https://www.dicomlibrary.com/dicom/dicom-tags/, input any additional tags that are not included by default
            Each tag should be formatted as shown in the DICOM tag library, eg. '(0002,0000)'.
            Non-existent tags will result in errors.

        Examples:
            >>> def custom_skip_func(path: Path):
            >>>     return '/incomplete_dicoms/' in path.as_posix()
            >>>
            >>> def custom_header_func(reader: DICOMImageReader):
            >>>     return {'custom_header': 'text', 'custom_header_int': 23}
        """
        data_dir = Path(data_dir).absolute()
        db_path = self.path.with_suffix('.db')
        db_pending_path = db_path.with_suffix('.pending.db')
        db_progress_path = db_path.with_suffix('.progress')
        db_action = {'n': 'create', 'ing': 'creating'}

        self.init_logger(self.path.with_suffix('.log'))
        self._headers = None
        self._custom_header_func = custom_header_func
        self._additional_dicom_tags = additional_dicom_tags

        if db_path.exists():
            with sqlite3.connect(db_path) as cursor:
                try:
                    cursor.execute("SELECT version FROM meta;")
                except sqlite3.OperationalError:
                    # database is corrupt and we need to start anew
                    self.print('Database has no meta table and is assumed to be corrupt.')
                else:
                    if not update:
                        self.print('Database exists, and parameter update=False.')
                        return  # db exists and we do not wish to update
                    shutil.copy(db_path, db_pending_path)
                    db_action = {'n': 'update', 'ing': 'updating'}
        elif db_pending_path.exists():
            db_action = {'n': 'resume', 'ing': 'resuming'}

        self.print(f"{db_action['ing'].capitalize()} DICOM database at {db_path} from {data_dir}.")

        try:
            existing_paths = set()
            if db_pending_path.exists():
                with sqlite3.connect(db_pending_path) as cursor:
                    existing_paths = {row[0] for row in cursor.execute('SELECT path FROM data').fetchall()}

            readers_to_submit = []
            readers_added, readers_scanned = 0, 0
            reader_kwargs = {'verify_dicom_filenames': self.verify_dcm_filenames,
                             'additional_tags': self._additional_dicom_tags,
                             'prefer_mode': reader_prefer_mode}
            reader_futures: dict[Future, list[DICOMImageReader]] = {}
            reader_batch_size = max(0, batch_size)
            reader_max_init = max(1, max_init)

            def submit_readers_as_future(*readers: DICOMImageReader) -> dict[Future, list[DICOMImageReader]]:
                if not self._headers:
                    progress.set_description_str('(initializing)')
                    self._create_or_assert_db(db_pending_path, reader_max_init, *readers)
                    progress.set_description_str()
                return {executor.submit(self._thread_execute, db_pending_path, data_dir, readers): readers}

            def process_future(future: Future):
                nonlocal readers_added
                added = 0
                try:
                    added = future.result()
                except Exception as e:
                    self.log(e, name='result', DICOMImageReaders=reader_futures[future])
                readers_added += added

                if progress.total is None:
                    progress.set_postfix_str(f'{readers_added} added, {self.errors} errors')
                else:
                    progress.update(added)
                    progress.set_postfix_str(f'{self.errors} errors')

            def update_progress():
                try:
                    with open(db_progress_path, 'w') as f:
                        f.write(str(progress))
                except:
                    pass
                progress.refresh()

            try:
                with ThreadPoolExecutor(max_workers=max_workers) as executor, \
                        tqdm(unit=' scanned', postfix=f'{self.errors} errors') as progress:

                    for root, dirs, filenames in os.walk(data_dir,
                                                         onerror=lambda err: self.log(traceback.format_exception(err))):
                        root = Path(root)
                        if skip_func and skip_func(root):
                            continue

                        scanner_empty = object()
                        scanner = self._scan_for_readers(root, *filenames, **reader_kwargs)
                        while (reader := next(scanner, scanner_empty)) is not scanner_empty:
                            readers = list(islice(scanner, reader_batch_size - len(readers_to_submit) - 1)) + [reader]
                            for reader in readers:
                                progress.update()
                                if str(reader.path.relative_to(data_dir)) not in existing_paths:
                                    readers_to_submit.append(reader)

                            if len(readers_to_submit) >= reader_batch_size:
                                reader_futures |= submit_readers_as_future(*readers_to_submit)
                                readers_to_submit.clear()

                            reader_futures_completed = {future for future in reader_futures.keys() if future.done()}
                            for f in reader_futures_completed:
                                process_future(f)
                                reader_futures.pop(f)

                            if 0 <= max_rows <= readers_added:
                                raise InterruptedError
                            update_progress()

                    if len(readers_to_submit) > 0:
                        reader_futures |= submit_readers_as_future(*readers_to_submit)

                    readers_scanned = progress.n
                    progress.total = readers_scanned
                    progress.n = readers_added
                    progress.unit = ' added'
                    progress.set_postfix_str(f'{self.errors} errors')

                    for f in as_completed(reader_futures):
                        process_future(f)
                        update_progress()
            except InterruptedError:
                pass

            if readers_scanned == 0:
                raise sqlite3.DataError(f'No DICOM data added using {data_dir} '
                                        f'(0 processed, {self.errors} errors occurred)')

            with sqlite3.connect(db_pending_path) as cursor:
                df_meta = pd.DataFrame({'datadir': str(data_dir),
                                        'version': __version__,
                                        'latest': datetime.now().strftime("%Y%m%dT%H%M")}, index=[0])
                df_meta.to_sql(name='meta', con=cursor, if_exists='replace')
            cursor.close()  # fails to properly close sometimes

            os.remove(db_progress_path)
            shutil.copy(db_pending_path, db_path)

            self.print(f"Completed {db_action['n']} action at {self.path} in {progress_duration(progress)} "
                       f"({readers_scanned} processed, {readers_added} added, {self.errors} errors occurred).")

            a = 0
            while db_pending_path.exists() and a < 5:
                try:
                    os.remove(db_pending_path)
                except PermissionError as e:
                    if a == 0:
                        self.print(str(e), level=self.WARN)
                    time.sleep(0.5)
                    a += 1
            if db_pending_path.exists():
                self.print(f'Could not delete {db_pending_path} due to permission errors.')
        finally:
            if self.errors > 0:
                self.print(f"{self.errors} errors during database {db_action['n']}: "
                           f"See {self.log_path} for details", level=self.WARN)

    def _scan_for_readers(self, root: Path, *filenames: str, **kwargs) -> Iterator[DICOMImageReader]:
        files: Dict[str, list[str]] = {'.zip': [], '.dcm': []}
        for file in filenames:
            try:
                files[Path(file).suffix].append(file)
            except KeyError:
                pass
        files_zip, files_dcm = files['.zip'], files['.dcm']

        if len(files_dcm) > 0 and len(files_zip) <= 1:
            if len(files_zip) == 1 and self.prefer_mode & Database.PreferMode.PreferZipFile:
                yield DICOMImageReader(root / files_zip.pop(), **kwargs)
            else:
                yield DICOMImageReader(root, **kwargs)

        if len(files_zip) > 0:
            for zipfile in files_zip:
                yield DICOMImageReader(root / zipfile, **kwargs)

    def _create_or_assert_db(self, db_path: Path, max_init: int, *readers: DICOMImageReader):
        column_sets = []
        create_column_error: Exception | None = None
        for reader in readers[:max_init]:
            try:
                dicom_columns, custom_columns = [], []

                # confirm these do not break
                dicom_metadata = reader.metadata | {'path': ''}
                custom_metadata = self._custom_header_func_runner(reader, dicom_metadata)

                # populate SQL columns
                self._custom_headers = {}
                dicom_columns = [f'{name} {dtype}' for name, dtype in reader.column_info().items()]
                for key, value in custom_metadata.items():  # split custom values into SQL datatypes
                    for T, dtype in [(str, 'TEXT'), (int, 'INTEGER'), (float, 'REAL')]:
                        if isinstance(value, T):
                            self._custom_headers[key] = T  # apply contract that this key must be of type T
                            custom_columns.append(f'{key} {dtype}')  # SQL column header
                            break

                if dicom_metadata is None or len(dicom_columns) == 0:
                    raise sqlite3.DataError('No DICOM data found')

                column_sets.append(set(dicom_columns + custom_columns))
            except Exception as e:
                create_column_error = e
                continue
        if create_column_error:
            raise create_column_error

        columns_set = {column for column_set in column_sets for column in column_set}
        columns = list(sorted(columns_set))
        self._headers = {c.split(' ')[0] for c in columns} | {'path'}

        if db_path.exists():
            with sqlite3.connect(db_path) as cursor:
                columns_existing = cursor.execute("PRAGMA table_info(data)").fetchall()
                pk, path = columns_existing[0], columns_existing[1]
                assert pk[1] == 'id' and pk[2] == 'INTEGER' and pk[-1] == 1, \
                    f'{db_path} is corrupt, first column is not "id INTEGER PRIMARY KEY"'
                assert path[1] == 'path' and path[2] == 'TEXT', \
                    f'{db_path} is corrupt, second column is not "path TEXT"'
                missing_columns = columns_set.difference({f'{c[1]} {c[2]}' for c in columns_existing[2:]})
                for sql in [f'ALTER TABLE data ADD COLUMN {c}' for c in missing_columns]:
                    cursor.execute(sql)
        else:
            with sqlite3.connect(db_path) as cursor:
                sql_columns = ', '.join(columns)
                cursor.execute(f'CREATE TABLE data (id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, {sql_columns});')

    def _custom_header_func_runner(self, reader: DICOMImageReader, existing_metadata: dict):
        if self._custom_header_func:
            custom_metadata = self._custom_header_func(reader)
            for key, value in custom_metadata.items():
                assert key not in existing_metadata, KeyError(f"'{key}' already exists in metadata")
                assert isinstance(key, str), KeyError("Custom headers must be of type 'str'")

                if self._custom_headers:
                    # during database creation, we check if the header maintains expected type as per the prior example
                    expected_type = self._custom_headers[key]
                    assert isinstance(value, expected_type), ValueError(
                        f"Value in custom header '{key}' must be of type '{expected_type.__name__}'")
                else:
                    assert isinstance(value, (str, int, float)), \
                        ValueError(f"Values in custom header '{key}' must be one of types 'str', 'int', 'float'")
            return custom_metadata
        return {}

    def _thread_execute(self, db: Path, data_dir: Path, readers: List[DICOMImageReader]):
        metadata: dict | list = []
        for reader in readers:
            try:
                meta = reader.metadata.copy()
                meta["path"] = str(reader.path.relative_to(data_dir))
                meta |= self._custom_header_func_runner(reader, meta)
                reader.clear()
            except BaseException as e:
                self.log(e, name='metadata', DICOMImageReaders=reader)
                continue
            if meta:
                metadata.append({key: value for key, value in meta.items() if key in self._headers})

        df_rows = pd.DataFrame.from_dict(metadata, orient='columns')
        with sqlite3.connect(db, check_same_thread=False) as conn:
            df_rows.to_sql(name='data', con=conn, if_exists='append', index=False)

        return len(metadata)
