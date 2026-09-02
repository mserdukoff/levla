from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.db import PassageRow, SessionLocal, SHELF_PUBLIC
from app.services.generate import save_authored_passage
from app.services.learner import calibration_passed
from app.services.seed_translations import TRANSLATIONS

# Original graded texts. Keep A1 Japanese on です/ます only; A1 Russian on
# nominative present only. Unknown lemmas are tolerated up to the CEFR cap.
SEED: list[dict] = [
    {
        "language": "ja",
        "level": "A1",
        "topic": "a quiet morning at home",
        "genre": "daily_life",
        "title": "私の朝",
        "text": (
            "私は学生です。今日は休みです。朝、水を飲みます。これはパンです。"
            "パンは美味しいです。母は家にいます。母は元気です。これはお茶です。"
            "お茶はいいです。私は本を読みます。本は新しいです。これはりんごです。"
            "りんごは美味しいです。私は学生です。家はきれいです。"
        ),
    },
    {
        "language": "ja",
        "level": "A1",
        "topic": "things on the table",
        "genre": "daily_life",
        "title": "これは本です",
        "text": (
            "これは本です。本は新しいです。それはペンです。ペンはここです。"
            "あれは水です。水はいいです。これはご飯です。ご飯は美味しいです。"
            "それはりんごです。りんごはここです。私は学生です。あなたは先生ですか。"
            "はい、私は先生です。今日はいいです。ここは家です。"
        ),
    },
    {
        "language": "ja",
        "level": "A1",
        "topic": "school and a teacher",
        "genre": "daily_life",
        "title": "学校の先生",
        "text": (
            "私は学生です。これは学校です。先生はここです。先生は元気です。"
            "私は本を読みます。本は新しいです。水を飲みます。これはペンです。"
            "友達は学生です。友達はいい人です。今日は学校です。"
            "学校はきれいです。私は家にいますか。いいえ、学校にいます。"
        ),
    },
    {
        "language": "ja",
        "level": "A1",
        "topic": "lunch with a friend",
        "genre": "daily_life",
        "title": "友達とご飯",
        "text": (
            "今日は友達とご飯です。ここはレストランです。これはパンです。"
            "それは水です。ご飯は美味しいです。私はお茶を飲みます。友達はコーヒーを飲みます。"
            "りんごもあります。りんごは美味しいです。私は学生です。友達も学生です。"
            "ありがとう。さようなら。"
        ),
    },
    {
        "language": "ja",
        "level": "A2",
        "topic": "a trip to the market",
        "genre": "daily_life",
        "title": "母と市場",
        "text": (
            "今日は金曜日です。母と一緒に市場に行きます。市場は家の近くです。"
            "朝早く起きました。母はおはようと言います。私は水を飲みました。"
            "りんごを二つ買いました。パンも買いました。お金はここです。"
            "母はりんごを買います。市場は人が多いです。それから家に帰ります。"
        ),
    },
    {
        "language": "ja",
        "level": "A2",
        "topic": "a train ride",
        "genre": "travel",
        "title": "電車に乗ります",
        "text": (
            "今日は駅に行きます。駅は家の近くです。電車に乗ります。"
            "切符を買いました。水も買いました。電車は便利です。友達は駅にいます。"
            "私は本を読みました。駅はきれいです。ホテルは駅の近くです。"
        ),
    },
    {
        "language": "ja",
        "level": "A2",
        "topic": "a new job",
        "genre": "work",
        "title": "新しい仕事",
        "text": (
            "私は新しい仕事をします。会社は駅の近くです。朝、バスに乗ります。"
            "水を飲みました。パンも食べました。仕事はいいです。先生ではありません。"
            "友達は会社にいます。お金はまだ少ないです。でも仕事は楽しいです。"
            "今日は早く帰りました。"
        ),
    },
    {
        "language": "ja",
        "level": "A2",
        "topic": "rainy afternoon",
        "genre": "daily_life",
        "title": "雨の日",
        "text": (
            "今日は雨です。私は家にいます。本を読みました。お茶を飲みました。"
            "母はご飯を作りました。パンもあります。友達は来ませんでした。"
            "窓の外は雨です。家は静かです。夜、もう一度本を読みます。"
            "明日は休みです。駅には行きません。"
        ),
    },
    {
        "language": "ja",
        "level": "B1",
        "topic": "reading on the train",
        "genre": "daily_life",
        "title": "電車で本を読む",
        "text": (
            "今、電車の中で本を読んでいます。隣の人は窓を見ています。"
            "駅に着いたら、友達に会います。友達は京都で働いています。"
            "もし雨なら、ホテルで待ちます。本は新しいし、とても面白いです。"
            "会社の仕事は忙しいですが、今日は休みです。"
        ),
    },
    {
        "language": "ja",
        "level": "B1",
        "topic": "working at a company",
        "genre": "work",
        "title": "会社で働く",
        "text": (
            "私は駅の近くの会社で働いています。朝は早く起きて、バスに乗ります。"
            "仕事をしているとき、水をよく飲みます。友達も同じ会社にいます。"
            "忙しい日はご飯を外で食べます。もし早く終わったら、本を読みます。"
            "お金はまだ少ないですが、仕事は楽しいです。"
        ),
    },
    {
        "language": "ja",
        "level": "B1",
        "topic": "waiting for a friend",
        "genre": "travel",
        "title": "駅で待つ",
        "text": (
            "今、駅で友達を待っています。電車が遅れているとメールが来ました。"
            "雨が降っています。ホテルは駅の近くにあります。着いたら、一緒にご飯を食べます。"
            "京都は初めてではありません。前に一度来ました。人は多いですが、きれいな町です。"
        ),
    },
    {
        "language": "ja",
        "level": "B2",
        "topic": "a meeting with a teacher",
        "genre": "work",
        "title": "先生がいらっしゃいます",
        "text": (
            "今、先生がいらっしゃいます。会社は駅の近くです。"
            "質問はあります。仕事は大切です。終わったら、駅まで行きます。"
            "今日は長いですが、いい仕事です。"
        ),
    },
    {
        "language": "ja",
        "level": "B2",
        "topic": "after a long day",
        "genre": "daily_life",
        "title": "長い一日のあと",
        "text": (
            "仕事が終わって、雨の中を歩いて帰りました。家に着くと、母がご飯を作ってくれていました。"
            "今日は会議が多くて、あまり水も飲めませんでした。それでも本を少し読みました。"
            "明日は早く出かけるはずです。もし雨なら、バスに乗ります。"
        ),
    },
    {
        "language": "ru",
        "level": "A1",
        "topic": "this is Anna",
        "genre": "daily_life",
        "title": "Это Анна",
        "text": (
            "Я студент. Это книга. Книга новая. Мама здесь. Это вода. Вода холодная. "
            "Это чай. Чай хороший. Анна здесь. Это комната. Комната новая. "
            "Анна студентка. День хороший."
        ),
    },
    {
        "language": "ru",
        "level": "A1",
        "topic": "the table",
        "genre": "daily_life",
        "title": "Это стол",
        "text": (
            "Это книга. Книга новая. Это вода. Вода холодная. Это чай. Чай хороший. "
            "Это мама. Мама здесь. Это Анна. Анна здесь. Это комната. Комната новая. "
            "Я студент. День хороший."
        ),
    },
    {
        "language": "ru",
        "level": "A1",
        "topic": "a student at home",
        "genre": "daily_life",
        "title": "Анна дома",
        "text": (
            "Анна студентка. Анна здесь. Это комната. Комната новая. "
            "Это книга. Книга новая. Это чай. Чай хороший. "
            "Мама здесь. Мама добрая. День хороший. Я студент."
        ),
    },
    {
        "language": "ru",
        "level": "A1",
        "topic": "food on the table",
        "genre": "daily_life",
        "title": "Чай и хлеб",
        "text": (
            "Это чай. Чай хороший. Это вода. Вода холодная. Это книга. Книга новая. "
            "Это мама. Мама здесь. Это Анна. Анна студентка. "
            "Я студент. День хороший. Комната новая."
        ),
    },
    {
        "language": "ru",
        "level": "A2",
        "topic": "a morning at the market",
        "genre": "daily_life",
        "title": "Утро на рынке",
        "text": (
            "Утром я иду на рынок. Рынок рядом с домом. Я покупаю хлеб и воду. "
            "Мама покупает яблоки. Вчера я был дома. Сегодня я читаю книгу. "
            "На рынке много людей. Потом я иду домой. Чай уже горячий."
        ),
    },
    {
        "language": "ru",
        "level": "A2",
        "topic": "a train to the city",
        "genre": "travel",
        "title": "Поезд в город",
        "text": (
            "Сегодня я еду в город. Вокзал рядом. Я покупаю билет. "
            "В поезде я читаю книгу и пью воду. Вчера я был дома. "
            "Друг ждёт меня на вокзале. Город большой. Отель рядом."
        ),
    },
    {
        "language": "ru",
        "level": "A2",
        "topic": "a new job",
        "genre": "work",
        "title": "Новая работа",
        "text": (
            "Я работаю в компании. Компания рядом с вокзалом. Утром я пью чай. "
            "Вчера я читал книгу. Сегодня я иду на работу. Работа хорошая. "
            "Друг тоже работает здесь. Вечером я иду домой."
        ),
    },
    {
        "language": "ru",
        "level": "A2",
        "topic": "a rainy day at home",
        "genre": "daily_life",
        "title": "Дождь",
        "text": (
            "Сегодня дождь. Я дома. Я читаю книгу и пью чай. Мама готовит хлеб. "
            "Вчера друг был дома. Сегодня он не приходит. За окном вода. "
            "Вечером я снова читаю книгу. Завтра я иду на рынок."
        ),
    },
    {
        "language": "ru",
        "level": "B1",
        "topic": "reading on the train",
        "genre": "daily_life",
        "title": "Книга в поезде",
        "text": (
            "Сейчас я еду в поезде и читаю книгу. Если друг позвонит, я выйду на вокзале. "
            "Работа сегодня не ждёт меня, потому что это выходной. "
            "Когда поезд остановится, я куплю воду. Город уже близко."
        ),
    },
    {
        "language": "ru",
        "level": "B1",
        "topic": "a day at the office",
        "genre": "work",
        "title": "День в компании",
        "text": (
            "Я работаю в компании у вокзала. Утром я пью чай и читаю письма. "
            "Если работа заканчивается рано, я иду домой пешком. "
            "Друг работает со мной. Вечером мы говорим о книге и о городе."
        ),
    },
    {
        "language": "ru",
        "level": "B1",
        "topic": "waiting at the station",
        "genre": "travel",
        "title": "На вокзале",
        "text": (
            "Я жду друга на вокзале. Поезд идёт с опозданием, потому что сегодня дождь. "
            "Когда он приедет, мы пойдём в отель рядом. Я уже был в этом городе. "
            "Людей много, но место тихое у окна."
        ),
    },
    {
        "language": "ru",
        "level": "B2",
        "topic": "after a long meeting",
        "genre": "work",
        "title": "После собрания",
        "text": (
            "После длинного собрания я шёл домой под дождём. Мама уже готовила хлеб, "
            "хотя я просил её не ждать. Работа сегодня требовала внимания, "
            "которое я редко отдаю письмам. Завтра, если не будет дождя, я поеду на рынок."
        ),
    },
    {
        "language": "ru",
        "level": "B2",
        "topic": "a city evening",
        "genre": "folklore",
        "title": "Вечер в городе",
        "text": (
            "Вечером город становится тише, хотя люди всё ещё идут к вокзалу. "
            "Я читал книгу у окна, пока чай остывал. Друг, который живёт рядом, "
            "сказал, что завтра мы поедем в другой район. Если будет дождь, мы останемся дома."
        ),
    },
]


def seed_library(db: Session | None = None) -> int:
    close = False
    if db is None:
        db = SessionLocal()
        close = True
    existing_rows = {
        (row.language, row.title): row
        for row in db.query(PassageRow).all()
    }
    added = 0
    try:
        for item in SEED:
            key = (item["language"], item["title"])
            translation = TRANSLATIONS.get(key)
            row = existing_rows.get(key)
            if row is not None and calibration_passed(row):
                if translation and not getattr(row, "translation", None):
                    row.translation = translation
                if getattr(row, "shelf_status", None) != SHELF_PUBLIC:
                    row.shelf_status = SHELF_PUBLIC
                db.commit()
                continue
            if row is not None:
                db.delete(row)
                db.commit()
            saved = save_authored_passage(
                db,
                language=item["language"],
                level=item["level"],
                topic=item["topic"],
                genre=item.get("genre"),
                title=item["title"],
                text=item["text"],
                translation=translation,
            )
            existing_rows[key] = saved
            added += 1
    finally:
        if close:
            db.close()
    return added
