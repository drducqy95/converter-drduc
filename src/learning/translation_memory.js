/**
 * Translation Memory
 * Manages stored translations and provides retrieval for similar texts
 */

class TranslationMemory {
  constructor() {
    this.memory = new Map(); // Stores source -> target translation pairs
    this.totalTranslations = 0;
    this.accessCount = new Map(); // Tracks how often each translation is used
  }

  /**
   * Store a translation pair
   * @param {string} source - Source text
   * @param {string} target - Target translation
   */
  store(source, target) {
    // Use the source text as a key to store the translation
    this.memory.set(source, target);
    this.totalTranslations++;
    
    // Initialize access count for this translation
    if (!this.accessCount.has(source)) {
      this.accessCount.set(source, 0);
    }
    
    console.log(`Stored translation pair (${this.totalTranslations} total)`);
  }

  /**
   * Retrieve a translation for source text
   * @param {string} source - Source text to translate
   * @returns {string|null} - Translation if found, null otherwise
   */
  retrieve(source) {
    const translation = this.memory.get(source);
    
    if (translation) {
      // Update access count
      const currentCount = this.accessCount.get(source) || 0;
      this.accessCount.set(source, currentCount + 1);
    }
    
    return translation;
  }

  /**
   * Find similar translations using string similarity
   * @param {string} source - Source text to find similar translations for
   * @param {number} threshold - Similarity threshold (0-1)
   * @returns {Array} - Array of similar translation pairs
   */
  findSimilar(source, threshold = 0.8) {
    const results = [];
    const sourceLower = source.toLowerCase();
    
    for (const [storedSource, target] of this.memory) {
      const similarity = this.calculateSimilarity(sourceLower, storedSource.toLowerCase());
      
      if (similarity >= threshold) {
        results.push({
          source: storedSource,
          target: target,
          similarity: similarity
        });
      }
    }
    
    // Sort by similarity (highest first)
    results.sort((a, b) => b.similarity - a.similarity);
    
    return results;
  }

  /**
   * Calculate string similarity using a simple algorithm
   * @param {string} str1 - First string
   * @param {string} str2 - Second string
   * @returns {number} - Similarity score between 0 and 1
   */
  calculateSimilarity(str1, str2) {
    // Simple similarity calculation (could be enhanced with more sophisticated algorithms)
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;
    
    if (longer.length === 0) {
      return 1.0;
    }
    
    const editDistance = this.levenshteinDistance(longer, shorter);
    return (longer.length - editDistance) / longer.length;
  }

  /**
   * Calculate Levenshtein distance between two strings
   * @param {string} str1 - First string
   * @param {string} str2 - Second string
   * @returns {number} - Edit distance
   */
  levenshteinDistance(str1, str2) {
    const matrix = Array(str2.length + 1).fill().map(() => Array(str1.length + 1).fill(0));
    
    for (let i = 0; i <= str1.length; i++) {
      matrix[0][i] = i;
    }
    
    for (let j = 0; j <= str2.length; j++) {
      matrix[j][0] = j;
    }
    
    for (let j = 1; j <= str2.length; j++) {
      for (let i = 1; i <= str1.length; i++) {
        const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
        matrix[j][i] = Math.min(
          matrix[j][i - 1] + 1,     // deletion
          matrix[j - 1][i] + 1,     // insertion
          matrix[j - 1][i - 1] + cost // substitution
        );
      }
    }
    
    return matrix[str2.length][str1.length];
  }

  /**
   * Get the size of the translation memory
   * @returns {number} - Number of stored translation pairs
   */
  getSize() {
    return this.memory.size;
  }

  /**
   * Get the total number of translations stored
   * @returns {number} - Total translation count
   */
  getTotalTranslations() {
    return this.totalTranslations;
  }

  /**
   * Clear the translation memory
   */
  clear() {
    this.memory.clear();
    this.accessCount.clear();
    this.totalTranslations = 0;
    console.log('Translation memory cleared');
  }
}

module.exports = TranslationMemory;
