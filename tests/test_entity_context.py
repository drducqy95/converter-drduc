from src.pipeline.entity_scanner import EntityScanner


def test_entity_scanner_disambiguates_same_name_without_output_tag():
    scanner = EntityScanner()
    try:
        entities = scanner.scan("奥丁召见雷神，洛基站在一旁，复仇者等待命令。")
        default_entities = scanner.scan("雷神说道。雷神点头。")
    finally:
        scanner.close()

    by_source = {entity.source: entity for entity in entities}
    assert by_source["雷神"].target == "Thor"
    assert by_source["雷神"].universe == "marvel"
    assert "[marvel]" not in by_source["雷神"].target

    default_by_source = {entity.source: entity for entity in default_entities}
    assert default_by_source["雷神"].target != "Thor"
    assert default_by_source["雷神"].universe != "marvel"


def test_entity_scanner_uses_project_universe_before_generic_context():
    scanner = EntityScanner(universe_id="Marvel")
    try:
        entities = scanner.scan("雷神说道。")
    finally:
        scanner.close()

    by_source = {entity.source: entity for entity in entities}
    assert by_source["雷神"].target == "Thor"
    assert by_source["雷神"].universe == "marvel"
