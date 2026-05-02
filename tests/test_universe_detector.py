from src.pipeline.universe_detector import UniverseContext, UniverseDetector, UniverseSignal


def test_detect_xianxia_by_character():
    detector = UniverseDetector()

    ctx = detector.detect("韓立拿出掌天瓶")

    assert isinstance(ctx, UniverseContext)
    assert ctx.primary_universe == "pham_nhan_tu_tien"
    assert not ctx.is_multi_universe


def test_detect_simplified_dau_pha_by_fingerprint():
    detector = UniverseDetector()

    ctx = detector.detect("萧炎催动斗气，异火出现，药尘提醒他。")

    assert ctx.primary_universe == "dau_pha_thuong_khung"
    assert ctx.signals[0].confidence >= 0.65


def test_detect_bleach():
    detector = UniverseDetector()

    ctx = detector.detect("黑崎一護使出斬魄刀。")

    assert ctx.primary_universe == "bleach"


def test_detect_naruto_with_alias_fingerprint():
    detector = UniverseDetector()

    ctx = detector.detect("漩涡鸣人使用影分身。")

    assert ctx.primary_universe == "naruto"


def test_multi_universe():
    detector = UniverseDetector()

    ctx = detector.detect("韓立和蕭炎在一起。")

    assert ctx.is_multi_universe
    assert {"pham_nhan_tu_tien", "dau_pha_thuong_khung"}.issubset(set(ctx.active_universes))


def test_unknown_fallback():
    detector = UniverseDetector()

    ctx = detector.detect("今天天气不错。")

    assert ctx.is_unknown
    assert ctx.primary_universe is None


def test_co_occurrence_boost():
    detector = UniverseDetector()

    ctx_single = detector.detect("韓立走了過來。")
    ctx_pair = detector.detect("韓立和南宮婉走了過來。")
    sig_single = next(signal for signal in ctx_single.signals if signal.universe_id == "pham_nhan_tu_tien")
    sig_pair = next(signal for signal in ctx_pair.signals if signal.universe_id == "pham_nhan_tu_tien")

    assert sig_pair.confidence > sig_single.confidence


def test_sentence_level_detection():
    detector = UniverseDetector()
    sentences = [
        "韓立走進了黃楓谷。",
        "他坐下來修煉靈氣。",
        "這時南宮婉走了過來。",
    ]

    results = detector.detect_sentence_level(sentences)

    assert len(results) == 3
    assert all(result.primary_universe == "pham_nhan_tu_tien" for result in results)


def test_backward_compat_tuple_format():
    detector = UniverseDetector()

    ctx = detector.detect("蕭炎催動斗氣。")
    tuples = [(signal.universe_id, signal.confidence) for signal in ctx.signals]

    assert isinstance(ctx.signals[0], UniverseSignal)
    assert len(tuples) >= 1
    assert isinstance(tuples[0][0], str)
    assert isinstance(tuples[0][1], float)
