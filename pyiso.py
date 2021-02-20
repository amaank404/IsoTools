import pycdlib
import io
from typing import BinaryIO
import os


def get_size_file_object(fp: BinaryIO):
    old_file_position = fp.tell()
    fp.seek(0, os.SEEK_END)
    size = fp.tell()
    fp.seek(old_file_position, os.SEEK_SET)
    return size


class IsoFile:
    """
    Open a Iso File for read and write operation according to specified arguments and iso extensions
    """
    def __init__(self, name: str, iso9660=False, joliet=None, rock_ridge=None, udf="2.60"):
        self.file_name = name
        self.is_joliet = joliet is not None
        self.is_iso9960 = iso9660
        self.is_udf = bool(udf)
        self.is_rock_ridge = rock_ridge is not None
        self.iso_manager = pycdlib.PyCdlib()
        if not os.path.exists(name):
            self.file = open(name, "w+b")
            args = {}
            if self.is_joliet:
                args["joliet"] = joliet
            if self.is_udf:
                args["udf"] = udf
            if self.is_rock_ridge:
                args["rock_ridge"] = rock_ridge
            self.iso_manager.new(**args)
            self.iso_manager.write_fp(self.file)
            self.file.close()
            self.iso_manager.close()
            self.iso_manager = pycdlib.PyCdlib()
        self.iso_manager.open(self.file_name)
        self.ext_types = []
        if self.is_iso9960:
            self.ext_types.append("iso_path")
        if self.is_joliet:
            self.ext_types.append("joliet_path")
        if self.is_rock_ridge:
            self.ext_types.append("rr_name")
        if self.is_udf:
            self.ext_types.append("udf_path")

    def close(self):
        self.save()
        self.iso_manager.close()

    def _prepare_args(self, name: str):
        return {x: name for x in self.ext_types}

    def write_str(self, name: str, data: bytes):
        self.iso_manager.add_fp(io.BytesIO(data), len(data), **self._prepare_args(name))

    def write(self, name: str, fp: BinaryIO):
        self.iso_manager.add_fp(fp, get_size_file_object(fp), **self._prepare_args(name))

    def read_stream(self, name: str, t: str = "udf_path"):
        return self.iso_manager.open_file_from_iso(**{t: self._prepare_args(name)[t]})

    def read_str(self, name: str, t: str = "udf_path"):
        extraction_stream = io.BytesIO()
        self.iso_manager.get_file_from_iso_fp(extraction_stream, **{t: self._prepare_args(name)[t]})
        extraction_stream.seek(0)
        return extraction_stream.read()

    def read(self, name: str, fp: BinaryIO, t: str = "udf_path"):
        self.iso_manager.get_file_from_iso_fp(fp, **{t: self._prepare_args(name)[t]})

    def make_bootable_str(self, name: str, data: bytes, hybrid: bool = False):
        """
        Make a file inside iso to be marked as bootable
        """
        self.iso_manager.add_fp(io.BytesIO(data), iso_path=name, length=len(data))
        self.iso_manager.add_eltorito(name)
        if hybrid:
            self.iso_manager.add_isohybrid()

    def make_bootable(self, name: str, fp: BinaryIO, hybrid: bool = False):
        """
        Make a file inside iso to be marked as bootable
        """
        self.iso_manager.add_fp(fp, iso_path=name, length=get_size_file_object(fp))
        self.iso_manager.add_eltorito(name)
        if hybrid:
            self.iso_manager.add_isohybrid()

    def new_dir(self, name: str):
        self.iso_manager.add_directory(**self._prepare_args(name))

    def walk(self, name: str = '/'):
        return self.iso_manager.walk(**self._prepare_args(name))

    def remove(self, name: str):
        self.iso_manager.rm_file(**self._prepare_args(name))

    def remove_bootable(self):
        self.iso_manager.rm_isohybrid()
        self.iso_manager.rm_eltorito()

    def remove_directory(self, name: str):
        self.iso_manager.rm_directory(**self._prepare_args(name))

    def make_hardlink(self, name: str, file_name: str):
        self.iso_manager.add_hard_link(iso_old_path=file_name, iso_new_path=name)

    def remove_hardlink(self, name: str):
        self.iso_manager.rm_hard_link(name)

    def list_dir(self, name: str = "/"):
        return self.iso_manager.list_dir(name, self.is_joliet)

    def save(self, file: str = None):
        if file is None:
            file = self.file_name
        fp = open(file, "w+b")
        self.iso_manager.write_fp(fp)
        fp.close()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
