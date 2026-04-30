export const SCREENS = [
  "Dashboard",
  "Project Import",
  "Translation Workspace",
  "Dictionary Editor",
  "Translation Coach",
  "Pipeline Monitor",
  "Settings",
] as const;

export type ScreenKey = (typeof SCREENS)[number];

export const SCREEN_LABELS: Record<ScreenKey, string> = {
  Dashboard: "Tổng quan",
  "Project Import": "Project & Import",
  "Translation Workspace": "Workspace dịch",
  "Dictionary Editor": "Từ điển",
  "Translation Coach": "Coach & Review",
  "Pipeline Monitor": "QA & Pipeline",
  Settings: "Cài đặt",
};

export const POS_TAG_OPTIONS = [
  "NOUN",
  "VERB",
  "ADJECTIVE",
  "ADVERB",
  "PARTICLE",
  "PREPOSITION",
  "PRONOUN",
  "CONJUNCTION",
  "NUMBER",
] as const;

export const POS_SUB_OPTIONS: Record<string, string[]> = {
  NOUN: ["abstract", "classifier", "idiom", "location", "name", "component", "misc"],
  VERB: ["action", "state", "speech", "movement"],
  ADJECTIVE: ["quality", "simulative", "descriptive"],
  ADVERB: ["time", "manner", "degree"],
  PARTICLE: ["aspect", "possessive", "question", "adverbial", "complement"],
  PREPOSITION: ["locative", "temporal", "target", "direction", "ba_construction", "passive"],
  PRONOUN: ["personal", "demonstrative", "reflexive", "indefinite", "honorific"],
  CONJUNCTION: ["coordination", "contrast", "cause"],
  NUMBER: ["cardinal", "ordinal", "measure"],
};

export const ENTITY_OPTIONS = ["person", "location", "organization", "artifact", "project_term"] as const;
export const REORDER_ROLE_OPTIONS = ["head", "modifier", "complement"] as const;
