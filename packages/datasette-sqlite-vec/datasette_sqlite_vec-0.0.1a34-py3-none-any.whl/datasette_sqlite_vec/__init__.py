
from datasette import hookimpl
import datasette_sqlite_vec

__version__ = "0.0.1a34"
__version_info__ = tuple(__version__.split("."))

@hookimpl
def prepare_connection(conn):
  conn.enable_load_extension(True)
  datasette_sqlite_vec.load(conn)
  conn.enable_load_extension(False)
