from sqlalchemy import types


class FileColumn(types.TypeDecorator):
    """
    Extends SQLAlchemy to support and mostly identify a File Column
    """

    impl = types.Text


class ImageColumn(types.TypeDecorator):
    """
    Extends SQLAlchemy to support and mostly identify an Image Column

    """

    impl = types.Text

    def __init__(self, thumbnail_size=(20, 20, True), size=(100, 100, True), **kw):
        types.TypeDecorator.__init__(self, **kw)
        self.thumbnail_size = thumbnail_size
        self.size = size
