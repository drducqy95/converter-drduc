/**
 * Structure Preserver Module
 * Handles preservation and restoration of non-text structures in documents
 */

class StructurePreserver {
  constructor() {
    this.placeholderPrefix = '__PLACEHOLDER_';
    this.placeholderCounter = 0;
    this.structureMap = new Map();
  }

  /**
   * Preserve non-text structures in the text by replacing them with placeholders
   * @param {string} text - Input text to process
   * @returns {Object} - Object containing processed text and structure map
   */
  preserve(text) {
    const result = {
      text: text,
      map: new Map()
    };

    // Define patterns for different types of structures to preserve
    const patterns = [
      // LaTeX formulas
      { type: 'latex', regex: /\$\$[\s\S]*?\$\$|\$.*?\$/g },
      // Code blocks
      { type: 'code', regex: /```[\s\S]*?```/g },
      // HTML tags
      { type: 'html', regex: /<[^>]+>/g },
      // Image links
      { type: 'image', regex: /!\[([^\]]*)\]\([^)]+\)/g },
      // Links
      { type: 'link', regex: /\[([^\]]+)\]\([^)]+\)/g }
    ];

    // Process each pattern
    for (const pattern of patterns) {
      result.text = result.text.replace(pattern.regex, (match) => {
        const placeholderId = `${this.placeholderPrefix}${pattern.type}_${this.placeholderCounter++}`;
        result.map.set(placeholderId, match);
        return placeholderId;
      });
    }

    return result;
  }

  /**
   * Restore preserved structures back to the text
   * @param {string} text - Text with placeholders
   * @param {Map} structureMap - Map of placeholders to original structures
   * @returns {string} - Text with structures restored
   */
  restore(text, structureMap) {
    let result = text;
    
    // Replace placeholders with original structures
    for (const [placeholder, original] of structureMap) {
      result = result.split(placeholder).join(original);
    }
    
    return result;
  }
}

module.exports = StructurePreserver;
