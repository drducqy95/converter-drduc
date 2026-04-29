import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.pretranslation_pipeline import PreTranslationPipeline

# Thư mục NGUỒN và ĐÍCH của bạn
SOURCE_DIR = r'D:\Dichtrung\Source\Source split\An Quy Nam Hai_Khung Pho Dich A Phi'
PROJECT = r'D:\Converter by DrDuc\workspace_projects\New folder'

if __name__ == "__main__":
    pipeline = PreTranslationPipeline()
    result = pipeline.prepare(SOURCE_DIR, PROJECT)
    pipeline.close()

    print(f'Format: {result.imported.detected_format}')
    print(f'Chapters: {[c.chapter_id for c in result.chapters]}')
    print(f'Config style: {result.config.get("style_profile")}')
