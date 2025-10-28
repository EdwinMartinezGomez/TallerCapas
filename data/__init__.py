from .RepositoryStudents import RepositoryStudents
from .RepositoryCourses import RepositoryCourses
from .RepositoryEnRoll import RepositoryEnroll
from .RepositoryUsers import RepositoryUsers

# Some parts of the codebase import `RepositoryEnRoll` (capital R and E) as if it were
# the class; provide a backward-compatible alias so `from data import RepositoryEnRoll`
# yields a callable class rather than a module object.
RepositoryEnRoll = RepositoryEnroll

__all__ = ["RepositoryStudents", "RepositoryCourses", "RepositoryEnroll", "RepositoryEnRoll"]
