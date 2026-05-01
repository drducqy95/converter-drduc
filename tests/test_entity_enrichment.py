from src.pipeline.entity_enrichment import EntityEnrichmentManager
from src.pipeline.entity_scanner import EntitySuggestion


def test_entity_enrichment_review_approval_and_deduped_save(tmp_path):
    manager = EntityEnrichmentManager(root=tmp_path / "term_bank", project_id="project-x")
    entity = EntitySuggestion(
        source="测试人",
        target="Trắc Thí Nhân",
        entity_type="person",
        confidence=0.82,
        source_dict="heuristic_name_mining",
        ambiguity_flag=False,
        count=1,
        positions=[0],
    )

    prepared = manager.prepare_for_review([entity], detected_universes=["Phàm Nhân Tu Tiên"], context="韩立见到测试人。")
    assert prepared[0].universe == "pham_nhan_tu_tien"
    assert prepared[0].enrichment_ready is True

    approved = [manager.approve_entity(prepared[0])]
    assert manager.save_to_term_bank(approved, target_scope="private") == 1
    assert manager.save_to_term_bank(approved, target_scope="private") == 0

    saved = manager.term_bank.lookup("测试人")
    assert len(saved) == 1
    assert saved[0].target == "Trắc Thí Nhân"
    assert saved[0].scope == "private"


def test_entity_enrichment_markdown_report():
    entity = EntitySuggestion(
        source="测试地",
        target="Trắc Thí Địa",
        entity_type="location",
        confidence=0.8,
        source_dict="user_review",
        ambiguity_flag=False,
        universe="real_world",
        review_status="pending",
    )

    report = EntityEnrichmentManager.export_review_report([entity])
    assert "# Entity Enrichment Review" in report
    assert "测试地" in report
    assert "real_world" in report


def test_entity_enrichment_defaults_to_project_story_universe(tmp_path):
    manager = EntityEnrichmentManager(root=tmp_path / "term_bank", project_id="Đấu Phá Thương Khung")
    entity = EntitySuggestion(
        source="新角色",
        target="Tân Nhân Vật",
        entity_type="person",
        confidence=0.8,
        source_dict="user_review",
        ambiguity_flag=False,
    )

    prepared = manager.prepare_for_review([entity], context="萧炎遇见新角色。")
    approved = [manager.approve_entity(prepared[0])]
    assert approved[0].universe == "dau_pha_thuong_khung"
    assert manager.save_to_term_bank(approved) == 1
    assert (tmp_path / "term_bank" / "universes" / "dau_pha_thuong_khung" / "user_terms.jsonl").exists()
