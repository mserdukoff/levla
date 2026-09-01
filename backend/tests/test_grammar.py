from app.services.morph import analyze_text


def ja(text: str):
    return analyze_text(text, "ja")


def by_text(tokens, surface: str):
    return next(t for t in tokens if t.text == surface)


def labels(tok):
    return [(p.text, p.label) for p in tok.conj]


def test_ha_ga_wo_roles():
    toks = ja("私は本を読みます。先生が来ます。")
    assert by_text(toks, "は").role == "topic"
    assert by_text(toks, "を").role == "object"
    assert by_text(toks, "が").role == "subject"


def test_other_particles_are_particle():
    toks = ja("東京へ行きます。駅で待ちます。")
    assert by_text(toks, "へ").role == "particle"
    assert by_text(toks, "で").role == "particle"


def test_tabemashita_chain():
    toks = ja("食べました。")
    head = by_text(toks, "食べ")
    assert labels(head) == [
        ("食べ", "stem"),
        ("まし", "polite"),
        ("た", "past"),
    ]
    mashita = by_text(toks, "まし")
    ta = by_text(toks, "た")
    assert mashita.conj_id == head.conj_id
    assert ta.conj_id == head.conj_id
    assert head.role == "verb"
    assert mashita.role == "aux"
    assert ta.role == "aux"


def test_taberu_splits_dictionary_ending():
    toks = ja("食べる。")
    head = by_text(toks, "食べる")
    assert labels(head) == [("食べ", "stem"), ("る", "dictionary")]
    assert head.role == "verb"


def test_yondeimasu_te_iru():
    toks = ja("読んでいます。")
    head = by_text(toks, "読ん")
    assert labels(head) == [
        ("読ん", "stem"),
        ("で", "te-form"),
        ("い", "progressive"),
        ("ます", "polite"),
    ]


def test_ikanai_negative():
    toks = ja("行かない。")
    head = by_text(toks, "行か")
    assert labels(head) == [("行か", "stem"), ("ない", "negative")]


def test_desu_copula_after_noun():
    toks = ja("学生です。")
    desu = by_text(toks, "です")
    assert desu.role == "aux"
    assert labels(desu) == [("です", "copula")]
    assert by_text(toks, "学生").role is None


def test_nouns_stay_uncolored():
    toks = ja("私は学生です。")
    assert by_text(toks, "私").role is None
    assert by_text(toks, "学生").role is None


def test_i_adj_and_na_adj():
    toks = ja("高い本です。静かな部屋です。")
    takai = by_text(toks, "高い")
    assert takai.role == "adj"
    assert labels(takai) == [("高", "stem"), ("い", "attributive")]
    shizuka = by_text(toks, "静か")
    na = by_text(toks, "な")
    assert shizuka.role == "adj"
    assert na.role == "aux"
    assert ("な", "adnominal") in labels(shizuka)


def test_passive_causative_chain():
    toks = ja("食べさせられた。")
    head = by_text(toks, "食べ")
    assert labels(head) == [
        ("食べ", "stem"),
        ("させ", "causative"),
        ("られ", "passive / potential"),
        ("た", "past"),
    ]


def test_volitional_split():
    toks = ja("食べよう。")
    head = by_text(toks, "食べよう")
    assert labels(head) == [("食べ", "stem"), ("よう", "volitional")]


def test_ba_conditional():
    toks = ja("行けば。")
    head = by_text(toks, "行け")
    assert labels(head) == [("行け", "stem"), ("ば", "conditional")]


def test_particle_pos_detail():
    toks = ja("私は本を読みます。")
    assert by_text(toks, "は").morph.pos_detail == "binding"
    assert by_text(toks, "を").morph.pos_detail == "case"


def test_russian_roles():
    toks = analyze_text("Я читаю книгу в парке.", "ru")
    chitayu = next(t for t in toks if t.lemma == "читать")
    assert chitayu.role == "verb"
    v = next(t for t in toks if t.text.lower() == "в")
    assert v.role == "particle"
    knigu = next(t for t in toks if t.lemma == "книга")
    assert knigu.role is None
