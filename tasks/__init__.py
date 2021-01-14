from invoke import Collection

from tasks import top
from .start import start_collection

ns = Collection.from_module(top)

ns.add_collection(start_collection)
