import traceback, sys
from pathlib import Path

filepath = r"D:\Dichtrung\Source\Source full\Đại Thừa Kỳ Mới Có Nghịch Tập Hệ Thống_Tối Bạch Đích Ô Nha.html"
print(f"File size: {Path(filepath).stat().st_size / 1024 / 1024:.1f} MB", file=sys.stderr)

from src.pipeline.pretranslation_pipeline import PreTranslationPipeline
p = PreTranslationPipeline()
try:
    r = p.prepare(filepath, "workspace_projects/project-dtk-test")
    print(f"OK: {len(r.chapters)} chapters", file=sys.stderr)
except Exception as exc:
    print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
finally:
    p.close()
