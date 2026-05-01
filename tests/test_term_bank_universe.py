import json

from src.pipeline.term_bank import TermBank


def test_term_bank_detects_universe_and_context_ranks_same_name():
    bank = TermBank()

    detected = dict(bank.detect_universe("萧炎收起异火，药尘提醒他斗气不可外泄。"))
    assert detected["dau_pha_thuong_khung"] >= 0.5

    marvel_record = bank.lookup_with_context("雷神", context_window="奥丁召见雷神，复仇者也抵达阿斯加德。")[0]
    assert marvel_record.target == "Thor"
    assert marvel_record.universe == "marvel"

    default_record = bank.lookup_with_context("雷神", context_window="雷神说道。雷神点头。")[0]
    assert default_record.target != "Thor"
    assert default_record.scope == "global"


def test_term_bank_ignores_deprecated_records_and_hot_reloads(tmp_path):
    root = tmp_path / "term_bank"
    global_dir = root / "global"
    global_dir.mkdir(parents=True)
    path = global_dir / "proper_names.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps({"source": "测试", "target": "Old", "status": "deprecated"}, ensure_ascii=False),
                json.dumps({"source": "测试", "target": "New", "status": "approved"}, ensure_ascii=False),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    bank = TermBank(root=root)
    assert [record.target for record in bank.lookup("测试")] == ["New"]

    path.write_text(
        json.dumps({"source": "测试", "target": "Reloaded", "status": "approved"}, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    bank.reload_universe("test")
    assert [record.target for record in bank.lookup("测试")] == ["Reloaded"]
