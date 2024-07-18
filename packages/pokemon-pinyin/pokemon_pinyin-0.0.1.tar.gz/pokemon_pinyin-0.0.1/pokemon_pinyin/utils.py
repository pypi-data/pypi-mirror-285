import importlib.resources
import time
from pathlib import Path

from platformdirs import user_cache_dir

PACKAGE_NAME = "pokemon_pinyin"


def get_seacher_path():
    return importlib.resources.files(PACKAGE_NAME) / "data/searcher.json"


def get_ttf_path():
    return importlib.resources.files(PACKAGE_NAME) / "data/chinese.simhei.ttf"


class CacheDir:
    def __init__(self):
        self.base = Path(user_cache_dir()).joinpath("pokemon_pinyin")
        if not self.base.exists():
            self.base.mkdir(parents=True)

    @property
    def pokemon_dir(self) -> Path:
        path = self.base.joinpath("pokemons")
        if not path.exists():
            path.mkdir(parents=True)
        return path

    @property
    def pokemon_img_dir(self) -> Path:
        path = self.base.joinpath("pokemon_imgs")
        if not path.exists():
            path.mkdir(parents=True)
        return path

    def clear(self):
        import shutil

        print(f"!!! 10秒后将清理缓存目录:{self.base}")
        time.sleep(10)
        shutil.rmtree(self.base)


CACHE_DIR = CacheDir()
