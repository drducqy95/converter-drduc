/**
 * Sliding Context Manager
 * Manages contextual information across sentences and paragraphs for coherent translation
 */

class ContextManager {
  constructor(windowSize = 5) {
    this.windowSize = windowSize; // Number of sentences to keep in context
    this.contextWindow = []; // Sliding window of recent sentences
    this.characterTracking = new Map(); // Track characters mentioned in context
    this.entityTracking = new Map(); // Track entities and their references
    this.topicTracking = []; // Track current topics/discourse
  }

  /**
   * Add a sentence to the context window
   * @param {string} sentence - Sentence to add
   * @param {Object} metadata - Additional metadata about the sentence
   */
  addSentence(sentence, metadata = {}) {
    // Add to context window
    this.contextWindow.push({
      text: sentence,
      timestamp: Date.now(),
      metadata: metadata,
      id: this.generateId()
    });
    
    // Trim window if it exceeds size
    if (this.contextWindow.length > this.windowSize) {
      this.contextWindow.shift();
    }
    
    // Update character and entity tracking
    this.updateTracking(sentence, metadata);
    
    console.log(`Added sentence to context (window size: ${this.contextWindow.length})`);
  }

  /**
   * Update character and entity tracking based on sentence
   * @param {string} sentence - Sentence text
   * @param {Object} metadata - Metadata associated with sentence
   */
  updateTracking(sentence, metadata) {
    // This is where we would implement character/entity recognition
    // For this demo, we'll just track some sample entities
    
    // Example: Extract and track characters if they exist in metadata
    if (metadata.characters) {
      for (const character of metadata.characters) {
        const currentCount = this.characterTracking.get(character) || 0;
        this.characterTracking.set(character, currentCount + 1);
      }
    }
    
    // Example: Extract and track entities if they exist in metadata
    if (metadata.entities) {
      for (const entity of metadata.entities) {
        const currentCount = this.entityTracking.get(entity) || 0;
        this.entityTracking.set(entity, currentCount + 1);
      }
    }
    
    // Update topic tracking
    if (metadata.topic) {
      this.topicTracking.push(metadata.topic);
      if (this.topicTracking.length > this.windowSize) {
        this.topicTracking.shift();
      }
    }
  }

  /**
   * Get the current context window
   * @returns {Array} - Array of sentences in context window
   */
  getContextWindow() {
    return [...this.contextWindow];
  }

  /**
   * Get context for a specific sentence (surrounding sentences)
   * @param {number} position - Position of target sentence
   * @returns {Object} - Context object with before/after sentences
   */
  getSentenceContext(position = -1) {
    // If position is -1, use the most recent sentence
    if (position === -1) {
      position = this.contextWindow.length - 1;
    }
    
    const before = this.contextWindow.slice(Math.max(0, position - this.windowSize), position);
    const after = this.contextWindow.slice(position + 1, position + 1 + this.windowSize);
    const current = position >= 0 && position < this.contextWindow.length ? 
                   this.contextWindow[position] : null;
    
    return {
      before: before,
      current: current,
      after: after,
      characterTracking: this.getCharacterTracking(),
      entityTracking: this.getEntityTracking(),
      topicTracking: this.getTopicTracking()
    };
  }

  /**
   * Get tracked characters
   * @returns {Map} - Map of characters and their occurrence counts
   */
  getCharacterTracking() {
    return new Map(this.characterTracking);
  }

  /**
   * Get tracked entities
   * @returns {Map} - Map of entities and their occurrence counts
   */
  getEntityTracking() {
    return new Map(this.entityTracking);
  }

  /**
   * Get tracked topics
   * @returns {Array} - Array of recent topics
   */
  getTopicTracking() {
    return [...this.topicTracking];
  }

  /**
   * Generate a unique ID
   * @returns {string} - Unique identifier
   */
  generateId() {
    return `ctx_${Date.now()}_${Math.floor(Math.random() * 10000)}`;
  }

  /**
   * Clear the context window and tracking information
   */
  clear() {
    this.contextWindow = [];
    this.characterTracking.clear();
    this.entityTracking.clear();
    this.topicTracking = [];
    console.log('Context manager cleared');
  }

  /**
   * Serialize the context for storage
   * @returns {Object} - Serializable context object
   */
  serialize() {
    return {
      windowSize: this.windowSize,
      contextWindow: this.contextWindow,
      characterTracking: Array.from(this.characterTracking.entries()),
      entityTracking: Array.from(this.entityTracking.entries()),
      topicTracking: this.topicTracking
    };
  }

  /**
   * Deserialize context from stored data
   * @param {Object} data - Serialized context data
   */
  deserialize(data) {
    this.windowSize = data.windowSize;
    this.contextWindow = data.contextWindow;
    this.characterTracking = new Map(data.characterTracking);
    this.entityTracking = new Map(data.entityTracking);
    this.topicTracking = data.topicTracking;
    console.log('Context manager restored from serialized data');
  }
}

module.exports = ContextManager;
