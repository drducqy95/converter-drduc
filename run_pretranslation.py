#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_pretranslation.py — Chạy Phase 02 (Pretranslation)
Quét entity, terminology, relationship từ source text.

Usage:
    python run_pretranslation.py
    python run_pretranslation.py --project "D:\path\to\project"
"""
import sys, json, argparse
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from src.pipeline.pretranslation_pipeline import PreTranslationPipeline

DEFAULT_PROJECT = r'D:\Converter by DrDuc\workspace_projects\New folder'

def main():
    parser = argparse.ArgumentParser(description='Run pretranslation pipeline')
    parser.add_argument('--project', default=DEFAULT_PROJECT, help='Project directory')
    args = parser.parse_args()

    project_dir = Path(args.project)
    source_dir = project_dir / 'source'

    if not source_dir.exists():
        print(f'❌ Source directory not found: {source_dir}')
        return

    print(f'📂 Project: {project_dir}')
    print(f'📄 Source:  {source_dir}')
    print()

    pipeline = PreTranslationPipeline()
    try:
        result = pipeline.prepare(source_dir, project_dir)
        print(f'✅ Pretranslation complete!')
        print(f'   Chapters: {len(result.chapters)}')
        print(f'   Entities: {len(result.entities)}')
        print(f'   Relationships: {len(result.relationships)}')
        print()

        # Show output paths
        working = project_dir / 'working'
        for json_file in sorted(working.rglob('*.json')):
            rel = json_file.relative_to(project_dir)
            print(f'   📋 {rel}')
    finally:
        pipeline.close()

if __name__ == '__main__':
    main()
