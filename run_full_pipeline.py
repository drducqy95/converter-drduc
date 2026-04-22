#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_full_pipeline.py — Pipeline hoàn chỉnh: Pretranslation → Dịch → QA → Learning Report

Quy trình:
  1. Quét entity/terminology từ source
  2. Dịch văn bản (RBMT)  
  3. Chạy QA kiểm tra chất lượng
  4. Xuất bản dịch + báo cáo

Usage:
    python run_full_pipeline.py                                  # Dịch chapter-001
    python run_full_pipeline.py --chapter chapter-002             # Dịch chapter cụ thể
    python run_full_pipeline.py --batch chapter-001 chapter-005   # Dịch hàng loạt
    python run_full_pipeline.py --all                             # Dịch tất cả chapter
"""
import sys, json, argparse, time
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from src.pipeline.pretranslation_pipeline import PreTranslationPipeline
from src.engine.rbmt_translator import RBMTTranslator
from src.qa.report_generator import QAReportGenerator

DEFAULT_PROJECT = r'D:\Converter by DrDuc\workspace_projects\New folder'


def discover_chapters(project_dir: Path) -> list[str]:
    """Tìm tất cả file chapter trong source/chapters/."""
    chapters_dir = project_dir / 'source' / 'chapters'
    if not chapters_dir.exists():
        return []
    return sorted([
        f.stem for f in chapters_dir.glob('*.txt')
        if f.stem.startswith('chapter-')
    ])


def translate_chapter(
    chapter_id: str,
    project_dir: Path,
    config: dict,
    translator: RBMTTranslator,
) -> dict:
    """Dịch 1 chương, trả về summary."""
    chapter_path = project_dir / 'source' / 'chapters' / f'{chapter_id}.txt'
    if not chapter_path.exists():
        return {'chapter': chapter_id, 'status': 'SKIP', 'reason': 'File not found'}

    source_text = chapter_path.read_text(encoding='utf-8')
    t0 = time.time()

    # Translate
    result = translator.translate_text(source_text, config=config)
    translator.export(result, project_dir, artifact_stem=chapter_id)

    # QA
    qa = QAReportGenerator()
    report = qa.run(source_text=source_text, translation_result=result, config=config)
    qa.write(report, project_dir, report_stem=f'qa_report_{chapter_id}')

    elapsed = time.time() - t0
    output_path = project_dir / 'output' / f'{chapter_id}.txt'
    char_count = len(result.clean_text)
    qa_issues = report.get('summary', {}).get('issues', 0)

    return {
        'chapter': chapter_id,
        'status': 'OK',
        'output': str(output_path),
        'chars': char_count,
        'qa_issues': qa_issues,
        'time_s': round(elapsed, 2),
    }


def main():
    parser = argparse.ArgumentParser(description='Full Translation Pipeline')
    parser.add_argument('--project', default=DEFAULT_PROJECT, help='Project directory')
    parser.add_argument('--chapter', default='chapter-001', help='Single chapter ID')
    parser.add_argument('--batch', nargs='+', help='Multiple chapter IDs')
    parser.add_argument('--all', action='store_true', help='Translate all chapters')
    parser.add_argument('--skip-pretranslation', action='store_true',
                        help='Skip entity scanning (reuse existing)')
    args = parser.parse_args()

    project_dir = Path(args.project)
    config_path = project_dir / 'working' / 'config' / 'translation_config.json'

    if not config_path.exists():
        print(f'❌ Config not found: {config_path}')
        print('   Run pretranslation first: python run_pretranslation.py')
        return

    config = json.loads(config_path.read_text(encoding='utf-8'))

    # Load learned terms if available
    learned_path = project_dir / 'working' / 'config' / 'learned_terms.json'
    if learned_path.exists():
        learned = json.loads(learned_path.read_text(encoding='utf-8'))
        phrase_count = len(learned.get('phrase_overrides', []))
        locked_count = len(learned.get('locked_entities', []))
        print(f'📚 Loaded learned terms: {phrase_count} phrases, {locked_count} locked entities')
    else:
        print('📚 No learned terms found (first run)')

    # Step 1: Pretranslation
    if not args.skip_pretranslation:
        print('\n━━━ Phase 1: Pretranslation ━━━')
        source_dir = project_dir / 'source'
        if source_dir.exists():
            pipeline = PreTranslationPipeline()
            try:
                result = pipeline.prepare(source_dir, project_dir)
                print(f'   ✅ Entities: {len(result.entities)}, Relationships: {len(result.relationships)}')
            finally:
                pipeline.close()
        else:
            print(f'   ⚠️ Source directory not found, skipping pretranslation')
    else:
        print('\n━━━ Pretranslation skipped (--skip-pretranslation) ━━━')

    # Step 2: Determine chapters to translate
    if args.all:
        chapters = discover_chapters(project_dir)
    elif args.batch:
        chapters = args.batch
    else:
        chapters = [args.chapter]

    if not chapters:
        print('❌ No chapters to translate')
        return

    # Step 3: Translate
    print(f'\n━━━ Phase 2: Translation ({len(chapters)} chapters) ━━━')
    translator = RBMTTranslator(tm_db_path=project_dir / 'state' / 'tm.sqlite')

    results = []
    total_t0 = time.time()
    for i, chapter_id in enumerate(chapters, 1):
        print(f'\n   [{i}/{len(chapters)}] {chapter_id}...', end=' ', flush=True)
        summary = translate_chapter(chapter_id, project_dir, config, translator)
        results.append(summary)

        if summary['status'] == 'OK':
            print(f'✅ {summary["chars"]} chars, {summary["qa_issues"]} QA issues ({summary["time_s"]}s)')
        else:
            print(f'⚠️ {summary.get("reason", "unknown error")}')

    translator.close()
    total_elapsed = time.time() - total_t0

    # Step 4: Summary
    print(f'\n━━━ Summary ━━━')
    ok_count = sum(1 for r in results if r['status'] == 'OK')
    total_chars = sum(r.get('chars', 0) for r in results if r['status'] == 'OK')
    total_issues = sum(r.get('qa_issues', 0) for r in results if r['status'] == 'OK')
    print(f'   Chapters: {ok_count}/{len(chapters)} OK')
    print(f'   Total chars: {total_chars:,}')
    print(f'   Total QA issues: {total_issues}')
    print(f'   Total time: {total_elapsed:.1f}s')
    print(f'\n   📂 Output: {project_dir / "output"}')
    print(f'   📋 QA reports: {project_dir / "reports"}')

    if total_issues > 0:
        print(f'\n💡 Tip: Chạy coach learning để cải thiện:')
        print(f'         python run_coach_feedback.py')
        print(f'         Sau đó dịch lại: python run_full_pipeline.py --skip-pretranslation')


if __name__ == '__main__':
    main()
