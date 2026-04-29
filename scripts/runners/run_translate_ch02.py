import sys, json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.engine.rbmt_translator import RBMTTranslator
from src.qa.report_generator import QAReportGenerator
from src.state.project_manager import ProjectManager

# --- CẤU HÌNH ---
PROJECT_DIR = r'D:\Converter by DrDuc\workspace_projects\New folder'   # Thư mục từ Phase 02
CHAPTER_FILE = 'chapter-002'                  # ID chương cần dịch

if __name__ == "__main__":
    project_dir = Path(PROJECT_DIR)

    # Load config từ Phase 02
    config_path = project_dir / 'working' / 'config' / 'translation_config.json'
    config = json.loads(config_path.read_text(encoding='utf-8'))

    # Load source text
    chapter_path = project_dir / 'source' / 'chapters' / f'{CHAPTER_FILE}.txt'
    source_text = chapter_path.read_text(encoding='utf-8')

    # Dịch
    translator = RBMTTranslator(tm_db_path=project_dir / 'state' / 'tm.sqlite')
    result = translator.translate_text(source_text, config=config)
    translator.export(result, project_dir, artifact_stem=CHAPTER_FILE)
    translator.close()

    # QA
    qa = QAReportGenerator()
    report = qa.run(source_text=source_text, translation_result=result, config=config)
    qa.write(report, project_dir, report_stem=f'qa_report_{CHAPTER_FILE}')

    print(f'Output: {project_dir / "output" / f"{CHAPTER_FILE}.txt"}')
    print(f'Draft:  {project_dir / "drafts" / f"{CHAPTER_FILE}_draft.txt"}')
    print(f'QA issues: {report["summary"]["issues"]}')
    print('--- Bản dịch (200 ký tự đầu) ---')
    print(result.clean_text[:200])
