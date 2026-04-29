# **Kế Hoạch Triển Khai Hệ Thống Dịch Thuật Nâng Cao: Tiền Xử Lý, Cú Pháp và Học Tăng Cường**

## **1. Tổng Quan Dự Án**

### **1.1 Mục Tiêu Chính**
Xây dựng hệ thống dịch thuật Trung-Việt nâng cao dựa trên quy tắc và thống kê, không sử dụng LLM, với ba thành phần cốt lõi:
1. **Tiền xử lý hình thái và ngữ âm**: Quét, chuyển đổi Phồn thể sang Giản thể, Pinyin sang Giản thể
2. **Hệ thống quy tắc chuyển giao cú pháp**: Xử lý ngữ pháp Trung-Việt một cách linh hoạt
3. **Khả năng học tăng cường**: Tự hoàn thiện sau mỗi dự án

### **1.2 Nguyên Tắc Thiết Kế**
- Không sử dụng LLMs trong triển khai
- Tối ưu hiệu năng (dưới 5 giây cho 3000 từ)
- Tiêu tốn tài nguyên nhẹ (dưới 500MB RAM)
- Bảo toàn cấu trúc phi văn bản (công thức, mã lệnh)

---

## **2. Phân Hệ 1: Tiền Xử Lý Hình Thái và Ngữ Âm**

### **2.1 Mô-đun Quét và Bảo Vệ Cấu Trúc**
```
Files to create:
- src/preprocessor/structure_preserver.js
- src/preprocessor/placeholder_manager.js
- src/preprocessor/structure_restorer.js
```

**Implementation Steps:**
1. **Lexer Based Structure Detection**
   - Sử dụng biểu thức chính quy để phát hiện:
     - Công thức toán học (LaTeX, MathML)
     - Mã nguồn (giữa ```code```)
     - Thẻ HTML/XML
     - Liên kết hình ảnh
   - Trích xuất và lưu trữ trong hash table
   - Thay thế bằng placeholder duy nhất (UUID-based)

2. **Placeholder Management System**
   - Quản lý bảng băm ánh xạ placeholder ↔ dữ liệu gốc
   - Hỗ trợ lồng ghép (nested structures)
   - Cơ chế phục hồi cấu trúc chính xác

3. **Structure Restoration**
   - Ánh xạ ngược placeholder với dữ liệu gốc
   - Bảo toàn 100% cấu trúc phi văn bản
   - Kiểm thử với các định dạng phức tạp

### **2.2 Mô-đun Chuyển Đổi Phồn Thể Sang Giản Thể**
```
Files to create:
- src/preprocessor/traditional_to_simplified.js
- src/preprocessor/trie_converter.js
- src/preprocessor/dictionary_loader.js
```

**Implementation Steps:**
1. **Multi-Level Conversion Chain**
   - T2S: Chuyển đổi Phồn thể tiêu chuẩn sang Giản thể
   - TW2S: Phồn thể Đài Loan sang Giản thể
   - TW2SP: Phồn thể Đài Loan sang Giản thể + chuẩn hóa thuật ngữ Đại lục
   - HK2S: Phồn thể Hồng Kông sang Giản thể

2. **Double-Array Trie Implementation**
   - Xây dựng Marisa-Trie cho hiệu năng cao
   - Hỗ trợ đối sánh cụm từ (phrase-level) trước
   - Lùi về đối sánh ký tự (character-level) sau
   - Giải quyết vấn đề "một Giản thể đối đa Phồn thể"

3. **Regional Vocabulary Normalization**
   - Từ điển khu vực (Đại lục, Đài Loan, Hồng Kông)
   - Chuyển đổi thuật ngữ địa phương về chuẩn Đại lục
   - Ví dụ: 计算机 → 电脑 (Đài Loan) → 计算机 (Đại lục)

### **2.3 Mô-đun Phân Giải Pinyin sang Giản Thể**
```
Files to create:
- src/preprocessor/pinyin_processor.js
- src/preprocessor/hmm_viterbi_decoder.js
- src/preprocessor/ngram_language_model.js
- src/preprocessor/pinyin_lexicon.js
```

**Implementation Steps:**
1. **Hidden Markov Model Architecture**
   - Xác suất phát xạ (Emission Probabilities) từ từ điển Pinyin
   - Xác suất chuyển đổi (Transition Probabilities) từ N-gram model
   - Kỹ thuật làm trơn Kneser-Ney

2. **Viterbi Algorithm Implementation**
   - Duyệt không gian trạng thái (Lattice)
   - Tối ưu hóa cục bộ tại mỗi bước
   - Giữ lại đường đi có xác suất cao nhất
   - Con trỏ ngược (backpointer) cho truy xuất

3. **External Lexicon Integration**
   - Nút siêu cấp (super-nodes) cho thuật ngữ dự án
   - Trọng số xác suất ưu tiên tối đa
   - Đảm bảo tính toàn vẹn tên riêng

---

## **3. Phân Hệ 2: Hệ Thống Quy Tắc Chuyển Giao Cú Pháp**

### **3.1 Mô-đun Phân Tích Hình Thái và Cú Pháp**
```
Files to create:
- src/parser/morphological_analyzer.js
- src/parser/dependency_parser.js
- src/parser/tree_graph_builder.js
- src/parser/pos_tagger.js
```

**Implementation Steps:**
1. **Conditional Random Fields (CRF) Morphological Analyzer**
   - Nhận diện hình thức gốc (Lemma)
   - Gán nhãn từ loại (POS tagging)
   - Không sử dụng LLM, dựa trên mô hình thống kê

2. **Dependency Parsing Structure**
   - Tạo đồ thị cây (Tree Graph) hoặc đồ thị có hướng
   - Mỗi nút mang thuộc tính hình thái học
   - Mối quan hệ cú pháp (Subject, Modifier, Object)

3. **Graph-Based Rule Application**
   - Ánh xạ và biến đổi trực tiếp trên đồ hình
   - Không thao tác trên văn bản phẳng
   - Hỗ trợ mẫu tham số hóa {0} (LuatNhan)

### **3.2 Quy Tắc Đảo Ngữ và Phân Giải Hư Từ "的"**
```
Files to create:
- src/rules/syntax_transfer_rules.js
- src/rules/modifier_reordering.js
- src/rules/demonstrative_resolver.js
- src/rules/relative_clause_handler.js
```

**Implementation Steps:**
1. **Left-Branching vs Right-Branching Handling**
   - Phát hiện cấu trúc [Modifier] + 的 + [Head Noun]
   - Cô lập đồ thị phân tích
   - Bóc tách và hoán vị không gian

2. **Adjective-Head Reordering**
   - 贵的 + 东西 → đồ vật đắt tiền
   - Áp dụng phép nội suy phù hợp
   - Triệt tiêu hư từ "的" khỏi chuỗi tạo thành

3. **Possessive Pronoun Handling**
   - 你的 + 书 → sách của bạn
   - Chèn giới từ sở hữu tùy chọn
   - Dựa trên phân tích POS

4. **Relative Clause Processing**
   - 我昨天买的 + 书 → cuốn sách mà tôi mua hôm qua
   - Cơ cấu bao bọc tạo thành [noun] + [mà/được] + [clause]

### **3.3 Quy Tắc Tái Định Vị Trạng Ngữ và Giới Từ**
```
Files to create:
- src/rules/adverbial_repositioning.js
- src/rules/spatial_shifting.js
- src/rules/instrumental_modifier.js
- src/rules/locative_handling.js
```

**Implementation Steps:**
1. **Locative Phrase Recognition**
   - Nhận diện giới từ (在, 用, 跟) và bổ ngữ đi kèm
   - Tạo khối phân vùng (dependency chunk)
   - Gán nhãn cụ thể cho các thành phần

2. **Spatial Movement Rules**
   - Tìm kiếm động từ hạt nhân và tân ngữ
   - Cắt toàn bộ khối trạng ngữ
   - Gắn kết vào vị trí rightmost leaf node sau cụm động-tân

3. **Cross-Index Condition Checking**
   - Bảo toàn nghĩa mà vẫn tuân thủ văn phong bản địa
   - Hàm logic điều kiện kiểm tra chỉ mục vị trí chéo

### **3.4 Quy Tắc Chuyển Giao Bổ Ngữ Phức Hợp**
```
Files to create:
- src/rules/complement_transfers.js
- src/rules/resultative_complement.js
- src/rules/potential_complement.js
- src/rules/directional_complement.js
```

**Implementation Steps:**
1. **Resultative Complement Handling**
   - Ánh xạ "没" thành trợ từ phủ định
   - Neo vị trí trước động từ chính
   - Duy trì tính từ kết quả sau động từ

2. **Potential Complement Processing**
   - Nhận dạng chuỗi [V] + 得/不 + [C]
   - Triệt tiêu "得" hoặc "不"
   - Chuyển hóa thành trợ từ năng nguyện tiếng Việt
   - Đảo vị trí thành: [V] + (không) + [Result] + (được)

3. **Directional Complement Aggregation**
   - Gom tụ các từ tố bị chẻ đôi (上 và 来)
   - Tái cấu trúc thành cụm động từ xu hướng hoàn chỉnh
   - Đặt sau động từ di chuyển trong tiếng Việt

### **3.5 Quy Tắc Xử Lý Động Từ Ly Hợp và Thể Bị Động**
```
Files to create:
- src/rules/separable_verb_handler.js
- src/rules/passive_voice_converter.js
- src/rules/polarity_analyzer.js
- src/rules/agentless_passive.js
```

**Implementation Steps:**
1. **Separable Verb Recognition**
   - Phát hiện hai từ tố hạt nhân nằm cách xa nhau
   - Chia sẻ gốc từ vựng (帮 và 忙)
   - Trích xuất thành phần bị kẹp ở giữa

2. **Re-arrangement Algorithm**
   - Tái hợp từ ly hợp thành chỉnh thể ngữ nghĩa
   - Tái bố trí thành tân ngữ hoặc trạng ngữ thời gian
   - Ví dụ: 帮了他三个月的忙 → giúp đỡ hắn trong ba tháng

3. **Passive Voice Polarity Analysis**
   - Mô-đun cảm nhận từ vựng (Emotion-aware heuristic)
   - Ma trận nội hàm 4D phân tích cực cảm xúc
   - Ánh xạ "被" thành "được" (tích cực) hoặc "bị" (tiêu cực)

---

## **4. Phân Hệ 3: Năng Lực Học Tăng Cường và Tiến Hóa**

### **4.1 Bộ Nhớ Dịch Thuật Gia Tăng**
```
Files to create:
- src/learning/translation_memory.js
- src/learning/suffix_array_storage.js
- src/learning/edit_distance_calculator.js
- src/learning/on_the_fly_scoring.js
```

**Implementation Steps:**
1. **Dual Output System**
   - Phiên bản MD sạch cho người đọc cuối (output/)
   - Phiên bản nháp có gán nhãn cho biên tập viên (drafts/)

2. **Dynamic Suffix Array Implementation**
   - Lưu trữ trên RAM (Memory-mapped dynamic suffix arrays)
   - Lấy cảm hứng từ kiến trúc Moses SMT
   - Tránh huấn luyện lại toàn bộ mô hình

3. **Real-time Weight Calculation**
   - Nối thêm cặp câu mới vào tập dữ liệu nền
   - Tính toán lại trọng số và xác suất điều kiện ngay lập tức
   - Áp dụng tức thì cho các chương tiếp theo

### **4.2 Thuật Toán Quy Nạp Quy Tắc Tự Động**
```
Files to create:
- src/learning/rule_induction_engine.js
- src/learning/word_alignment.js
- src/learning/error_driven_discovery.js
- src/learning/pos_generalization.js
```

**Implementation Steps:**
1. **Word Alignment Algorithm**
   - Sử dụng mô hình HMM kết hợp thuật toán GIZA++
   - Ánh xạ từ tiếng Trung với từ tiếng Việt đã hậu biên tập
   - Phát hiện điểm dị biệt về vị trí ("chéo từ")

2. **POS-Based Template Generation**
   - Nội suy các thẻ từ loại tương ứng
   - Phát sinh mẫu ngữ pháp trừu tượng (Adj + Noun → Noun + Adj)
   - Tăng khả năng áp dụng cho ngữ cảnh tương đồng

3. **Syntax Tree Analysis**
   - Ánh xạ cấu trúc cây phân tích
   - Nhận diện ranh giới khối cụm từ (chunk boundaries)
   - Biên dịch thành hàm XML hoặc tập tin JSON cấu trúc

### **4.3 Khả Năng Thích Nghi Ngữ Cảnh**
```
Files to create:
- src/learning/context_adaptation.js
- src/learning/domain_classifier.js
- src/learning/provenance_tracker.js
- src/learning/cultural_origin_detector.js
```

**Implementation Steps:**
1. **Hierarchical Domain Adaptation**
   - Theo dõi nguồn gốc dữ liệu mới
   - Phân loại theo thể loại, tác giả, bối cảnh văn hóa
   - Đẩy trọng số cao nhất trong không gian ngữ cảnh tương ứng

2. **Cross-Genre Contamination Prevention**
   - Ngăn chặn sự ô nhiễm chéo giữa các miền văn bản
   - Duy trì tính đa dụng của hệ thống
   - Ví dụ: "đạo hữu" chỉ ưu tiên trong văn học Tu tiên

3. **Pinyin Model Evolution**
   - Điều chỉnh tần suất xuất hiện N-gram
   - Tính toán lại ma trận phát xạ và chuyển trạng thái
   - Chèn thuật ngữ mới vào từ điển cốt lõi

### **4.4 Trình Quản Lý Ngữ Cảnh Trượt**
```
Files to create:
- src/learning/sliding_context_manager.js
- src/learning/character_tracking.js
- src/learning/storyline_comprehension.js
- src/learning/memory_accumulator.js
```

**Implementation Steps:**
1. **Sliding Window Mechanism**
   - Quét 5 câu trước và 5 câu sau điểm neo hiện tại
   - Lưu trữ danh sách nhân vật đang tham gia cảnh
   - Ghi nhớ tùy chỉnh nhân xưng đặc biệt

2. **Structured Memory Accumulation**
   - Lược sử bối cảnh mã hóa vượt ranh giới chương
   - Tự hoàn thiện theo thời gian
   - Giảm tỷ lệ dịch sai đại từ, nhầm lẫn danh từ riêng

---

## **5. Giai Đoạn Triển Khai**

### **Giai đoạn 1: Thiết lập nền tảng (Week 1-2)**
- [ ] Thiết lập cấu trúc thư mục
- [ ] Cài đặt thư viện phụ trợ (trie, hmm, crf)
- [ ] Xây dựng framework cơ bản
- [ ] Tạo hệ thống logging và monitoring

### **Giai đoạn 2: Tiền xử lý (Week 3-4)**
- [ ] Triển khai lexer và structure preserver
- [ ] Xây dựng trie converter cho Phồn thể
- [ ] Phát triển HMM-Viterbi cho Pinyin
- [ ] Tích hợp từ điển đa cấp

### **Giai đoạn 3: Phân tích cú pháp (Week 5-6)**
- [ ] Triển khai morphological analyzer
- [ ] Xây dựng dependency parser
- [ ] Phát triển tree graph builder
- [ ] Tích hợp POS tagger

### **Giai đoạn 4: Quy tắc chuyển giao (Week 7-8)**
- [ ] Xây dựng syntax transfer rules
- [ ] Triển khai modifier reordering
- [ ] Phát triển complement handlers
- [ ] Tích hợp separable verb processing

### **Giai đoạn 5: Học tăng cường (Week 9-10)**
- [ ] Triển khai translation memory
- [ ] Xây dựng rule induction engine
- [ ] Phát triển context manager
- [ ] Tích hợp domain adaptation

### **Giai đoạn 6: Tích hợp và kiểm thử (Week 11-12)**
- [ ] Tích hợp toàn bộ module
- [ ] Kiểm thử hiệu năng (speed, memory)
- [ ] Kiểm thử độ chính xác (accuracy)
- [ ] Tối ưu hóa cuối cùng

---

## **6. Kế Hoạch Kiểm Thử**

### **Kiểm Thử Hiệu Năng**
- [ ] Thời gian xử lý < 5 giây cho 3000 từ
- [ ] Bộ nhớ tiêu thụ < 500MB
- [ ] Bảo toàn 100% cấu trúc phi văn bản

### **Kiểm Thử Độ Chính Xác**
- [ ] So sánh với bản dịch thủ công
- [ ] Đánh giá chất lượng BLEU, METEOR
- [ ] Kiểm thử với văn bản đa thể loại

### **Kiểm Thử Học Tăng Cường**
- [ ] Khả năng tự cập nhật sau mỗi dự án
- [ ] Tăng độ chính xác theo thời gian
- [ ] Ngăn chặn "catastrophic forgetting"

---

## **7. Tài Nguyên Và Công Cụ**

### **Thư Viện Phụ Trợ**
- **Trie Implementation**: marisa-trie, double-array trie
- **HMM-Viterbi**: custom implementation
- **CRF**: sklearn-crfsuite hoặc tương đương
- **N-gram**: kenlm hoặc tương đương

### **Từ Điển Và Mô Hình**
- **OpenCC dictionaries**: t2s.json, tw2s.json, tw2sp.json, hk2s.json
- **Pinyin lexicon**: từ điển âm tiết và ánh xạ ngữ âm
- **POS tagset**: từ điển từ loại Trung-Việt
- **Translation rules**: mẫu cú pháp chuyển giao

### **Công Cụ Phát Triển**
- **IDE**: VS Code với extension hỗ trợ
- **Version Control**: Git
- **Testing Framework**: Jest hoặc Mocha
- **Performance Profiler**: Node.js profiler

---

## **8. Kết Luận**

Kế hoạch này cung cấp lộ trình chi tiết để xây dựng hệ thống dịch thuật Trung-Việt nâng cao dựa trên quy tắc và thống kê, không sử dụng LLM. Với ba phân hệ cốt lõi (tiền xử lý, quy tắc cú pháp, học tăng cường), hệ thống sẽ đạt được hiệu năng cao, độ chính xác tốt và khả năng tự hoàn thiện theo thời gian. Việc triển khai theo từng giai đoạn giúp kiểm soát chất lượng và tiến độ một cách hiệu quả.
