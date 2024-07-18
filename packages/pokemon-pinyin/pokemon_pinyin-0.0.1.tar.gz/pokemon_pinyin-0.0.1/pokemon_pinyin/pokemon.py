import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

import requests
from lxml import html

from pokemon_pinyin.utils import CACHE_DIR

BASE_URL = "https://www.pokemon.cn"
MAX_POKEDEX = 1010


def get_pokemon_name(tree: html.HtmlElement):
    lxml_path = '//*[contains(@class, "pokemon-slider__main-name")]'
    elements = tree.xpath(lxml_path)
    if len(elements) != 1:
        raise ValueError("获取名字失败")
    return elements[0].text_content().strip()


def list_pokemon_attribute(tree: html.HtmlElement):
    lxml_path = '//*[contains(@class, "pokemon-type__type")]'
    elements = tree.xpath(lxml_path)
    return [i.text_content().strip() for i in elements]


def list_pokemon_weakness(tree: html.HtmlElement):
    lxml_path = '//*[contains(@class, "pokemon-weakness__btn")]'
    elements = tree.xpath(lxml_path)
    return [i.text_content().strip() for i in elements]


def get_pokemon_img_url(tree: html.HtmlElement):
    lxml_path = '//*[contains(@class, "pokemon-img__front")]'
    elements = tree.xpath(lxml_path)
    if len(elements) != 1:
        raise ValueError("获取img失败")
    return BASE_URL + elements[0].attrib["src"].strip()


def fetch_pokemon_html_element(pokedex: int) -> html.HtmlElement:
    url = BASE_URL + f"/play/pokedex/{pokedex:04}"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise ValueError("get response error")

    html_tree = html.fromstring(response.content)
    return html_tree


@dataclass(repr=False)
class Pokemon:
    pokedex: int
    chinese_name: str
    attributes: list[str]
    weakness: list[str]
    img_url: str

    def __repr__(self) -> str:
        return f"Pokemon(pokedex={self.pokedex},name=`{self.chinese_name}`)"

    @classmethod
    def from_pokemon_cn(cls, pokedex: int, try_cache=True) -> "Pokemon":
        if try_cache and (obj := cls.try_from_cache(pokedex)):
            return obj

        html_tree = fetch_pokemon_html_element(pokedex)
        obj = cls(
            pokedex=pokedex,
            chinese_name=get_pokemon_name(html_tree),
            attributes=list_pokemon_attribute(html_tree),
            weakness=list_pokemon_weakness(html_tree),
            img_url=get_pokemon_img_url(html_tree),
        )
        obj.save_to_cache()
        return obj

    @classmethod
    def try_from_cache(cls, pokedex: int) -> Optional["Pokemon"]:
        cache_path = CACHE_DIR.pokemon_dir.joinpath(f"{pokedex}.json")
        if cache_path.exists():
            with open(cache_path, "rb") as f:
                pokemon = json.load(f)
                return cls(**pokemon)

        return None

    @property
    def pokemon_img_cache_path(self) -> Path:
        return CACHE_DIR.pokemon_img_dir.joinpath(f"{self.pokedex:04}.png")

    def save_to_cache(self):
        cache_path = CACHE_DIR.pokemon_dir.joinpath(f"{self.pokedex}.json")
        with open(cache_path, "w") as f:
            json.dump(asdict(self), f, indent=4, ensure_ascii=False)

    def download_pokemon_img(self, overwrite: bool = False) -> Path:
        pokemon_img_cache_path = self.pokemon_img_cache_path
        if pokemon_img_cache_path.exists() and not overwrite:
            return pokemon_img_cache_path.absolute().as_posix()

        response = requests.get(self.img_url, timeout=10)
        if response.status_code == 200:
            with open(pokemon_img_cache_path, "wb") as file:
                file.write(response.content)
            return pokemon_img_cache_path.absolute().as_posix()

        raise ValueError("下载图片失败，状态码：", response.status_code)


if __name__ == "__main__":
    args = sys.argv[1:]
    pokedexs = [int(i) for i in args]
    for pokedex in pokedexs:
        pokemon = Pokemon.from_pokemon_cn(pokedex)
        pokemon.download_pokemon_img()
        print(f"pokemon:{pokedex:04}, data: {pokemon}")
