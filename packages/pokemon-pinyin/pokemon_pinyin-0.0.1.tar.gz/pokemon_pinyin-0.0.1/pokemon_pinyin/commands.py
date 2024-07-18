from typing import Literal

import click

from pokemon_pinyin.draw import PokemonIterator, draw_pdf
from pokemon_pinyin.pokemon import MAX_POKEDEX, Pokemon
from pokemon_pinyin.searcher import PokemonSearcher
from pokemon_pinyin.utils import CACHE_DIR


@click.group()
def cli(): ...


@cli.command()
@click.argument("pokedexs", type=str, nargs=1, required=False)
@click.option(
    "-o", "--output", default="output_a4.pdf", help="输出的文件名", show_default=True
)
@click.option("--ttf", default=None, help="字体文件路径")
@click.option(
    "-ft",
    "--filter_type",
    default="only",
    type=click.Choice(["only", "include"]),
    show_default=True,
)
@click.option("-fb", "--filter_by", help="过滤的拼音,逗号分隔 [example: a,b,c,ong]")
@click.option(
    "--margin", help="画布上四周的空白[px]", default=300, type=int, show_default=True
)
def run(
    *,
    pokedexs: str | None,
    output: str,
    ttf: str | None = None,
    filter_type: Literal["only", "include"],
    filter_by: str = None,
    margin: int = 300,
):
    """POKEDEXS [1,2,3或1..3] 表示从1到3号"

    examples:

        ppinyin 1,3,5

        ppinyin 1..5 --output=a.pdf

        ppinyin -ft only -fb m,a
    """
    if not pokedexs:
        if not filter_by:
            raise click.BadParameter("--filter_by为空时必须指定编号范围")
        pokedexs = range(1, MAX_POKEDEX + 1)
    elif ".." in pokedexs:
        start, end = pokedexs.strip().split("..", maxsplit=1)
        start, end = int(start), int(end)
        if start >= end or start < 1 or end > MAX_POKEDEX:
            raise click.BadParameter(f"开始和结束必须在1..{MAX_POKEDEX}以内")
        pokedexs = range(start, end + 1)
        click.echo(f"开始绘画编号为{start}..{end}的宝可梦")
    else:
        pokedexs = [int(i) for i in pokedexs.strip().split(",")]
        for i in pokedexs:
            if not 1 <= i <= MAX_POKEDEX:
                raise click.BadParameter(f"开始和结束必须在1..{MAX_POKEDEX}以内")
        click.echo(f"开始绘画编号为{pokedexs}的宝可梦")

    if filter_by:
        filter_by = filter_by.strip().split(",")
        searcher = PokemonSearcher.load_from_json()
        searcher = searcher.copy_filter_by_pokedexs(pokedexs)
        if filter_type == "only":
            pokemons = searcher.any_only(*filter_by)
        elif filter_type == "include":
            pokemons = searcher.any_include(*filter_by)
        else:
            raise click.BadOptionUsage(
                "filter_type", f"不支持的filter_type`{filter_type}`"
            )
        click.echo(f"共搜索到符合条件的宝可梦{len(pokemons)}只")
    else:
        pokemons = [Pokemon.from_pokemon_cn(i) for i in pokedexs]

    draw_pdf(PokemonIterator(pokemons), output, font_path=ttf, margin=margin)


@cli.group()
def cache(): ...


@cache.command()
def ls():
    click.echo(str(CACHE_DIR.base))


@cache.command()
def clear():
    CACHE_DIR.clear()


def main():
    cli(prog_name="pp", default_map={"cli": {"default_command": "run"}})


if __name__ == "__main__":
    main()
