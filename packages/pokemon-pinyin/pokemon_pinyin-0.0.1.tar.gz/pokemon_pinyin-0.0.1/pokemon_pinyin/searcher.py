import json
from typing import TypedDict

from pypinyin import Style, pinyin

from pokemon_pinyin.pokemon import MAX_POKEDEX, Pokemon
from pokemon_pinyin.utils import get_seacher_path

SEACHER_ITEM = TypedDict(
    "SEACHER_ITEM",
    pokedex=int,
    name=str,
    pinyins=list[tuple[str, str]],
)


def create_searcher_data(output: str = "searcher.json"):
    data: list[SEACHER_ITEM] = []
    for pokedex in range(1, MAX_POKEDEX + 1):
        if pokedex % 50 == 0:
            print(f"读取进度: {pokedex} ...")
        pokemon = Pokemon.from_pokemon_cn(pokedex)
        pinyins = get_pinyin(pokemon.chinese_name)
        data.append(
            SEACHER_ITEM(
                name=pokemon.chinese_name,
                pokedex=pokemon.pokedex,
                pinyins=pinyins,
            )
        )

    with open(output, "w") as f:
        json.dump(data, f, ensure_ascii=False)


def get_pinyin(name: str, strict=False) -> list[tuple[str, str]]:
    initials = pinyin(name, style=Style.INITIALS, strict=strict)
    initials = [i[0] for i in initials]

    finals = pinyin(name, style=Style.FINALS, strict=strict)
    finals = [i[0] for i in finals if i[0]]
    return list(zip(initials, finals))


class PokemonSearcher:
    def __init__(self, data: list[SEACHER_ITEM]) -> None:
        self._data = data

    @classmethod
    def load_from_json(cls, path: str = None):
        path = path or get_seacher_path()
        with open(path, "r") as f:
            data = json.load(f)
        return PokemonSearcher(data)

    def copy_filter_by_pokedexs(self, pokedexs: list[int]) -> "PokemonSearcher":
        pokedexs = set(pokedexs)
        data = [i for i in self._data if i["pokedex"] in pokedexs]
        return PokemonSearcher(data)

    def any_include(self, *args) -> list[Pokemon]:
        """任何一个字包含这些声韵母其中一个"""
        char_set = set(args)

        def _helper(x: SEACHER_ITEM):
            for initial, final in x["pinyins"]:
                if initial in char_set or final in char_set:
                    return True
            return False

        return [
            Pokemon.try_from_cache(i["pokedex"]) for i in filter(_helper, self._data)
        ]

    def any_only(self, *args) -> list[Pokemon]:
        """任何一个字只包含这些声韵母"""
        char_set = set(args)

        def _helper(x: SEACHER_ITEM):
            for initial, final in x["pinyins"]:
                if initial in char_set and final in char_set:
                    return True
            return False

        return [
            Pokemon.try_from_cache(i["pokedex"]) for i in filter(_helper, self._data)
        ]


if __name__ == "__main__":
    searcher = PokemonSearcher.load_from_json()
    pokemons = searcher.any_include("m", "a")
    pokemons = searcher.any_only("m", "a")
