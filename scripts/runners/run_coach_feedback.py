#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_coach_feedback.py — Coach Learning: Nhập feedback → Sinh rule → Cập nhật pipeline

Có 3 chế độ chạy:
  1. Interactive — nhập feedback trực tiếp qua terminal
  2. File mode   — đọc từ file JSON chứa danh sách feedback
  3. Quick term  — thêm nhanh 1 cặp thuật ngữ source->target

Usage:
    python scripts/runners/run_coach_feedback.py                                          # Interactive
    python scripts/runners/run_coach_feedback.py --file feedback_batch.json               # File mode
    python scripts/runners/run_coach_feedback.py --term "张陈" "Trương Trần"              # Quick term
    python scripts/runners/run_coach_feedback.py --term "张陈" "Trương Trần" --lock       # Quick locked entity
"""
import sys, json, argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
sys.stdout.reconfigure(encoding='utf-8')

from src.learning.natural_feedback_engine import NaturalFeedbackEngine

DEFAULT_PROJECT = r'D:\Converter by DrDuc\workspace_projects\New folder'


def apply_suggestions(suggestions: list[dict], project_dir: Path) -> dict:
    """Áp các suggestion vào learned_terms.json và translation_config.json."""
    learned_path = project_dir / 'working' / 'config' / 'learned_terms.json'
    config_path = project_dir / 'working' / 'config' / 'translation_config.json'

    learned = json.loads(learned_path.read_text(encoding='utf-8')) if learned_path.exists() else {
        'phrase_overrides': [], 'locked_entities': []
    }
    config = json.loads(config_path.read_text(encoding='utf-8')) if config_path.exists() else {}

    applied = {'phrase_overrides': 0, 'locked_entities': 0, 'style_changes': 0, 'guidance': 0}

    existing_phrases = {item['source'] for item in learned.get('phrase_overrides', [])}
    existing_locked = {item['source'] for item in learned.get('locked_entities', [])}

    for suggestion in suggestions:
        rule_type = suggestion.get('rule_type', '')
        payload = suggestion.get('payload', {})

        if rule_type == 'phrase_override':
            source = payload.get('source', '')
            target = payload.get('target', '')
            if source and source not in existing_phrases:
                learned.setdefault('phrase_overrides', []).append({
                    'source': source, 'target': target, 'origin': 'coach_feedback'
                })
                existing_phrases.add(source)
                applied['phrase_overrides'] += 1

        elif rule_type == 'locked_entity':
            source = payload.get('source', '')
            target = payload.get('target', '')
            if source and source not in existing_locked:
                learned.setdefault('locked_entities', []).append({
                    'source': source, 'target': target,
                    'entity_type': payload.get('entity_type', 'project_term'),
                    'origin': 'coach_feedback'
                })
                existing_locked.add(source)
                applied['locked_entities'] += 1

        elif rule_type == 'style_profile':
            profile = payload.get('style_profile')
            if profile:
                config['style_profile'] = profile
                applied['style_changes'] += 1

        elif rule_type == 'naturalization':
            nat = payload.get('naturalization', {})
            if nat:
                config['naturalization'] = {**config.get('naturalization', {}), **nat}
                applied['style_changes'] += 1

        elif rule_type == 'style_context':
            ctx = payload.get('style_context', {})
            if ctx.get('genre_hints'):
                config['genre_hints'] = ctx['genre_hints']
                applied['style_changes'] += 1

        else:
            applied['guidance'] += 1

    # Write back
    learned_path.parent.mkdir(parents=True, exist_ok=True)
    learned_path.write_text(json.dumps(learned, ensure_ascii=False, indent=2), encoding='utf-8')
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')

    return applied


def run_interactive(engine: NaturalFeedbackEngine, project_dir: Path):
    """Chế độ interactive — nhập feedback từng dòng."""
    print('🎓 Coach Learning — Interactive Mode')
    print('   Nhập feedback bằng tiếng Việt hoặc format "源文 -> 译文"')
    print('   Gõ "done" hoặc Ctrl+C để kết thúc.')
    print()

    total_applied = {'phrase_overrides': 0, 'locked_entities': 0, 'style_changes': 0, 'guidance': 0}

    while True:
        try:
            feedback = input('📝 Feedback: ').strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not feedback or feedback.lower() in ('done', 'exit', 'quit'):
            break

        # Kiểm tra nếu có format "source -> target"
        source_text = ''
        preferred = ''
        if '->' in feedback or '=>' in feedback or '→' in feedback:
            parts = feedback.replace('=>', '->').replace('→', '->').split('->', 1)
            if len(parts) == 2:
                source_text = parts[0].strip().strip('"\'')
                preferred = parts[1].strip().strip('"\'')

        result = engine.analyze(
            feedback_text=feedback,
            source_text=source_text,
            preferred_translation=preferred,
            scope='project',
        )

        suggestions = result.get('suggestions', [])
        if suggestions:
            for s in suggestions:
                conf = s.get('confidence', 0)
                icon = '🟢' if conf >= 0.8 else '🟡' if conf >= 0.6 else '🔵'
                print(f'   {icon} [{s["rule_type"]}] {s["title"]} (confidence: {conf:.2f})')
                if 'source' in s.get('payload', {}):
                    print(f'      {s["payload"]["source"]} → {s["payload"]["target"]}')

            applied = apply_suggestions(suggestions, project_dir)
            for key, count in applied.items():
                total_applied[key] = total_applied.get(key, 0) + count
                if count > 0:
                    print(f'   ✅ Applied {count} {key}')
        print()

    print(f'\n📊 Session total: {total_applied}')


def run_file_mode(engine: NaturalFeedbackEngine, project_dir: Path, filepath: str):
    """Chế độ file — đọc danh sách feedback từ JSON."""
    data = json.loads(Path(filepath).read_text(encoding='utf-8'))
    items = data if isinstance(data, list) else data.get('feedbacks', [data])

    print(f'🎓 Coach Learning — File Mode ({len(items)} feedbacks)')
    all_suggestions = []

    for i, item in enumerate(items, 1):
        feedback = item.get('feedback', item.get('feedback_text', ''))
        source = item.get('source', item.get('source_text', ''))
        preferred = item.get('preferred', item.get('preferred_translation', ''))

        result = engine.analyze(
            feedback_text=feedback,
            source_text=source,
            preferred_translation=preferred,
            scope=item.get('scope', 'project'),
        )
        suggestions = result.get('suggestions', [])
        all_suggestions.extend(suggestions)

        for s in suggestions:
            conf = s.get('confidence', 0)
            icon = '🟢' if conf >= 0.8 else '🟡' if conf >= 0.6 else '🔵'
            print(f'  {i}. {icon} [{s["rule_type"]}] {s["title"]} ({conf:.2f})')

    applied = apply_suggestions(all_suggestions, project_dir)
    print(f'\n📊 Applied: {applied}')


def run_quick_term(project_dir: Path, source: str, target: str, lock: bool):
    """Chế độ quick — thêm nhanh 1 cặp thuật ngữ."""
    rule_type = 'locked_entity' if lock else 'phrase_override'
    suggestion = {
        'rule_type': rule_type,
        'payload': {'source': source, 'target': target, 'entity_type': 'project_term'}
    }
    applied = apply_suggestions([suggestion], project_dir)
    icon = '🔒' if lock else '📝'
    print(f'{icon} {source} → {target} [{rule_type}]')
    print(f'✅ Applied: {applied}')


def main():
    parser = argparse.ArgumentParser(description='Coach Learning Feedback Engine')
    parser.add_argument('--project', default=DEFAULT_PROJECT, help='Project directory')
    parser.add_argument('--file', help='JSON file with feedback entries')
    parser.add_argument('--term', nargs=2, metavar=('SOURCE', 'TARGET'), help='Quick add term')
    parser.add_argument('--lock', action='store_true', help='Lock term as entity (with --term)')
    args = parser.parse_args()

    project_dir = Path(args.project)

    if args.term:
        run_quick_term(project_dir, args.term[0], args.term[1], args.lock)
    elif args.file:
        engine = NaturalFeedbackEngine()
        run_file_mode(engine, project_dir, args.file)
    else:
        engine = NaturalFeedbackEngine()
        run_interactive(engine, project_dir)


if __name__ == '__main__':
    main()
