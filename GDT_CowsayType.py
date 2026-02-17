from pathlib import Path

from gdo.core.GDT_Enum import GDT_Enum
from gdo.fun.module_fun import module_fun


class GDT_CowsayType(GDT_Enum):

    def gdo_ambiguous_show_keys(self) -> bool:
        return True

    def gdo_choices(self) -> dict:
        base = Path(module_fun.instance().file_path('cowsay-files/cows/'))
        return dict(sorted({f.stem: str(f) for f in base.iterdir() if f.is_file() and f.suffix == '.cow'}.items()))
