#!/usr/bin/env python3
"""Rebuild data/kanji/ja.json from KANJIDIC2 + KRADFILE + modern JLPT lists.

Jisho.org has no kanji API (word search only). Jisho itself is a UI over
EDRDG data: KANJIDIC2 (readings, meanings, strokes, grade, frequency,
radical) and KRADFILE (component parts). This script writes that data
locally so the reader does not scrape Jisho or call a live API.

JLPT N1–N5 tags come from kanjiapi.dev (Jonathan Waller's lists). KANJIDIC's
own JLPT field is the pre-2010 1–4 scale and is only used as a fallback.

Sources (downloaded into gitignored data/raw/):
  https://www.edrdg.org/kanjidic/kanjidic2.xml.gz
  https://raw.githubusercontent.com/jmettraux/kensaku/master/data/kradfile-u
  https://kanjiapi.dev/v1/kanji/jlpt-{1-5}

KANJIDIC2 and KRADFILE are the property of the Electronic Dictionary
Research and Development Group, used in conformance with their licence:
https://www.edrdg.org/edrdg/licence.html
"""

from __future__ import annotations

import gzip
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "kanji" / "ja.json"

KANJIDIC_URL = "https://www.edrdg.org/kanjidic/kanjidic2.xml.gz"
KRADFILE_URL = (
    "https://raw.githubusercontent.com/jmettraux/kensaku/master/data/kradfile-u"
)
JLPT_URL = "https://kanjiapi.dev/v1/kanji/jlpt-{n}"
UA = "Levla/1.0 (kanji lexicon build; local graded reader)"

# Kangxi radicals 1–214, preferred CJK forms (same numbering as KANJIDIC).
KANGXI = [
    "一", "丨", "丶", "丿", "乙", "亅",
    "二", "亠", "人", "儿", "入", "八", "冂", "冖", "冫", "几", "凵", "刀", "力", "勹",
    "匕", "匚", "匸", "十", "卜", "卩", "厂", "厶", "又",
    "口", "囗", "土", "士", "夂", "夊", "夕", "大", "女", "子", "宀",
    "寸", "小", "尢", "尸", "屮", "山", "巛", "工", "己", "巾",
    "干", "幺", "广", "廴", "廾", "弋", "弓", "彐", "彡", "彳",
    "心", "戈", "戶", "手", "支", "攴", "文", "斗", "斤", "方",
    "无", "日", "曰", "月", "木", "欠", "止", "歹", "殳", "毋",
    "比", "毛", "氏", "气", "水", "火", "爪", "父", "爻", "爿",
    "片", "牙", "牛", "犬", "玄", "玉", "瓜", "瓦", "甘", "生",
    "用", "田", "疋", "疒", "癶", "白", "皮", "皿", "目", "矛",
    "矢", "石", "示", "禸", "禾", "穴", "立", "竹", "米", "糸",
    "缶", "网", "羊", "羽", "老", "而", "耒", "耳", "聿", "肉",
    "臣", "自", "至", "臼", "舌", "舛", "舟", "艮", "色", "艸",
    "虍", "虫", "血", "行", "衣", "襾", "見", "角", "言", "谷",
    "豆", "豕", "豸", "貝", "赤", "走", "足", "身", "車", "辛",
    "辰", "辵", "邑", "酉", "釆", "里", "金", "長", "門", "阜",
    "隶", "隹", "雨", "靑", "非", "面", "革", "韋", "韭", "音",
    "頁", "風", "飛", "食", "首", "香", "馬", "骨", "高", "髟",
    "鬥", "鬯", "鬲", "鬼", "魚", "鳥", "鹵", "鹿", "麥", "麻",
    "黃", "黍", "黑", "黹", "黽", "鼎", "鼓", "鼠", "鼻", "齊",
    "齒", "龍", "龜", "龠",
]
KANGXI_NAME = [
    "one", "line", "dot", "slash", "second", "hook",
    "two", "lid", "person", "legs", "enter", "eight", "down box", "cover",
    "ice", "table", "open box", "knife", "power", "wrap",
    "spoon", "box", "hiding enclosure", "ten", "divination", "seal", "cliff",
    "private", "again",
    "mouth", "enclosure", "earth", "scholar", "go", "go slowly", "evening",
    "big", "woman", "child", "roof",
    "inch", "small", "lame", "corpse", "sprout", "mountain", "river", "work",
    "oneself", "turban",
    "dry", "short thread", "dotted cliff", "long stride", "two hands", "shoot",
    "bow", "snout", "bristle", "step",
    "heart", "spear", "door", "hand", "branch", "rap", "script", "dipper",
    "axe", "square",
    "not", "sun", "say", "moon", "tree", "lack", "stop", "death", "weapon",
    "do not",
    "compare", "fur", "clan", "steam", "water", "fire", "claw", "father",
    "double x", "half tree trunk",
    "slice", "fang", "cow", "dog", "profound", "jade", "melon", "tile",
    "sweet", "life",
    "use", "field", "bolt of cloth", "sickness", "dotted tent", "white",
    "skin", "dish", "eye", "spear",
    "arrow", "stone", "spirit", "track", "grain", "cave", "stand", "bamboo",
    "rice", "silk",
    "jar", "net", "sheep", "feather", "old", "and", "plow", "ear", "brush",
    "meat",
    "minister", "self", "arrive", "mortar", "tongue", "oppose", "boat",
    "stopping", "color", "grass",
    "tiger", "insect", "blood", "walk enclosure", "clothes", "west", "see",
    "horn", "speech", "valley",
    "bean", "pig", "badger", "shell", "red", "run", "foot", "body", "cart",
    "bitter",
    "morning", "walk", "city", "wine", "distinguish", "village", "gold",
    "long", "gate", "mound",
    "slave", "short-tailed bird", "rain", "blue", "wrong", "face", "leather",
    "tanned leather", "leek", "sound",
    "leaf", "wind", "fly", "eat", "head", "fragrant", "horse", "bone", "tall",
    "hair",
    "fight", "sacrificial wine", "cauldron", "ghost", "fish", "bird", "salt",
    "deer", "wheat", "hemp",
    "yellow", "millet", "black", "embroidery", "frog", "tripod", "drum",
    "rat", "nose", "even",
    "tooth", "dragon", "turtle", "flute",
]
assert len(KANGXI) == 214 and len(KANGXI_NAME) == 214

# Pre-2010 KANJIDIC JLPT (1 hardest … 4 easiest) → approximate N-level.
_OLD_JLPT = {4: 5, 3: 4, 2: 2, 1: 1}

_KATAKANA_START = 0x30A1
_KATAKANA_END = 0x30F6
_KATA_TO_HIRA = 0x60


def _fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def _ensure_kanjidic() -> Path:
    xml_path = RAW / "kanjidic2.xml"
    if xml_path.exists() and xml_path.stat().st_size > 1_000_000:
        return xml_path
    print(f"downloading {KANJIDIC_URL}")
    raw = _fetch(KANJIDIC_URL)
    gz_path = RAW / "kanjidic2.xml.gz"
    gz_path.write_bytes(raw)
    xml_path.write_bytes(gzip.decompress(raw))
    return xml_path


def _ensure_kradfile() -> Path:
    path = RAW / "kradfile-u"
    if path.exists() and path.stat().st_size > 50_000:
        return path
    print(f"downloading {KRADFILE_URL}")
    path.write_bytes(_fetch(KRADFILE_URL))
    return path


def _ensure_jlpt() -> dict[str, int]:
    """Map character → JLPT N-level (5 easiest … 1 hardest)."""
    path = RAW / "jlpt.json"
    lists: dict[str, list[str]]
    if path.exists():
        lists = json.loads(path.read_text(encoding="utf-8"))
    else:
        lists = {}
        for n in range(1, 6):
            url = JLPT_URL.format(n=n)
            print(f"downloading {url}")
            lists[str(n)] = json.loads(_fetch(url).decode("utf-8"))
        path.write_text(json.dumps(lists, ensure_ascii=False), encoding="utf-8")
    out: dict[str, int] = {}
    for n in range(1, 6):
        for ch in lists.get(str(n), []):
            out[ch] = n
    return out


def _kata_to_hira(text: str) -> str:
    out: list[str] = []
    for ch in text:
        cp = ord(ch)
        if _KATAKANA_START <= cp <= _KATAKANA_END:
            out.append(chr(cp - _KATA_TO_HIRA))
        else:
            out.append(ch)
    return "".join(out)


def _cap(meaning: str) -> str:
    meaning = meaning.strip()
    if not meaning:
        return meaning
    return meaning[0].upper() + meaning[1:]


def _parse_kradfile(path: Path) -> dict[str, list[str]]:
    parts: dict[str, list[str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or " : " not in line:
            continue
        left, right = line.split(" : ", 1)
        char = left.strip()
        seen: list[str] = []
        for p in right.split():
            if p and p != char and p not in seen:
                seen.append(p)
        if seen:
            parts[char] = seen
    return parts


def _parse_kanjidic(path: Path) -> dict[str, dict]:
    text = path.read_text(encoding="utf-8")
    start = text.find("<kanjidic2>")
    if start < 0:
        raise SystemExit("kanjidic2.xml has no <kanjidic2> root")
    root = ET.fromstring(text[start:])
    out: dict[str, dict] = {}
    for character in root.findall("character"):
        literal = character.findtext("literal")
        if not literal:
            continue
        on: list[str] = []
        kun: list[str] = []
        nanori: list[str] = []
        meanings: list[str] = []
        for rm in character.findall("reading_meaning"):
            for group in rm.findall("rmgroup"):
                for reading in group.findall("reading"):
                    rtype = reading.get("r_type")
                    val = (reading.text or "").strip()
                    if not val:
                        continue
                    if rtype == "ja_on":
                        on.append(_kata_to_hira(val))
                    elif rtype == "ja_kun":
                        kun.append(val)
                for meaning in group.findall("meaning"):
                    if meaning.get("m_lang"):
                        continue
                    cap = _cap(meaning.text or "")
                    if cap and cap not in meanings:
                        meanings.append(cap)
            for name in rm.findall("nanori"):
                val = (name.text or "").strip()
                if val and val not in nanori:
                    nanori.append(val)
        misc = character.find("misc")
        strokes = None
        grade = None
        freq = None
        old_jlpt = None
        if misc is not None:
            sc = misc.findtext("stroke_count")
            if sc and sc.isdigit():
                strokes = int(sc)
            gr = misc.findtext("grade")
            if gr and gr.isdigit():
                grade = int(gr)
            fr = misc.findtext("freq")
            if fr and fr.isdigit():
                freq = int(fr)
            jl = misc.findtext("jlpt")
            if jl and jl.isdigit():
                old_jlpt = int(jl)
        rad_no = None
        radical_el = character.find("radical")
        if radical_el is not None:
            for rad in radical_el.findall("rad_value"):
                if rad.get("rad_type") == "classical" and (rad.text or "").isdigit():
                    rad_no = int(rad.text)
                    break
        entry: dict = {"meanings": meanings, "on": on, "kun": kun}
        if strokes is not None:
            entry["strokes"] = strokes
        if grade is not None:
            entry["grade"] = grade
        if freq is not None:
            entry["freq"] = freq
        if old_jlpt is not None:
            entry["jlpt_old"] = old_jlpt
        if rad_no and 1 <= rad_no <= 214:
            entry["radical"] = KANGXI[rad_no - 1]
            entry["radical_name"] = KANGXI_NAME[rad_no - 1]
        if nanori:
            entry["nanori"] = nanori
        out[literal] = entry
    return out


def main() -> None:
    if len(KANGXI) != 214:
        raise SystemExit(f"KANGXI length {len(KANGXI)}")
    RAW.mkdir(parents=True, exist_ok=True)
    kanjidic = _parse_kanjidic(_ensure_kanjidic())
    parts_map = _parse_kradfile(_ensure_kradfile())
    jlpt = _ensure_jlpt()

    for char, entry in kanjidic.items():
        n = jlpt.get(char)
        if n is None:
            old = entry.pop("jlpt_old", None)
            n = _OLD_JLPT.get(old) if old else None
        else:
            entry.pop("jlpt_old", None)
        if n is not None:
            entry["jlpt"] = n
        comps = parts_map.get(char)
        if comps:
            entry["parts"] = comps

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(kanjidic, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(kanjidic)} characters → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
