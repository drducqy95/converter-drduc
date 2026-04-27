-- Split machine-generated TM from human-approved TM.

CREATE TABLE IF NOT EXISTS tm_machine (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_hash TEXT NOT NULL,
  source_text TEXT NOT NULL,
  machine_target TEXT NOT NULL,
  engine_version TEXT DEFAULT '',
  rule_version TEXT DEFAULT '',
  quality_score REAL DEFAULT 0.0,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  trace_json TEXT DEFAULT '',
  hit_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tm_approved (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_hash TEXT NOT NULL UNIQUE,
  source_text TEXT NOT NULL,
  approved_target TEXT NOT NULL,
  domain TEXT DEFAULT '',
  register TEXT DEFAULT '',
  reviewer TEXT DEFAULT '',
  approved_at TEXT DEFAULT CURRENT_TIMESTAMP,
  confidence REAL DEFAULT 1.0,
  provenance TEXT DEFAULT '',
  hit_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tm_reviewed (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_hash TEXT NOT NULL,
  source_text TEXT NOT NULL,
  machine_target TEXT DEFAULT '',
  edited_target TEXT DEFAULT '',
  reviewer TEXT DEFAULT '',
  review_status TEXT DEFAULT 'pending',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

