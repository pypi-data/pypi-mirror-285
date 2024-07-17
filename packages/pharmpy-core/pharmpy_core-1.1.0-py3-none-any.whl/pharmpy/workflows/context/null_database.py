from ..model_database import NullModelDatabase
from .baseclass import Context


class NullContext(Context):
    """Dummy context

    No operation does anything. This context can be used if no storing of files
    is desirable.
    """

    def __init__(self, toolname, **kwargs):
        super().__init__(toolname)
        self.model_database = NullModelDatabase()

    def store_local_file(self, source_path):
        pass

    def store_results(self, res):
        pass

    def store_metadata(self, metadata):
        pass

    def read_metadata(self):
        pass
