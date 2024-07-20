import hashlib
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

import numpy as np
import pydicom
import pydicom.errors
import pydicom.multival
import pydicom.tag
import SimpleITK as sitk

from dicomselect.dicom import DEFAULT_DICOM_TAGS, DICOMTag, InvalidTagError

PathLike = Union[Path, str]


class UnreadableDICOMError(BaseException):
    """
    Exception raised when a DICOM series could not be loaded.
    """

    def __init__(self, path: PathLike):
        super().__init__(f'Could not read {path} using either SimpleITK or pydicom')


class MissingDICOMFilesError(BaseException):
    """
    Exception raised when a DICOM series has missing DICOM slices.
    """

    def __init__(self, path: PathLike):
        super().__init__(f"Missing DICOM slices detected in {path}")


def get_orientation(image_direction: Iterable[float]):
    """sphinx-skip
    Deduce image orientation from DICOM Image Orientation (Patient) Attribute.
    Based on https://gist.github.com/agirault/60a72bdaea4a2126ecd08912137fe641
    and https://stackoverflow.com/questions/70645577/translate-image-orientation-into-axial-sagittal-or-coronal-plane
    and https://stackoverflow.com/questions/69799946/simpleitk-getdirection-explained
    """
    if len(image_direction) != 9:
        return "unknown"

    Ax, Bx, Cx, Ay, By, Cy, Az, Bz, Cz = image_direction
    C = (Cx, Cy, Cz)

    abs_image_z = np.abs(C)
    main_index = list(abs_image_z).index(max(abs_image_z))
    if main_index == 0:
        main_direction = "sagittal"
    elif main_index == 1:
        main_direction = "coronal"
    else:
        main_direction = "transverse"
    return main_direction


def get_pydicom_value(ds: pydicom.dataset.Dataset, key: Union[pydicom.tag.BaseTag, str]) -> str:
    if isinstance(key, str):
        key = '0x' + key.replace('|', '')
    if key in ds:
        result = ds[key]
        if result.is_empty:
            return ''
        result = result.value
        if isinstance(result, (list, pydicom.multival.MultiValue)):
            result = "\\".join([str(v) for v in result])
        return str(result)
    return ''


def get_orientation_matrix(ds: pydicom.FileDataset) -> np.ndarray:
    x, y = np.array(list(map(float, ds.ImageOrientationPatient))).reshape(2, 3)
    return np.stack([x, y, np.cross(x, y)])


def filter_localizer_slices(dicom_slice_paths: List[str]) -> List[str]:
    """sphinx-skip
    Filter out localizer slices (slices with ImageType == LOCALIZER).
    WARNING: this is slow and a heuristic that may not work for all datasets.
    """
    filtered_dicom_slice_paths = []
    for path in dicom_slice_paths:
        reader = sitk.ImageFileReader()
        reader.SetFileName(str(path))
        reader.LoadPrivateTagsOn()
        reader.ReadImageInformation()
        image_type = reader.GetMetaData("0008|0008")
        if "LOCALIZER" not in image_type.upper():
            filtered_dicom_slice_paths.append(path)
    return filtered_dicom_slice_paths


class DICOMImageReader:
    """
    Reads a folder containing DICOM slices (possibly enclosed in a zip file).
    Will only read items which end with .dcm.

    Args:
        path:
            Path to the folder containing the DICOM slices. The folder should contain the DICOM slices,
            or a zip file named "dicom.zip" containing the DICOM slices.
        verify_dicom_filenames:
            Verify DICOM filenames have increasing numbers, with no gaps.
            Common prefixes are removed from the filenames before checking the numbers,
            this allows to verify filenames like "1.2.86.1.dcm", ..., "1.2.86.12.dcm".
        allow_raw_tags:
            Allow loading of any tags contained in the DICOM, irrelevant of whether they are valid
        additional_tags:
            Load more strings than is defined in dicomselect.constants.
            A full list of all DICOM tags is available in dicomselect.tags_generated

    Examples:
        >>> reader = DICOMImageReader('path/to/dicom/folder')
        >>> image = reader.image
        >>> metadata = reader.metadata
    """

    def __init__(self, path: PathLike, prefer_mode: int = None, verify_dicom_filenames: bool = False, allow_raw_tags: bool = True, additional_tags: list[str] = None):
        self._dcm_tags_str = additional_tags if additional_tags else []
        self._dcm_tags: List[DICOMTag] = []
        self._prefer_mode = prefer_mode if prefer_mode else self.PreferMode.PreferITKImage | self.PreferMode.PreferITKMetadata

        self._path: Path = Path(path)
        self._allow_raw_tags = allow_raw_tags
        self._verify_dicom_filenames = verify_dicom_filenames
        self._is_zip = self._path.suffix == '.zip'

        self._image = None
        self._metadata = {}
        self._dicom_slice_paths: Optional[List[str]] = None
        self.__series_reader = None
        self._initialized = False
        self._enter_exit = None

    class PreferMode:
        """
        See :func:`DICOMImageReader.prefer_mode`.
        """
        PreferITKMetadata = 1
        PreferPydicomMetadata = 2
        PreferITKImage = 4
        PreferPydicomImage = 8

    def __len__(self) -> int:
        if self._initialized:
            return len(self._dicom_slice_paths)
        else:
            return -1

    def __repr__(self) -> str:
        return f'DICOMImageReader({self._path})'

    def __enter__(self) -> list[Path]:
        self._initialize()
        self._enter_exit = None
        if self._is_zip:
            zf = zipfile.ZipFile(self._path)
            td = tempfile.mkdtemp()
            zf.extractall(td)
            self._enter_exit = (zf, td)
            return list(Path(td).iterdir())
        return [Path(p) for p in self.dicom_slice_paths]

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._is_zip:
            zf, td = self._enter_exit
            zf.close()
            shutil.rmtree(td)

    @property
    def _series_reader(self) -> sitk.ImageSeriesReader:
        if not self.__series_reader:
            self.__series_reader = sitk.ImageSeriesReader()
        return self.__series_reader

    @property
    def dicom_slice_paths(self) -> list[str]:
        """
        Usually, a DICOM image is built from a multiple of smaller .dcm files. This returns a list of those .dcm files.
        """
        self._initialize()
        return self._dicom_slice_paths

    @property
    def is_zipfile(self) -> bool:
        return self._is_zip

    @property
    def path(self) -> Path:
        return self._path

    @property
    def prefer_mode(self) -> int:
        """
        By default, DICOM metadata and image data is read using SimpleITK.
        Set preference for which one to use during database creation using :class:`PreferMode`.
        """
        return self._prefer_mode

    @prefer_mode.setter
    def prefer_mode(self, value: int):
        self._prefer_mode = value

    @property
    def image(self) -> sitk.Image:
        """
        This is a slow operation. More information on :class:`sitk.Image` can be found in the
        `documentation <https://simpleitk.readthedocs.io/en/master/fundamentalConcepts.html#images>`_.
        Returns:
            A SimpleITK image
        """
        self._initialize()
        if self._image is None:
            path = Path(self._path)
            if self.is_zipfile:
                with zipfile.ZipFile(path) as zf:
                    if not zf.namelist():
                        raise RuntimeError('zip file is empty')
                    with tempfile.TemporaryDirectory() as tempdir:
                        zf.extractall(tempdir)
                        self._image = self._read_image(path=tempdir)
            else:
                self._image = self._read_image(path=path)
        return self._image

    @property
    def metadata(self) -> Dict[str, str]:
        """
        Native DICOM metadata.

        Returns:
            A dictionary of `str -> str`, where keys and values are native DICOM headers and their values.
        """
        self._initialize()
        return self._get_metadata()

    def clear(self):
        self._image = None
        self._metadata = {}
        self._initialized = False
        self._dcm_tags = []

    def column_info(self):
        columns = {tag.name: tag.column_type for tag in self._dcm_tags} | {'series_length': 'INTEGER'}
        for key in self.metadata.keys():
            if key not in columns:
                columns[key] = "TEXT"
        return columns

    def _initialize(self):
        if not self._initialized:
            self._dcm_tags = DEFAULT_DICOM_TAGS + [DICOMTag(tag) for tag in self._dcm_tags_str]
            if self.is_zipfile:
                with zipfile.ZipFile(self._path, 'r') as zf:
                    self._dicom_slice_paths = [
                        self._path / name
                        for name in zf.namelist()
                        if name.endswith(".dcm")
                    ]
                if self._verify_dicom_filenames:
                    self._verify_dicom_filenames_func()
            else:
                self._set_dicom_list()
        self._initialized = True

    def _verify_dicom_filenames_func(self, filenames: Optional[List[PathLike]] = None) -> bool:
        """sphinx-skip
        Verify DICOM filenames have increasing numbers, with no gaps

        Common prefixes are removed from the filenames before checking the numbers,
        this allows to verify filenames like "1.2.86.1.dcm", ..., "1.2.86.12.dcm".
        """
        if filenames is None:
            filenames = [os.path.basename(dcm) for dcm in self._dicom_slice_paths]

        # remove common prefixes
        common_prefix = os.path.commonprefix(filenames)
        if common_prefix:
            filenames = [fn.replace(common_prefix, "") for fn in filenames]
        common_postfix = os.path.commonprefix([fn[::-1] for fn in filenames])[::-1]
        if common_postfix:
            filenames = [fn.replace(common_postfix, "") for fn in filenames]

        # extract numbers from filenames
        filename_digits = [(''.join(c for c in str(fn) if c.isdigit())) for fn in filenames]
        filename_digits = [int(d) for d in filename_digits if d]
        if len(filename_digits) < 2:
            # either no numbers in the filenames, or only one file
            return True

        missing_slices = False
        for num in range(min(filename_digits), max(filename_digits) + 1):
            if num not in filename_digits:
                missing_slices = True
                break
        if missing_slices:
            raise MissingDICOMFilesError(self._path)
        return True

    def _set_dicom_list(self, path: Optional[PathLike] = None) -> None:
        """
        Set the list of paths to the DICOM slices.

        Parameters
        ----------
        path: PathLike
            path to the folder containing the DICOM slices. The folder should contain the DICOM slices,
            or a zip file containing the DICOM slices.
            default: self.path
        """
        if path is None:
            path = self._path

        self._dicom_slice_paths = self._series_reader.GetGDCMSeriesFileNames(str(path))

        # verify DICOM files are found
        if len(self._dicom_slice_paths) == 0:
            raise MissingDICOMFilesError(self._path)

        if self._verify_dicom_filenames:
            self._verify_dicom_filenames_func()

    def _read_image(self, index: int = 0, path: Optional[PathLike] = None) -> sitk.Image:
        if path is None:
            path = self._path
        pref_pydicom = self.prefer_mode & self.PreferMode.PreferPydicomImage
        kwargs = {'index': index, 'path': path}

        primary_reader = self._read_image_pydicom if pref_pydicom else self._read_image_sitk
        fallback_reader = self._read_image_sitk if pref_pydicom else self._read_image_pydicom

        try:
            return primary_reader(**kwargs)
        except RuntimeError:
            return fallback_reader(**kwargs)

    def _read_image_sitk(self, index: int = 0, path: Optional[PathLike] = None) -> sitk.Image:
        """
        Read image using SimpleITK.

        Args:
            path
                path to the folder containing the DICOM slices. The folder should contain the DICOM slices,
                or a zip file containing the DICOM slices. (default = self.path)

        Returns:
            image
        """
        if path is not None:
            self._path = path
            self._set_dicom_list(path=path)

        # read DICOM sequence
        try:
            self._series_reader.SetFileNames(self._dicom_slice_paths)
            image: sitk.Image = self._series_reader.Execute()
        except RuntimeError:
            # try again while removing localizer slices
            self._dicom_slice_paths = filter_localizer_slices(self._dicom_slice_paths)
            self._series_reader.SetFileNames(self._dicom_slice_paths)
            image: sitk.Image = self._series_reader.Execute()

        # read metadata from the last DICOM slice
        reader = sitk.ImageFileReader()
        reader.SetFileName(self._dicom_slice_paths[index])
        reader.LoadPrivateTagsOn()
        reader.ReadImageInformation()

        # set metadata
        metadata = {key: reader.GetMetaData(key).strip() for key in reader.GetMetaDataKeys()}
        for key, value in metadata.items():
            if len(value) > 0:
                value = value.encode("utf-8", "ignore").decode("utf-8")
                image.SetMetaData(key, value)

        return image

    def _read_image_pydicom(self, index: int = 0, path: Optional[PathLike] = None) -> sitk.Image:
        """
        Read image using pydicom. Warning: experimental! This function has limited capabilities.

        Parameters
        ----------
        path: PathLike
            path to the folder containing the DICOM slices. The folder should contain the DICOM slices,
            or a zip file containing the DICOM slices.
            default: self.path

        Returns
        -------
        image: SimpleITK.Image
        """
        if path is not None:
            self._path = path
            self._set_dicom_list(path=path)

        files = [pydicom.dcmread(dcm) for dcm in self._dicom_slice_paths]

        # skip files with no SliceLocation (eg. scout views)
        slices = filter(lambda a: hasattr(a, 'SliceLocation'), files)
        slices = sorted(slices, key=lambda s: s.SliceLocation)

        # create and fill 3D array
        image = np.zeros([len(slices)] + list(slices[0].pixel_array.shape))
        for index, s in enumerate(slices):
            image[index, :, :] = s.pixel_array

        # convert to SimpleITK
        image: sitk.Image = sitk.GetImageFromArray(image)
        ref = slices[index]  # corresponds to the same slice as with SimpleITK
        image.SetSpacing(list(ref.PixelSpacing) + [ref.SliceThickness])
        image.SetOrigin(ref.ImagePositionPatient)
        image.SetDirection(tuple(get_orientation_matrix(ref).transpose().flatten()))

        for key in ref.keys():
            # collect all available metadata (with DICOM tags, e.g. 0010|1010, as keys)
            value = get_pydicom_value(ref, key)
            if value is not None:
                value = value.encode("utf-8", "ignore").decode("utf-8")
                key = str(key).replace(", ", "|").replace("(", "").replace(")", "")
                image.SetMetaData(key, value)

        return image

    def _get_metadata(self, index: int = 0) -> Dict[str, str]:
        if index < 0 or index >= len(self):
            raise IndexError(f"{str(self)}: Index {index} out of range")
        if index in self._metadata:
            return self._metadata[index]

        # Read metadata from DICOM file
        metadata = self._read_metadata(index)

        uid_str = '_'.join([str(metadata[tag.name]) for tag in DEFAULT_DICOM_TAGS])
        metadata['dicomselect_uid'] = hashlib.blake2b(uid_str.encode(), digest_size=32).hexdigest()
        metadata["series_length"] = str(len(self))

        self._metadata[index] = metadata
        return metadata

    def _read_metadata(self, index: int = 0) -> Dict[str, str]:
        pref_pydicom = (self.prefer_mode & self.PreferMode.PreferPydicomMetadata) == self.PreferMode.PreferPydicomMetadata
        if self._image is not None and index == 0:
            # TODO: does not respect preference
            return self._collect_metadata_sitk(self._image)

        if self.is_zipfile:
            # read metadata from dicom.zip with pydicom
            with zipfile.ZipFile(self._path) as zf:
                if not zf.namelist():
                    raise RuntimeError('zip file is empty')

                with tempfile.TemporaryDirectory() as tempdir:
                    targetpath = zf.extract(member=zf.namelist()[-1-index], path=tempdir)
                    return self._read_metadata_from_file(targetpath, pref_pydicom)

        # extract metadata from specified DICOM slice
        dicom_slice_path = self._dicom_slice_paths[index]
        return self._read_metadata_from_file(dicom_slice_path, pref_pydicom)

    def _read_metadata_from_file(self, path: PathLike, pref_pydicom: bool) -> Dict[str, str]:
        def collect_pydicom():
            with pydicom.dcmread(path, stop_before_pixels=True) as ds:
                return self._collect_metadata_pydicom(ds)

        def collect_sitk():
            reader = sitk.ImageFileReader()
            reader.SetFileName(str(path))
            reader.LoadPrivateTagsOn()
            reader.ReadImageInformation()
            return self._collect_metadata_sitk(reader)

        primary = collect_pydicom if pref_pydicom else collect_sitk
        fallback = collect_sitk if pref_pydicom else collect_pydicom

        try:
            try:
                return primary()
            except:
                return fallback()
        except:
            raise UnreadableDICOMError(path)

    def _collect_metadata_sitk(self, ref: Union[sitk.Image, sitk.ImageFileReader]) -> Dict[str, str]:
        metadata = {}
        for tag in self._dcm_tags:
            # collect metadata with DICOM names, e.g. patientsage, as keys)
            metadata[tag.name] = tag.convert(ref.GetMetaData(tag.key.lower()).strip() if ref.HasMetaDataKey(tag.key) else '')
        if self._allow_raw_tags:
            for key in ref.GetMetaDataKeys():
                # collect all available metadata (with DICOM tags, e.g. 0010|1010, as keys)
                try:
                    tag = DICOMTag(key)
                    if tag not in self._dcm_tags:
                        metadata[tag.name] = tag.convert(ref.GetMetaData(tag.key).strip())
                except InvalidTagError:
                    continue

        for tag, func in [
            ('image_spacing_in_plane', lambda: str(ref.GetSpacing()[0:2])),
            ('image_direction', lambda: get_orientation(ref.GetDirection())),
            ('image_origin', lambda: str(ref.GetOrigin())),
        ]:
            try:
                metadata[tag] = func()
            except BaseException as e:
                metadata[tag] = str(e.__class__)

        return metadata

    def _collect_metadata_pydicom(self, ds: "pydicom.dataset.Dataset") -> Dict[str, str]:
        metadata = {}

        fds = pydicom.Dataset()
        stack = [ds]
        while stack:
            sds = stack.pop()
            for elem in sds:
                if elem.VR == 'SQ':
                    fds.add_new(elem.tag, elem.VR, '')
                    stack.extend(elem.value)
                else:
                    fds.add_new(elem.tag, elem.VR, elem.value)
        ds = fds

        for tag in self._dcm_tags:
            # collect metadata with DICOM names, e.g. patients_age, as keys)
            value = get_pydicom_value(ds, tag.key)
            metadata[tag.name] = tag.convert(value if value is not None else '')
        if self._allow_raw_tags:
            for key in ds.keys():
                # collect all available metadata (with DICOM tags, e.g. 0010|1010, as keys)
                try:
                    tag = DICOMTag('|'.join([str(x).zfill(4) for x in [key.group, key.elem]]))
                    if tag not in self._dcm_tags:
                        value = get_pydicom_value(ds, tag.key)
                        if value is not None:
                            metadata[tag.name] = tag.convert(value)
                except InvalidTagError:
                    continue

        for tag, func in [
            ('spacing_in_plane', lambda: str(ds.PixelSpacing[0:2])),
            ('image_direction', lambda: get_orientation([]))
        ]:
            try:
                metadata[tag] = func()
            except BaseException as e:
                metadata[tag] = str(e.__class__)

        return metadata
    