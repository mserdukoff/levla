#!/usr/bin/env python3
"""Write Japanese CEFR vocab bands + ja→en gloss JSON."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOCAB_OUT = ROOT / "data" / "vocab" / "ja_cefr.json"
GLOSS_OUT = ROOT / "data" / "gloss" / "ja_en.json"

PEDAGOGICAL: dict[str, tuple[str, str]] = {}


def add(level: str, pairs: list[tuple[str, str]]) -> None:
    for lemma, gloss in pairs:
        lemma = lemma.strip()
        if lemma and lemma not in PEDAGOGICAL:
            PEDAGOGICAL[lemma] = (level, gloss.strip())


add(
    "A1",
    [
        ("私", "I"),
        ("僕", "I (male)"),
        ("あなた", "you"),
        ("彼", "he"),
        ("彼女", "she"),
        ("これ", "this"),
        ("それ", "that"),
        ("あれ", "that over there"),
        ("どれ", "which"),
        ("ここ", "here"),
        ("そこ", "there"),
        ("あそこ", "over there"),
        ("どこ", "where"),
        ("だれ", "who"),
        ("何", "what"),
        ("いつ", "when"),
        ("どう", "how"),
        ("はい", "yes"),
        ("いいえ", "no"),
        ("です", "to be (polite)"),
        ("ます", "polite verb ending"),
        ("いる", "to be (animate)"),
        ("ある", "to be (inanimate) / to have"),
        ("する", "to do"),
        ("なる", "to become"),
        ("行く", "to go"),
        ("来る", "to come"),
        ("帰る", "to return home"),
        ("食べる", "to eat"),
        ("飲む", "to drink"),
        ("見る", "to see / watch"),
        ("聞く", "to hear / ask"),
        ("読む", "to read"),
        ("書く", "to write"),
        ("話す", "to speak"),
        ("言う", "to say"),
        ("買う", "to buy"),
        ("売る", "to sell"),
        ("待つ", "to wait"),
        ("会う", "to meet"),
        ("分かる", "to understand"),
        ("知る", "to know"),
        ("思う", "to think"),
        ("好き", "to like"),
        ("嫌い", "to dislike"),
        ("欲しい", "to want (object)"),
        ("人", "person"),
        ("男", "man"),
        ("女", "woman"),
        ("子供", "child"),
        ("友達", "friend"),
        ("家族", "family"),
        ("父", "father"),
        ("母", "mother"),
        ("兄", "older brother"),
        ("姉", "older sister"),
        ("弟", "younger brother"),
        ("妹", "younger sister"),
        ("名前", "name"),
        ("先生", "teacher"),
        ("学生", "student"),
        ("医者", "doctor"),
        ("日本", "Japan"),
        ("日本語", "Japanese language"),
        ("英語", "English"),
        ("国", "country"),
        ("町", "town"),
        ("家", "house / home"),
        ("部屋", "room"),
        ("学校", "school"),
        ("大学", "university"),
        ("会社", "company"),
        ("駅", "station"),
        ("店", "shop"),
        ("市場", "market"),
        ("時", "o'clock / time"),
        ("病院", "hospital"),
        ("銀行", "bank"),
        ("食堂", "cafeteria"),
        ("レストラン", "restaurant"),
        ("ホテル", "hotel"),
        ("水", "water"),
        ("お茶", "tea"),
        ("コーヒー", "coffee"),
        ("ご飯", "rice / meal"),
        ("パン", "bread"),
        ("肉", "meat"),
        ("魚", "fish"),
        ("野菜", "vegetable"),
        ("果物", "fruit"),
        ("りんご", "apple"),
        ("時間", "time"),
        ("今", "now"),
        ("今日", "today"),
        ("明日", "tomorrow"),
        ("昨日", "yesterday"),
        ("朝", "morning"),
        ("昼", "noon / daytime"),
        ("夜", "night"),
        ("週", "week"),
        ("月", "month / moon"),
        ("年", "year"),
        ("月曜日", "Monday"),
        ("火曜日", "Tuesday"),
        ("水曜日", "Wednesday"),
        ("木曜日", "Thursday"),
        ("金曜日", "Friday"),
        ("土曜日", "Saturday"),
        ("日曜日", "Sunday"),
        ("天気", "weather"),
        ("雨", "rain"),
        ("雪", "snow"),
        ("風", "wind"),
        ("空", "sky"),
        ("本", "book"),
        ("紙", "paper"),
        ("ペン", "pen"),
        ("電話", "telephone"),
        ("車", "car"),
        ("電車", "train"),
        ("バス", "bus"),
        ("自転車", "bicycle"),
        ("切符", "ticket"),
        ("お金", "money"),
        ("円", "yen"),
        ("仕事", "work"),
        ("休み", "holiday / rest"),
        ("問題", "problem / question"),
        ("質問", "question"),
        ("答え", "answer"),
        ("言葉", "word / language"),
        ("一", "one"),
        ("二", "two"),
        ("三", "three"),
        ("四", "four"),
        ("五", "five"),
        ("六", "six"),
        ("七", "seven"),
        ("八", "eight"),
        ("九", "nine"),
        ("十", "ten"),
        ("百", "hundred"),
        ("千", "thousand"),
        ("万", "ten thousand"),
        ("大きい", "big"),
        ("小さい", "small"),
        ("新しい", "new"),
        ("古い", "old"),
        ("いい", "good"),
        ("悪い", "bad"),
        ("高い", "expensive / tall"),
        ("安い", "cheap"),
        ("暑い", "hot (weather)"),
        ("寒い", "cold"),
        ("難しい", "difficult"),
        ("易しい", "easy"),
        ("多い", "many"),
        ("少ない", "few"),
        ("長い", "long"),
        ("短い", "short"),
        ("近い", "near"),
        ("遠い", "far"),
        ("早い", "early / fast"),
        ("遅い", "late / slow"),
        ("白い", "white"),
        ("黒い", "black"),
        ("赤い", "red"),
        ("青い", "blue"),
        ("元気", "healthy / well"),
        ("静か", "quiet"),
        ("有名", "famous"),
        ("便利", "convenient"),
        ("きれい", "pretty / clean"),
        ("とても", "very"),
        ("少し", "a little"),
        ("もう", "already / more"),
        ("まだ", "still / not yet"),
        ("いつも", "always"),
        ("よく", "often / well"),
        ("時々", "sometimes"),
        ("一緒", "together"),
        ("本当", "really / true"),
        ("どうぞ", "please / here you are"),
        ("どうも", "thanks"),
        ("ありがとう", "thank you"),
        ("すみません", "excuse me / sorry"),
        ("こんにちは", "hello"),
        ("さようなら", "goodbye"),
        ("おはよう", "good morning"),
        ("は", "topic particle"),
        ("が", "subject particle"),
        ("を", "object particle"),
        ("に", "to / at / in"),
        ("で", "at / by / with"),
        ("の", "of / 's"),
        ("と", "and / with"),
        ("も", "also"),
        ("から", "from / because"),
        ("まで", "until"),
        ("ね", "right? (particle)"),
        ("よ", "emphasis particle"),
        ("か", "question particle"),
    ],
)

add(
    "A2",
    [
        ("て", "te-form connective"),
        ("た", "past (plain)"),
        ("ない", "not (plain)"),
        ("ください", "please"),
        ("ましょう", "let's"),
        ("たい", "want to"),
        ("でも", "but"),
        ("そして", "and then"),
        ("それから", "after that"),
        ("だから", "so / therefore"),
        ("けど", "but"),
        ("まだ", "still"),
        ("もう", "already"),
        ("すぐ", "soon / immediately"),
        ("ゆっくり", "slowly"),
        ("たくさん", "a lot"),
        ("全部", "all"),
        ("自分", "oneself"),
        ("他", "other"),
        ("同じ", "same"),
        ("違う", "different / to differ"),
        ("使う", "to use"),
        ("作る", "to make"),
        ("持つ", "to hold / have"),
        ("取る", "to take"),
        ("置く", "to put"),
        ("開ける", "to open"),
        ("閉める", "to close"),
        ("始める", "to begin"),
        ("終わる", "to end"),
        ("働く", "to work"),
        ("休む", "to rest"),
        ("遊ぶ", "to play"),
        ("歌う", "to sing"),
        ("泳ぐ", "to swim"),
        ("走る", "to run"),
        ("歩く", "to walk"),
        ("乗る", "to ride"),
        ("降りる", "to get off"),
        ("着く", "to arrive"),
        ("出る", "to leave / come out"),
        ("入る", "to enter"),
        ("住む", "to live"),
        ("教える", "to teach"),
        ("習う", "to learn"),
        ("覚える", "to remember"),
        ("忘れる", "to forget"),
        ("考える", "to think (consider)"),
        ("決める", "to decide"),
        ("選ぶ", "to choose"),
        ("送る", "to send"),
        ("もらう", "to receive"),
        ("あげる", "to give"),
        ("くれる", "to give (to me)"),
        ("貸す", "to lend"),
        ("借りる", "to borrow"),
        ("払う", "to pay"),
        ("見せる", "to show"),
        ("呼ぶ", "to call"),
        ("着る", "to wear"),
        ("寝る", "to sleep"),
        ("起きる", "to wake up / get up"),
        ("洗う", "to wash"),
        ("切る", "to cut"),
        ("旅行", "trip"),
        ("観光", "sightseeing"),
        ("地図", "map"),
        ("道", "road / way"),
        ("右", "right"),
        ("左", "left"),
        ("前", "front / before"),
        ("後ろ", "behind"),
        ("中", "inside"),
        ("外", "outside"),
        ("上", "up / above"),
        ("下", "down / below"),
        ("隣", "next door"),
        ("近く", "nearby"),
        ("空港", "airport"),
        ("出口", "exit"),
        ("入口", "entrance"),
        ("予約", "reservation"),
        ("荷物", "luggage"),
        ("写真", "photo"),
        ("映画", "movie"),
        ("音楽", "music"),
        ("スポーツ", "sport"),
        ("趣味", "hobby"),
        ("誕生日", "birthday"),
        ("プレゼント", "present"),
        ("服", "clothes"),
        ("靴", "shoes"),
        ("体", "body"),
        ("頭", "head"),
        ("手", "hand"),
        ("足", "foot / leg"),
        ("目", "eye"),
        ("口", "mouth"),
        ("病気", "illness"),
        ("薬", "medicine"),
        ("熱", "fever"),
        ("元気", "fine / pep"),
        ("春", "spring"),
        ("夏", "summer"),
        ("秋", "autumn"),
        ("冬", "winter"),
        ("季節", "season"),
        ("色", "color"),
        ("意味", "meaning"),
        ("理由", "reason"),
        ("約束", "promise / appointment"),
        ("予定", "plan / schedule"),
        ("必要", "necessary"),
        ("大丈夫", "it's okay"),
        ("心配", "worry"),
        ("大変", "tough / terrible"),
        ("簡単", "simple"),
        ("特別", "special"),
        ("大切", "important"),
        ("危険", "dangerous"),
        ("安全", "safe"),
        ("自由", "free"),
        ("忙しい", "busy"),
        ("暇", "free time"),
        ("楽しい", "fun"),
        ("嬉しい", "glad"),
        ("悲しい", "sad"),
        ("痛い", "painful"),
        ("美味しい", "delicious"),
        ("まずい", "tastes bad"),
        ("面白い", "interesting"),
        ("つまらない", "boring"),
        ("初めて", "for the first time"),
        ("出かける", "to go out"),
        ("にぎやか", "lively"),
        ("色々", "various"),
        ("最後", "last"),
        ("最初", "first"),
        ("次", "next"),
        ("回", "times (counter)"),
        ("人", "people (counter)"),
        ("つ", "generic counter"),
        ("本", "long-object counter"),
        ("枚", "flat-object counter"),
        ("円", "yen"),
    ],
)

add(
    "B1",
    [
        ("ている", "progressive / resultative"),
        ("れる", "potential / passive aux"),
        ("られる", "potential / passive"),
        ("させる", "causative"),
        ("ば", "if (conditional)"),
        ("たら", "if / when"),
        ("なら", "if (given that)"),
        ("ながら", "while"),
        ("ために", "in order to / for"),
        ("について", "about"),
        ("として", "as"),
        ("によって", "by / depending on"),
        ("場合", "case / situation"),
        ("経験", "experience"),
        ("関係", "relation"),
        ("社会", "society"),
        ("文化", "culture"),
        ("歴史", "history"),
        ("政治", "politics"),
        ("経済", "economy"),
        ("環境", "environment"),
        ("自然", "nature"),
        ("科学", "science"),
        ("技術", "technology"),
        ("情報", "information"),
        ("教育", "education"),
        ("国際", "international"),
        ("世界", "world"),
        ("未来", "future"),
        ("過去", "past"),
        ("現在", "present"),
        ("変化", "change"),
        ("発展", "development"),
        ("影響", "influence"),
        ("原因", "cause"),
        ("結果", "result"),
        ("目的", "purpose"),
        ("方法", "method"),
        ("機会", "opportunity"),
        ("努力", "effort"),
        ("成功", "success"),
        ("失敗", "failure"),
        ("意見", "opinion"),
        ("考え", "idea / thought"),
        ("気持ち", "feeling"),
        ("性格", "personality"),
        ("習慣", "habit / custom"),
        ("伝統", "tradition"),
        ("法律", "law"),
        ("権利", "right"),
        ("義務", "duty"),
        ("責任", "responsibility"),
        ("平和", "peace"),
        ("戦争", "war"),
        ("人口", "population"),
        ("都市", "city"),
        ("田舎", "countryside"),
        ("産業", "industry"),
        ("製品", "product"),
        ("価格", "price"),
        ("給料", "salary"),
        ("税金", "tax"),
        ("比べる", "to compare"),
        ("調べる", "to investigate"),
        ("説明する", "to explain"),
        ("相談する", "to consult"),
        ("反対する", "to oppose"),
        ("賛成する", "to agree"),
        ("参加する", "to participate"),
        ("利用する", "to use"),
        ("続ける", "to continue"),
        ("変える", "to change"),
        ("増える", "to increase"),
        ("減る", "to decrease"),
        ("起こる", "to happen"),
        ("助ける", "to help"),
        ("守る", "to protect"),
        ("信じる", "to believe"),
        ("疑う", "to doubt"),
        ("期待する", "to expect"),
        ("可能", "possible"),
        ("不可能", "impossible"),
        ("普通", "ordinary"),
        ("特別", "special"),
        ("複雑", "complex"),
        ("十分", "enough"),
        ("当然", "natural / of course"),
        ("明らか", "clear / obvious"),
        ("重要", "important"),
        ("最近", "recently"),
        ("将来", "in the future"),
        ("突然", "suddenly"),
        ("ほとんど", "almost"),
        ("必ず", "without fail"),
        ("ぜひ", "by all means"),
        ("もし", "if"),
        ("たぶん", "probably"),
        ("きっと", "surely"),
        ("やはり", "as expected"),
        ("実は", "actually"),
        ("例えば", "for example"),
        ("つまり", "in other words"),
        ("しかし", "however"),
        ("一方", "on the other hand"),
        ("そのため", "for that reason"),
    ],
)

add(
    "B2",
    [
        ("られる", "passive / potential"),
        ("わけ", "reason / conclusion"),
        ("はず", "ought to / expected"),
        ("べき", "should"),
        ("つつ", "while (formal)"),
        ("ものの", "although"),
        ("にもかかわらず", "despite"),
        ("に対して", "toward / in contrast to"),
        ("に関して", "regarding"),
        ("に基づいて", "based on"),
        ("次第", "as soon as / depending on"),
        ("以上", "beyond / since"),
        ("以下", "below / the following"),
        ("傾向", "tendency"),
        ("構造", "structure"),
        ("制度", "system / institution"),
        ("政策", "policy"),
        ("改革", "reform"),
        ("議論", "debate"),
        ("分析", "analysis"),
        ("評価", "evaluation"),
        ("効果", "effect"),
        ("効率", "efficiency"),
        ("課題", "issue / task"),
        ("対策", "countermeasure"),
        ("状況", "situation"),
        ("背景", "background"),
        ("視点", "viewpoint"),
        ("立場", "standpoint"),
        ("役割", "role"),
        ("価値", "value"),
        ("意識", "awareness"),
        ("態度", "attitude"),
        ("現象", "phenomenon"),
        ("事実", "fact"),
        ("仮説", "hypothesis"),
        ("理論", "theory"),
        ("研究", "research"),
        ("発表", "presentation / announcement"),
        ("報告", "report"),
        ("記事", "article"),
        ("世論", "public opinion"),
        ("格差", "disparity"),
        ("高齢化", "aging (of society)"),
        ("少子化", "declining birthrate"),
        ("グローバル化", "globalization"),
        ("持続", "sustainability / continuation"),
        ("尊重", "respect"),
        ("配慮", "consideration"),
        ("貢献", "contribution"),
        ("達成", "achievement"),
        ("維持", "maintenance"),
        ("改善", "improvement"),
        ("解決", "solution"),
        ("いらっしゃる", "to come / be (honorific)"),
        ("おっしゃる", "to say (honorific)"),
        ("いたす", "to do (humble)"),
        ("申す", "to say (humble)"),
        ("ございます", "to be (polite)"),
        ("いただく", "to receive (humble)"),
        ("差し上げる", "to give (humble)"),
        ("拝見する", "to look (humble)"),
        ("承知する", "to understand / consent"),
        ("拝見", "looking (humble)"),
    ],
)


JLPT_JSON = {
    "A1": "https://raw.githubusercontent.com/evanclan/OpenJLPT/main/data/json/vocab/n5.json",
    "A2": "https://raw.githubusercontent.com/evanclan/OpenJLPT/main/data/json/vocab/n4.json",
    "B1": "https://raw.githubusercontent.com/evanclan/OpenJLPT/main/data/json/vocab/n3.json",
    "B2": "https://raw.githubusercontent.com/evanclan/OpenJLPT/main/data/json/vocab/n2.json",
}
JLPT_CSV = {
    "A1": "https://raw.githubusercontent.com/jamsinclair/open-anki-jlpt-decks/master/src/n5.csv",
    "A2": "https://raw.githubusercontent.com/jamsinclair/open-anki-jlpt-decks/master/src/n4.csv",
    "B1": "https://raw.githubusercontent.com/jamsinclair/open-anki-jlpt-decks/master/src/n3.csv",
    "B2": "https://raw.githubusercontent.com/jamsinclair/open-anki-jlpt-decks/master/src/n2.csv",
}


def _http_json(url: str):
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": "levla-lexicon"})
    with urllib.request.urlopen(req, timeout=60) as res:
        return json.loads(res.read().decode("utf-8"))


def _http_text(url: str) -> str:
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": "levla-lexicon"})
    with urllib.request.urlopen(req, timeout=60) as res:
        return res.read().decode("utf-8")


def _ingest_openjlpt(vocab: dict[str, str], gloss: dict[str, str]) -> int:
    added = 0
    for band, url in JLPT_JSON.items():
        try:
            payload = _http_json(url)
        except Exception as exc:
            print(f"OpenJLPT {band} skipped: {exc}")
            continue
        rows = payload if isinstance(payload, list) else payload.get("vocab") or payload.get("items") or []
        for row in rows:
            if not isinstance(row, dict):
                continue
            lemma = (row.get("word") or row.get("expression") or "").strip()
            meanings = row.get("meanings") or row.get("meaning") or []
            if isinstance(meanings, list):
                meaning = ", ".join(str(m) for m in meanings[:2])
            else:
                meaning = str(meanings)
            if not lemma or lemma in vocab:
                continue
            vocab[lemma] = band
            if meaning:
                gloss[lemma] = meaning[:80]
            added += 1
    return added


def _ingest_jlpt_csv(vocab: dict[str, str], gloss: dict[str, str]) -> int:
    import csv
    import io

    added = 0
    for band, url in JLPT_CSV.items():
        try:
            text = _http_text(url)
        except Exception as exc:
            print(f"JLPT CSV {band} skipped: {exc}")
            continue
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            lemma = (row.get("expression") or row.get("word") or row.get("Expression") or "").strip()
            meaning = (row.get("meaning") or row.get("Meaning") or row.get("english") or "").strip()
            if not lemma or lemma in vocab:
                continue
            vocab[lemma] = band
            if meaning:
                gloss[lemma] = meaning.split(";")[0][:80]
            added += 1
    return added

JMDICT_URL = "https://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz"
JMDICT_PATH = ROOT / "data" / "raw" / "JMdict_e.xml"


def _nf_band(pris: list[str]) -> str | None:
    nfs: list[int] = []
    for p in pris:
        if p.startswith("nf") and p[2:].isdigit():
            nfs.append(int(p[2:]))
    if nfs:
        rank = min(nfs)
        if rank <= 8:
            return "A1"
        if rank <= 16:
            return "A2"
        if rank <= 24:
            return "B1"
        if rank <= 40:
            return "B2"
        return None
    if any(p in {"ichi1", "news1", "spec1", "gai1"} for p in pris):
        return "B2"
    return None


def _download_jmdict() -> Path | None:
    import gzip
    import urllib.request

    gz_path = ROOT / "data" / "raw" / "JMdict_e.gz"
    gz_path.parent.mkdir(parents=True, exist_ok=True)
    if not JMDICT_PATH.exists():
        try:
            print("Downloading JMdict_e.gz …")
            urllib.request.urlretrieve(JMDICT_URL, gz_path)
            with gzip.open(gz_path, "rb") as src, JMDICT_PATH.open("wb") as dest:
                dest.write(src.read())
        except Exception as exc:
            print(f"JMdict download skipped: {exc}")
            return None
    return JMDICT_PATH if JMDICT_PATH.exists() else None


def _parse_jmdict(path: Path) -> list[tuple[str, str, str]]:
    import re
    import xml.etree.ElementTree as ET

    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"<!DOCTYPE[^>]*>", "", raw, count=1)
    raw = re.sub(r"&([a-zA-Z0-9_-]+);", r"\1", raw)
    root = ET.fromstring(raw)
    rows: list[tuple[str, str, str]] = []
    for entry in root.findall("entry"):
        kebs = [k.findtext("keb") or "" for k in entry.findall("k_ele")]
        rebs = [r.findtext("reb") or "" for r in entry.findall("r_ele")]
        lemma = next((k for k in kebs if k), None) or next((r for r in rebs if r), None)
        if not lemma:
            continue
        pris: list[str] = []
        for ele in entry.findall("k_ele") + entry.findall("r_ele"):
            for pri in ele.findall("ke_pri") + ele.findall("re_pri"):
                if pri.text:
                    pris.append(pri.text)
        band = _nf_band(pris)
        if not band:
            continue
        gloss = ""
        sense = entry.find("sense")
        if sense is not None:
            g = sense.find("gloss")
            if g is not None and g.text:
                gloss = g.text.strip()[:80]
        if not gloss:
            continue
        rows.append((lemma, band, gloss))
    return rows


def main() -> None:
    vocab = {lemma: level for lemma, (level, _g) in PEDAGOGICAL.items()}
    gloss = {lemma: g for lemma, (_l, g) in PEDAGOGICAL.items()}

    added_jlpt = _ingest_openjlpt(vocab, gloss)
    print(f"Added {added_jlpt} OpenJLPT lemmas")
    if len(vocab) < 3000:
        added_csv = _ingest_jlpt_csv(vocab, gloss)
        print(f"Added {added_csv} JLPT CSV lemmas")

    jmdict = _download_jmdict()
    if jmdict is not None and len(vocab) < 3000:
        added = 0
        for lemma, band, meaning in _parse_jmdict(jmdict):
            if lemma in vocab:
                continue
            vocab[lemma] = band
            gloss[lemma] = meaning
            added += 1
            if len(vocab) >= 4200:
                break
        print(f"Added {added} JMdict lemmas")

    VOCAB_OUT.parent.mkdir(parents=True, exist_ok=True)
    GLOSS_OUT.parent.mkdir(parents=True, exist_ok=True)
    VOCAB_OUT.write_text(
        json.dumps(vocab, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    GLOSS_OUT.write_text(
        json.dumps(gloss, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    counts: dict[str, int] = defaultdict(int)
    for level in vocab.values():
        counts[level] += 1
    print(f"Wrote {len(vocab)} lemmas → {VOCAB_OUT}")
    print(f"Wrote {len(gloss)} glosses → {GLOSS_OUT}")
    print("Bands:", dict(counts))
    if len(vocab) < 3000:
        raise SystemExit(f"Lexicon too small ({len(vocab)}). Need JMdict or more pedagogical entries.")


if __name__ == "__main__":
    main()
