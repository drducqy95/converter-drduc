---
title: Translation Engine - Chinese Structure Rewriter - RegexOverlap/TranslationAmbiguity Pattern
type: pattern
slug: translation-engine-chinese-structure-rewriter-regexoverlaptranslationambiguity-pattern
category: patterns
created: 2026-04-22T09:32:58
updated: 2026-04-22T09:32:58
status: active
source: /debug
tags: ["Translation Engine - Chinese Structure Rewriter", "RegexOverlap/TranslationAmbiguity", "auto-generated"]
---

# Translation Engine - Chinese Structure Rewriter - RegexOverlap/TranslationAmbiguity Pattern

> [!WARNING]
> **Origin:** `ERR_0006`
> **Module:** `Translation Engine - Chinese Structure Rewriter` | **Type:** `RegexOverlap/TranslationAmbiguity`

## 🚨 The Issue

**Message:** 
```text
Regex overlapping caused '其他的坟头' to match Category 2 Possessive '他的坟' resulting in 'của nó của hắn đầu', and Chinese single-digit classifiers '两座' translated to 'lạng tấm' due to Trie confusing '两' as weight 'lượng/lạng'.
```

**Root Cause:** 
1) Cat 2 regex for '他' matched greedily inside '其他'. 2) Cat 7 replacing the measure word '座' with 'tấm' left '两' isolated, causing the Trie engine to misinterpret '两' based on its default isolated meaning 'lạng'.

## 🛠️ The Fix

1) Inserted Regex Negative Lookbehind '(?<!其)他' in Cat 2 so OWNER cannot be part of '其他'. 2) Explicitly mapped Chinese numerals [一两三四...] directly to Vietnamese [một hai ba...] within the Cat 7 classification regex so isolated numerals never reach Trie.

**Files Affected:**
- `d:\Converter by DrDuc\src\engine\zh_structure_rewriter.py`

## 🛡️ Prevention

> [!TIP]
> - Check for similar issues in `Translation Engine - Chinese Structure Rewriter` module
> - Add test case to prevent regression
