/**
 * Traditional to Simplified Chinese Converter
 * Uses OpenCC dictionaries for conversion with multi-level support
 */

// Mock dictionary data for demonstration
const conversionDicts = {
  // Standard Traditional to Simplified
  t2s: new Map([
    ['國', '国'],
    ['學', '学'], 
    ['轉', '转'],
    ['換', '换'],
    ['體', '体'],
    ['簡', '简'],
    ['繁', '繁']
  ]),
  
  // Taiwan variant to Simplified
  tw2s: new Map([
    ['電腦', '电脑'],
    ['軟體', '软件'],
    ['硬體', '硬件']
  ]),
  
  // Hong Kong variant to Simplified
  hk2s: new Map([
    ['軟體', '软件'] // Same as Taiwan in this case
  ])
};

class TraditionalToSimplified {
  constructor() {
    this.dicts = conversionDicts;
  }

  /**
   * Convert Traditional Chinese to Simplified Chinese
   * @param {string} text - Input text in Traditional Chinese
   * @returns {string} - Converted text in Simplified Chinese
   */
  convert(text) {
    // For this implementation, we'll use a simple character-by-character conversion
    // In a real implementation, this would use a Trie structure for phrase-level matching
    
    let result = text;
    
    // Apply each conversion dictionary
    for (const [key, dict] of Object.entries(this.dicts)) {
      result = this.applyDictionary(result, dict);
    }
    
    return result;
  }
  
  /**
   * Apply a conversion dictionary to text
   * @param {string} text - Input text
   * @param {Map} dict - Conversion dictionary
   * @returns {string} - Converted text
   */
  applyDictionary(text, dict) {
    let result = text;
    
    // Sort entries by length (descending) to handle longer phrases first
    const sortedEntries = Array.from(dict.entries()).sort((a, b) => b[0].length - a[0].length);
    
    for (const [from, to] of sortedEntries) {
      result = result.replaceAll(from, to);
    }
    
    return result;
  }
}

module.exports = TraditionalToSimplified;
