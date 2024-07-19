from dataclasses import dataclass

from nema.data.data_properties import DataProperties, FileDataProperties


@dataclass
class FigureDataProperties(DataProperties):
    pass


@dataclass
class ImageDataProperties(FigureDataProperties, FileDataProperties):
    @property
    def data_type(self):
        return "IMAGE.V0"
