/**
 * Converter by DrDuc - Main Entry Point
 * Advanced Chinese-Vietnamese Translation System
 * 
 * This system implements a rule-based and statistical approach to translation
 * without relying on Large Language Models (LLMs), featuring:
 * 1. Preprocessing (Traditional->Simplified, Pinyin resolution)
 * 2. Syntax transfer rules for Chinese-Vietnamese grammar
 * 3. Incremental learning capabilities
 */

const fs = require('fs');
const path = require('path');

// Import core modules
const StructurePreserver = require('./src/preprocessor/structure_preserver');
const TraditionalToSimplified = require('./src/preprocessor/traditional_to_simplified');
const PinyinProcessor = require('./src/preprocessor/pinyin_processor');
const MorphologicalAnalyzer = require('./src/parser/morphological_analyzer');
const DependencyParser = require('./src/parser/dependency_parser');
const SyntaxTransferRules = require('./src/rules/syntax_transfer_rules');
const TranslationMemory = require('./src/learning/translation_memory');
const RuleInductionEngine = require('./src/learning/rule_induction_engine');
const ContextManager = require('./src/learning/sliding_context_manager');

class DrDucTranslator {
  constructor(options = {}) {
    this.options = {
      preserveStructures: true,
      convertTraditional: true,
      resolvePinyin: true,
      analyzeSyntax: true,
      applyTransferRules: true,
      learnFromEdits: true,
      ...options
    };

    // Initialize core components
    this.structurePreserver = new StructurePreserver();
    this.traditionalToSimplified = new TraditionalToSimplified();
    this.pinyinProcessor = new PinyinProcessor();
    this.morphologicalAnalyzer = new MorphologicalAnalyzer();
    this.dependencyParser = new DependencyParser();
    this.syntaxTransferRules = new SyntaxTransferRules();
    this.translationMemory = new TranslationMemory();
    this.ruleInductionEngine = new RuleInductionEngine();
    this.contextManager = new ContextManager();

    console.log('DrDuc Translator initialized with options:', this.options);
  }

  /**
   * Main translation method
   * @param {string} text - Input text to translate
   * @param {Object} context - Additional context for translation
   * @returns {Promise<string>} - Translated text
   */
  async translate(text, context = {}) {
    try {
      console.log('Starting translation process...');
      
      // Step 1: Preserve non-text structures
      let preservedText;
      let structureMap;
      if (this.options.preserveStructures) {
        const result = this.structurePreserver.preserve(text);
        preservedText = result.text;
        structureMap = result.map;
        console.log('Step 1: Structures preserved');
      } else {
        preservedText = text;
      }

      // Step 2: Convert Traditional to Simplified Chinese
      let simplifiedText;
      if (this.options.convertTraditional) {
        simplifiedText = this.traditionalToSimplified.convert(preservedText);
        console.log('Step 2: Traditional to Simplified conversion completed');
      } else {
        simplifiedText = preservedText;
      }

      // Step 3: Resolve Pinyin to Simplified Chinese
      let resolvedText;
      if (this.options.resolvePinyin) {
        resolvedText = await this.pinyinProcessor.resolve(simplifiedText);
        console.log('Step 3: Pinyin resolution completed');
      } else {
        resolvedText = simplifiedText;
      }

      // Step 4: Analyze syntax and morphology
      let analyzedText;
      if (this.options.analyzeSyntax) {
        analyzedText = await this.morphologicalAnalyzer.analyze(resolvedText);
        console.log('Step 4: Morphological analysis completed');
      } else {
        analyzedText = resolvedText;
      }

      // Step 5: Apply syntax transfer rules
      let transferredText;
      if (this.options.applyTransferRules) {
        transferredText = this.syntaxTransferRules.apply(analyzedText, context);
        console.log('Step 5: Syntax transfer rules applied');
      } else {
        transferredText = analyzedText;
      }

      // Step 6: Restore preserved structures
      let finalText;
      if (this.options.preserveStructures && structureMap) {
        finalText = this.structurePreserver.restore(transferredText, structureMap);
        console.log('Step 6: Structures restored');
      } else {
        finalText = transferredText;
      }

      // Step 7: Learn from the translation (if enabled)
      if (this.options.learnFromEdits) {
        this.translationMemory.store(text, finalText);
        console.log('Step 7: Translation stored in memory');
      }

      console.log('Translation completed successfully!');
      return finalText;

    } catch (error) {
      console.error('Translation failed:', error);
      throw error;
    }
  }

  /**
   * Process post-editing feedback to improve the system
   * @param {string} originalText - Original source text
   * @param {string} translatedText - Original machine translation
   * @param {string} editedText - Human-edited version
   */
  processPostEdit(originalText, translatedText, editedText) {
    try {
      console.log('Processing post-edit feedback...');
      
      // Store the improved translation pair
      this.translationMemory.store(originalText, editedText);
      
      // Extract and induce new rules from the edit
      this.ruleInductionEngine.induceFromEdit(originalText, translatedText, editedText);
      
      console.log('Post-edit feedback processed successfully');
    } catch (error) {
      console.error('Post-edit processing failed:', error);
      throw error;
    }
  }

  /**
   * Get translation statistics and quality metrics
   * @returns {Object} - Statistics object
   */
  getStats() {
    return {
      translationMemorySize: this.translationMemory.getSize(),
      ruleCount: this.syntaxTransferRules.getRuleCount(),
      learnedRuleCount: this.ruleInductionEngine.getLearnedRuleCount(),
      totalTranslations: this.translationMemory.getTotalTranslations()
    };
  }
}

// Export the translator class
module.exports = DrDucTranslator;

// If run directly, provide a simple CLI interface
if (require.main === module) {
  console.log('DrDuc Translator CLI Interface');
  
  // Example usage
  const translator = new DrDucTranslator({
    preserveStructures: true,
    convertTraditional: true,
    resolvePinyin: true,
    analyzeSyntax: true,
    applyTransferRules: true,
    learnFromEdits: true
  });

  console.log('Translator is ready for use.');
  console.log('Available methods:');
  console.log('  - translator.translate(text, context)');
  console.log('  - translator.processPostEdit(original, translated, edited)');
  console.log('  - translator.getStats()');
}
