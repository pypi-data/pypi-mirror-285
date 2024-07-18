import logging
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFont import FreeTypeFont
from pypinyin import pinyin

from pokemon_pinyin.pokemon import Pokemon
from pokemon_pinyin.utils import get_ttf_path

logger = logging.getLogger(__name__)

CHAR_WIDTH_SPACE = 30  # 一个Pokemon单个汉字或者拼音之间的间隔
CHAR_HEIGHT_SPACE = 30  # 一个Pokemon单个汉字或者拼音之间的间隔
PINYIN_CHINESE_SPACE = 20  # 拼音和汉字上下间隔
CHINESE_IMAGE_SPACE = 20

PNG_SIZE = (400, 400)  # (width, height)
CHINESE_FONT_SIZE = 60
PINYIN_FONT_SIZE = 80


def convert_transparent_to_white(image_path):
    img = Image.open(image_path).convert("RGBA")
    W, L = img.size
    white_pixel = (0, 0, 0, 0)  # 设置透明
    for h in range(W):
        for i in range(L):
            if img.getpixel((h, i)) == white_pixel:
                img.putpixel((h, i), (255, 255, 255, 255))  # 白色
    return img


class PokemonBox:
    def __init__(
        self,
        pokemon: Pokemon,
        draw: ImageDraw.ImageDraw,
        pinyin_font: FreeTypeFont,
        char_font: FreeTypeFont,
    ) -> None:
        self.pokemon = pokemon
        self.pinyin_font = pinyin_font
        self.char_font = char_font
        self.image_draw = draw

        pinyin_names = pinyin(pokemon.chinese_name, v_to_u=True)

        if any(len(i) > 1 for i in pinyin_names):
            logger.warning(f"!!!发现多音字 {pokemon.chinese_name}, {pinyin_names=}")
        # 假设没有多音字
        pinyins = [i[0] for i in pinyin_names]

        self.pinyins = pinyins

    @lru_cache
    def font_width(self) -> int:
        total_width = 0
        # 计算总宽度
        for i, char in enumerate(self.pokemon.chinese_name):
            char_pinyin = self.pinyins[i]

            # 计算拼音和汉字的宽度
            pinyin_bbox = self.image_draw.textbbox(
                (0, 0), char_pinyin, font=self.pinyin_font
            )
            char_bbox = self.image_draw.textbbox((0, 0), char, font=self.char_font)

            pinyin_width = pinyin_bbox[2] - pinyin_bbox[0]
            char_width = char_bbox[2] - char_bbox[0]

            # 计算最大宽度
            char_spacing = max(pinyin_width, char_width) + CHAR_WIDTH_SPACE
            total_width += char_spacing
        return total_width

    @lru_cache
    def font_height(self) -> int:
        # 计算总宽度
        pinyin_bboxs = [
            self.image_draw.textbbox((0, 0), i, font=self.pinyin_font)
            for i in self.pinyins
        ]
        pinyin_height = max(i[3] - i[1] for i in pinyin_bboxs)

        char_bboxs = [
            self.image_draw.textbbox((0, 0), i, font=self.pinyin_font)
            for i in self.pokemon.chinese_name
        ]
        char_height = max(i[3] - i[1] for i in char_bboxs)

        total_height = pinyin_height + char_height + CHAR_HEIGHT_SPACE
        return total_height

    def box_width(self):
        return max(PNG_SIZE[0], self.font_width())

    def box_height(self):
        return self.font_height() + PNG_SIZE[1] + CHINESE_IMAGE_SPACE

    def draw(
        self,
        position: tuple[int, int],
        background: Image,
    ) -> tuple[int, int, int, int]:
        x, y = position
        font_total_width = self.font_width()
        # 待确认是否需要计算得到
        char_y = y + self.pinyin_font.size + PINYIN_CHINESE_SPACE
        # 重新设置x，使其居中
        x = x + (self.box_width() - font_total_width) // 2
        # 画拼音和汉字
        for i, char in enumerate(self.pokemon.chinese_name):
            char_pinyin = self.pinyins[i]
            # 计算拼音和汉字的宽度
            pinyin_bbox = self.image_draw.textbbox(
                (0, 0), char_pinyin, font=self.pinyin_font
            )
            char_bbox = self.image_draw.textbbox((0, 0), char, font=self.char_font)
            pinyin_width = pinyin_bbox[2] - pinyin_bbox[0]
            char_width = char_bbox[2] - char_bbox[0]
            # 计算最大宽度
            char_spacing = max(pinyin_width, char_width) + CHAR_WIDTH_SPACE
            # 计算汉字的起始x位置，使其居中
            char_x = x + (pinyin_width - char_width) / 2
            # 画拼音
            self.image_draw.text(
                (x, y), char_pinyin, font=self.pinyin_font, fill="black"
            )
            # 画汉字
            self.image_draw.text(
                (char_x, char_y), char, font=self.char_font, fill="black"
            )
            # 移动到下一个字符的位置
            x += char_spacing

        # 打开并插入固定大小的图片
        image = convert_transparent_to_white(self.pokemon.download_pokemon_img())
        image = image.resize(PNG_SIZE)
        image_x = (
            position[0] + (self.box_width() - PNG_SIZE[0]) // 2
        )  # 将图片居中放置在文字正下方
        image_y = position[1] + self.font_height() + CHINESE_IMAGE_SPACE
        image_pil = image.convert("RGBA")
        background.paste(image_pil, (image_x, image_y))

        return (
            position[0],
            position[1],
            position[0] + self.box_width(),
            position[1] + self.box_height(),
        )

    def draw_img(self, position: tuple[int, int]):
        self.pokemon.download_pokemon_img()


class PokemonIterator:
    def __init__(self, data: list[Pokemon]):
        self.data: list[Pokemon] = data

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.data) == 0:
            raise StopIteration
        return self.data.pop(0)

    def __len__(self):
        return len(self.data)


def draw_a4(
    pokemons: PokemonIterator,
    font_path: str | None = None,
    margin: int = 300,
) -> Image.Image:
    """
    Args:
        pokemons (list[Pokemon]):
        font_path (str | None, optional): 字体文件路径. Defaults to simhei.
        margin (int, optional): 边距. Defaults to 300.
    """
    font_path = font_path or get_ttf_path()  # 确保字体文件路径正确
    if not Path(font_path).exists():
        raise ValueError(f"字体文件`{font_path}`不存在，请下载或者修改路径")
    pinyin_font = ImageFont.truetype(font_path, PINYIN_FONT_SIZE)
    char_font = ImageFont.truetype(font_path, CHINESE_FONT_SIZE)
    # 设置 A4 纸的大小，单位是像素
    # A4 尺寸是 210 x 297 mm，像素 = mm * DPI (例如，300 DPI)
    dpi = 300
    a4_width_mm = 210
    a4_height_mm = 297
    a4_width_px = int(a4_width_mm * dpi / 25.4)
    a4_height_px = int(a4_height_mm * dpi / 25.4)
    # 创建白色背景的图像
    background = Image.new("RGB", (a4_width_px, a4_height_px), "white")
    draw = ImageDraw.Draw(background)

    x, y = margin, margin
    next_row_top_y = y
    while pokemon := next(pokemons, None):
        pokemon_box = PokemonBox(pokemon, draw, pinyin_font, char_font)
        # 先计算如果加了这次之后会不会超过宽度
        box_width = pokemon_box.box_width()
        rest_of_right = a4_width_px - x - margin
        if rest_of_right < box_width:
            x = margin
            rest_of_bottom = a4_height_px - next_row_top_y - margin
            if rest_of_bottom < pokemon_box.box_height():
                logger.debug("这一页纸已满")
                break
            else:
                y = next_row_top_y + 120

        (_, _, right, bottom) = pokemon_box.draw((x, y), background)
        x = right + 120
        next_row_top_y = max(bottom, next_row_top_y)

    # 保存图像
    return background


def draw_pdf(
    pokemons: PokemonIterator,
    output: str,
    font_path: str | None = None,
    margin: int = 300,
):
    images = []
    n = 1
    if len(pokemons) == 0:
        print("--- 没有可用的数据 ---")
        return

    while len(pokemons):
        logger.info(f"开始绘画第{n}页")
        img = draw_a4(pokemons, font_path, margin)
        images.append(img)
        n += 1

    # 将图像保存为一个PDF文件
    images[0].save(output, save_all=True, append_images=images[1:], format="PDF")
    print(f"--- 文件已保存到`{output}` ---")


if __name__ == "__main__":
    from pokemon_pinyin.pokemon import Pokemon

    pokemons = [Pokemon.from_pokemon_cn(i) for i in range(1, 32)]
    ttf_path = get_ttf_path()
    # draw_a4(iter(pokemons), font_path=ttf_path).save("output_a4.png")
    draw_pdf(PokemonIterator(pokemons), "output_a4.pdf", font_path=ttf_path)
