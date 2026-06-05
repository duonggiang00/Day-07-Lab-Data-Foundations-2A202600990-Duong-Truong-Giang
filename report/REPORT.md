# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Dương Trường Giang
**Nhóm:** Chill Guys
**Ngày:** 06/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity nghĩa là hai vector biểu diễn văn bản hướng về cùng một phía trong không gian đa chiều, cho thấy hai văn bản đó có sự tương đồng lớn về mặt ngữ nghĩa (semantic meaning) và ngữ cảnh, bất chấp độ dài hay từ ngữ sử dụng có khác nhau.

**Ví dụ HIGH similarity:**
- Sentence A: Trí tuệ nhân tạo đang làm thay đổi sâu sắc cách vận hành của các ngành công nghiệp hiện đại.
- Sentence B: AI đang tạo ra những bước chuyển mình mạnh mẽ trong hoạt động sản xuất kinh doanh toàn cầu.
- Tại sao tương đồng: Cả hai câu đều nói về tác động to lớn của trí tuệ nhân tạo (AI) lên các lĩnh vực công nghiệp/kinh doanh, dù từ vựng sử dụng không giống nhau hoàn toàn nhưng ngữ nghĩa tương đương.

**Ví dụ LOW similarity:**
- Sentence A: Trái Đất quay quanh Mặt Trời theo quỹ đạo hình elip gần tròn.
- Sentence B: Món phở bò Hà Nội cần có nước dùng trong, thơm mùi quế hồi và gừng nướng.
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác nhau (thiên văn học và ẩm thực Việt Nam), không có mối liên hệ ngữ nghĩa nào.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Euclidean distance đo khoảng cách đường thẳng giữa hai điểm, dễ bị ảnh hưởng bởi độ dài văn bản (văn bản dài hơn có vector lớn hơn). Cosine similarity chỉ đo góc giữa hai vector nên không phụ thuộc vào độ dài văn bản, giúp so sánh chính xác độ tương đồng ngữ nghĩa của các tài liệu ngắn dài khác nhau.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> Áp dụng công thức: `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))`
> Ta có: `num_chunks = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11)`
> *Đáp án:* 23 chunks

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap tăng lên 100, số lượng chunks sẽ tăng lên thành 25 chunks (phép tính: `ceil((10000-100)/(500-100)) = ceil(9900/400) = ceil(24.75) = 25`). Ta muốn nhiều overlap hơn để tránh mất mát ngữ cảnh ở vùng biên giữa các chunk, đảm bảo thông tin liên tục và đầy đủ khi truy xuất trong hệ thống RAG.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Hướng dẫn giả lập Robot trên Gazebo và đặc tả SDF (Simulation Description Format).

**Tại sao nhóm chọn domain này?**
> Nhóm chọn domain này để xây dựng một trợ lý ảo hỗ trợ kỹ thuật cho việc lập trình và thiết lập mô phỏng robot. Tài liệu chứa nhiều hướng dẫn thực tế từ cơ bản (giao diện GUI, phím tắt) đến nâng cao (nạp cảm biến, cấu hình thế giới SDF, thiết lập Actor di động) giúp tối ưu hóa khả năng truy xuất RAG trong kỹ thuật.

### Data Inventory

| #  | Tên tài liệu               | Nguồn       | Số ký tự | Metadata đã gán                                           |
| -- | -------------------------- | ----------- | -------- | --------------------------------------------------------- |
| 1  | building_robot.md          | Gazebo Docs | 15,523   | category: robot_modeling, interface: sdf_code             |
| 2  | moving_robot.md            | Gazebo Docs | 7,982    | category: robot_control, interface: terminal_and_gui      |
| 3  | sensors.md                 | Gazebo Docs | 15,503   | category: robot_sensing, interface: sdf_code_and_terminal |
| 4  | GUI_tutorial.md            | Gazebo Docs | 6,614    | category: gui_basics, interface: gui                      |
| 5  | actors.md                  | Gazebo Docs | 7,808    | category: animation, interface: sdf_code                  |
| 6  | hotkeys.md                 | Gazebo Docs | 1,726    | category: gui_shortcuts, interface: gui_keyboard          |
| 7  | Manipulating_models.md     | Gazebo Docs | 7,593    | category: gui_model_manipulation, interface: gui          |
| 8  | Model_insertion_fuel.md    | Gazebo Docs | 3,952    | category: model_insertion, interface: gui_or_sdf          |
| 9  | sdf_worlds.md              | Gazebo Docs | 11,840   | category: world_building, interface: sdf_code             |
| 10 | spawn_urdf.md              | Gazebo Docs | 3,321    | category: model_spawning, interface: terminal_service     |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `category` | `str` | `"robot_modeling"`, `"robot_control"`, `"robot_sensing"`, `"gui_basics"`, `"animation"`, `"gui_shortcuts"`, `"gui_model_manipulation"`, `"model_insertion"`, `"world_building"`, `"model_spawning"` | Phân loại tài liệu theo phân hệ chức năng cụ thể của robot hoặc môi trường giả lập để nhanh chóng định tuyến và loại bỏ các tài liệu không liên quan. |
| `interface` | `str` | `"sdf_code"`, `"terminal_and_gui"`, `"sdf_code_and_terminal"`, `"gui"`, `"gui_keyboard"`, `"gui_or_sdf"`, `"terminal_service"` | Xác định phương thức tương tác chính trong tài liệu (giao diện đồ họa GUI, dòng lệnh Terminal hay viết mã SDF), giúp truy xuất đúng định dạng thông tin mà người dùng muốn thực hiện. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| `GUI_tutorial.md` | FixedSizeChunker (`fixed_size`) | 37 | 198.22 | Không (cắt cơ học, dễ chia đôi từ/câu) |
| `GUI_tutorial.md` | SentenceChunker (`by_sentences`) | 14 | 471.07 | Có (giữ nguyên câu, nhưng chunk hơi to) |
| `GUI_tutorial.md` | RecursiveChunker (`recursive`) | 41 | 159.68 | Tốt nhất (giữ nguyên cấu trúc markdown/đoạn) |
| `spawn_urdf.md` | FixedSizeChunker (`fixed_size`) | 19 | 193.74 | Không (dễ ngắt ngang dòng lệnh XML/URDF) |
| `spawn_urdf.md` | SentenceChunker (`by_sentences`) | 6 | 552.33 | Khá (giữ câu nhưng mất cấu trúc XML block) |
| `spawn_urdf.md` | RecursiveChunker (`recursive`) | 21 | 156.67 | Tốt (không ngắt vụn thẻ URDF) |
| `hotkeys.md` | FixedSizeChunker (`fixed_size`) | 10 | 190.60 | Không (cắt đôi các dòng mô tả phím tắt) |
| `hotkeys.md` | SentenceChunker (`by_sentences`) | 1 | 1725.00 | Tệ nhất (do phím tắt ít dấu chấm nên gộp thành 1 chunk khổng lồ) |
| `hotkeys.md` | RecursiveChunker (`recursive`) | 12 | 141.50 | Tốt nhất (chia nhỏ theo dòng phím tắt một cách tự nhiên) |

### Strategy Của Tôi

**Loại:** FixedSizeChunker (`fixed_size`) với `chunk_size = 500` và `overlap = 50`

**Mô tả cách hoạt động:**
> Chunker này hoạt động bằng cách cắt văn bản thành các đoạn nhỏ (chunk) đều đặn có kích thước cố định bằng 500 ký tự. Để tránh bị mất ngữ cảnh tại các điểm cắt ranh giới giữa hai chunk kế tiếp, thuật toán cấu hình một khoảng trùng lặp (overlap) bằng 50 ký tự dùng chung giữa chúng.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Đây là chiến lược đơn giản, dễ triển khai và cho kích thước chunk cực kỳ đồng đều, giúp LLM dễ xử lý khi nhận ngữ cảnh có cùng dung lượng. Nó giúp giữ được lượng thông tin bao quát lớn trong mỗi chunk, thích hợp cho các câu hỏi tổng hợp ở mức độ rộng.

**Code snippet (nếu custom):**
*Sử dụng FixedSizeChunker mặc định từ mã nguồn của dự án.*

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| `hotkeys.md` | best baseline (recursive 200) | 12 | 141.50 | Tốt hơn (chia nhỏ theo dòng phím tắt một cách tự nhiên) |
| `hotkeys.md` | **của tôi** (fixed_size 500) | 4 | 469.00 | Khá tốt (kích thước chunk lớn giúp gom nhiều phím tắt cùng lúc, nhưng vẫn bị nguy cơ cắt đôi dòng phím tắt ở ranh giới) |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | FixedSize (500) | 6/10 | Bao quát rộng, kích thước đồng đều | Dễ cắt ngang code XML hoặc dòng phím tắt |
| Nguyễn Việt Hoàng Lương | CustomChunker | 9/10 | Giữ cấu trúc code tốt, trọn vẹn ngữ cảnh của từng Mục | Nếu một mục quá dài vẫn phải dựa vào đệ quy chia nhỏ |
| Trần Công Minh | RecursiveChunker | 9/10 | Giữ cấu trúc code tốt | Đôi khi tạo chunk nhỏ lắt nhắt |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Chiến lược `CustomChunker` (của Nguyễn Việt Hoàng Lương) và `RecursiveChunker` (của Trần Công Minh) là tốt nhất cho domain này. Bởi vì đặc thù tài liệu mô phỏng kỹ thuật chứa nhiều danh sách phím tắt và mã XML/SDF, việc chia theo mục nội dung hoặc chia đệ quy tôn trọng dấu xuống dòng (`\n`) giúp duy trì tính toàn vẹn của mã lệnh và danh sách phím tắt tốt hơn hẳn so với việc chia cơ học theo ký tự (FixedSize) của tôi.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`FixedSizeChunker.chunk` (Chiến thuật cá nhân tôi chọn)** — approach:
> Thuật toán duyệt qua toàn bộ văn bản bằng một vòng lặp `for` với bước nhảy cố định (`step = chunk_size - overlap`). Tại mỗi bước nhảy, thuật toán trích xuất một phân đoạn (slice) văn bản có độ dài bằng `chunk_size`. Cơ chế này đảm bảo có một vùng đệm (overlap) có kích thước cố định được chia sẻ giữa các chunk liên tiếp nhằm tránh thất thoát thông tin ngữ nghĩa tại các điểm cắt ranh giới. Nếu văn bản gốc ngắn hơn `chunk_size`, toàn bộ văn bản sẽ được giữ nguyên trong một chunk duy nhất.

**`SentenceChunker.chunk`** — approach:
> Sử dụng biểu thức chính quy (Regex) dạng lookbehind `(?<=\. |! |\? |\.\n)` để phân tách văn bản thành các câu riêng biệt mà không làm mất các ký hiệu phân cách câu ở cuối. Thuật toán loại bỏ các câu rỗng/chỉ chứa khoảng trắng, gộp các câu liên tiếp theo cụm `max_sentences_per_chunk` rồi tiến hành `strip()` loại bỏ khoảng trắng dư thừa ở đầu và cuối trước khi thêm vào danh sách chunk kết quả.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Sử dụng thuật toán đệ quy duyệt qua các ký tự phân tách theo thứ tự ưu tiên (`\n\n`, `\n`, `. `, ` `, `""`). Base case là khi đoạn văn bản hiện tại có độ dài nhỏ hơn hoặc bằng `chunk_size` thì dừng chia. Nếu đoạn văn bản vượt quá kích thước và hết danh sách phân tách, thuật toán sẽ chia nhỏ cố định theo số lượng ký tự. Các phần tử con sau khi chia nhỏ nếu vẫn lớn hơn `chunk_size` sẽ được đệ quy chia tiếp, sau đó gộp lại bằng hàm `_merge_splits` để tối ưu hóa độ dài của mỗi chunk không vượt quá `chunk_size`.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Thực hiện chuyển đổi các `Document` thành bản ghi lưu trữ có cấu trúc dưới dạng dictionary chứa `id`, `content`, `embedding` (tạo từ `embedding_fn`) và `metadata` rồi thêm vào list `self._store` trong RAM, đồng thời đồng bộ lưu vào collection của ChromaDB nếu có sẵn. Khi `search`, vector câu hỏi sẽ được nhân vô hướng và chia cho tích độ dài (tính Cosine Similarity) với vector của tất cả các bản ghi có trong store, sau đó sắp xếp theo độ tương đồng giảm dần và lấy ra top_k kết quả.

**`search_with_filter` + `delete_document`** — approach:
> Phương thức `search_with_filter` áp dụng cơ chế tiền lọc (pre-filtering), duyệt qua danh sách lưu trữ để giữ lại các bản ghi khớp với tất cả các cặp key-value trong `metadata_filter`, sau đó mới thực hiện tìm kiếm tương đồng trên tập con này. `delete_document` thực hiện lọc bỏ các phần tử khỏi `self._store` nếu có `id` hoặc `metadata['doc_id']` khớp với `doc_id` yêu cầu, đồng thời gọi lệnh xóa tương ứng trên ChromaDB và trả về trạng thái có bản ghi nào bị xóa hay không.

### KnowledgeBaseAgent

**`answer`** — approach:
> Gọi phương thức `search` từ `EmbeddingStore` để truy xuất top-k chunk liên quan nhất đến câu hỏi. Các chunk này được chuẩn hóa và ghép lại kèm theo nhãn đánh dấu nguồn (ví dụ: `[Source 1]`, `[Source 2]`) tạo thành phần ngữ cảnh (context), sau đó chèn vào cấu trúc prompt mẫu hướng dẫn LLM chỉ trả lời dựa trên ngữ cảnh này trước khi gọi hàm `llm_fn`.

### Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0 -- python.exe
cachedir: .pytest_cache
rootdir: .
plugins: anyio-4.13.0, langsmith-0.8.8
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.10s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Trí tuệ nhân tạo đang phát triển rất nhanh. | Công nghệ AI đang tiến bộ với tốc độ chóng mặt. | High | -0.2865 | Sai |
| 2 | Học máy là một nhánh của trí tuệ nhân tạo. | Machine learning là một lĩnh vực con của AI. | High | -0.0780 | Sai |
| 3 | Hôm nay tôi ăn cơm gà. | Ngày mai trời có thể mưa. | Low | 0.0110 | Đúng |
| 4 | Quy trình thiết kế robot gồm nhiều bước phức tạp. | Để lập trình robot, bạn cần cài đặt ROS và Gazebo. | Low | 0.1328 | Đúng |
| 5 | Tôi thích chơi bóng đá vào cuối tuần. | Bóng đá là môn thể thao tôi yêu thích nhất. | High | -0.0241 | Sai |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Kết quả bất ngờ nhất là các câu đồng nghĩa hoàn toàn (như Cặp 1 và Cặp 2) lại có điểm tương đồng rất thấp hoặc âm, trong khi các câu không liên quan lại có điểm gần 0. Điều này chứng minh rằng `MockEmbedder` chỉ băm ký tự bằng MD5 để tạo vector ngẫu nhiên nên không hề biểu diễn được ngữ nghĩa thực sự. Trong các mô hình thật, embeddings sẽ học được các mối liên hệ ngữ nghĩa để đặt các từ đồng nghĩa gần nhau trong không gian vector và cho điểm cao.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | What is an SDF file and how do I use it to build a robot? | SDFormat (SDF) is an XML format that describes objects and environments for robot simulators. To build a robot, we define a `<model>` tag with a name, and inside we define `<link>` tags for physical bodies (such as chassis and wheels) and `<joint>` tags to connect those links together. |
| 2 | How do I make my robot move forward using the differential drive? | You set up the `diff_drive` plugin (using `<plugin filename="gz-sim-diff-drive-system" name="gz::sim::systems::DiffDrive">`) within the robot model. Then, send velocity commands of type `gz.msgs.Twist` to the input topic (default `cmd_vel`), specifying a positive linear speed for the x-axis (e.g. `x: 0.5`). |
| 3 | Can I simulate a Lidar or a Depth Camera to map the world? | Yes, you can simulate a Lidar sensor by adding the `Sensors` plugin (filename `gz-sim-sensors-system`, name `gz::sim::systems::Sensors`) under the `<world>` tag. Then, define a `<sensor>` of type `gpu_lidar` inside a model's link, setting up parameters like `<pose>`, `<topic>`, `<update_rate>`, `<ray>` and `<range>`. |
| 4 | Is there a quick way to scale or rotate an object without clicking the menu? | Yes, you can use keyboard shortcuts. To translate or rotate in customizable increments, hold `Ctrl` while dragging. To scale an object, press the `S` hotkey to activate the scale tool, and press `R` to activate the rotation tool. |
| 5 | Why doesn't my human actor collide with the walls in the simulation? | In Gazebo Sim, an `actor` is designed for scripted animations (e.g. walking paths) and does not participate in the physics engine's collision calculations by default. They lack collision detection and can pass through solid models like walls. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What is an SDF file and... | create --reqtype gz.msgs.EntityFactory ... 'sdf_filename: "/path/to/model.urd... | 0.3454 | No | [DEMO LLM] Generated answer... |
| 2 | How do I make my robot move... | <property type="string" key="state">floating</property> <anchors target="3D View">... | 0.3287 | No | [DEMO LLM] Generated answer... |
| 3 | Can I simulate a Lidar... | s` The message should look like this: ![world_shapes_stats]... ### Entity tree... | 0.2961 | No | [DEMO LLM] Generated answer... |
| 4 | Is there a quick way to scale... | ows: ```xml <sensor name='gpu_lidar' type='gpu_lidar'>" <pose relative_to='lidar_frame'>0 0 0 0 0 0</pose>... | 0.3418 | No | [DEMO LLM] Generated answer... |
| 5 | Why doesn't my human actor... | # Spawn URDF This tutorial will cover how to spawn a URDF model in Gazebo Sim... | 0.3762 | No | [DEMO LLM] Generated answer... |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 0 / 5

> *Giải thích:* Do chạy thử nghiệm cá nhân sử dụng chiến thuật `FixedSizeChunker (chunk_size=500, overlap=50)` cùng backend `MockEmbedder` băm MD5 ngẫu nhiên, các vector đặc trưng không thể hiện được ngữ nghĩa thực tế. Kết quả là toàn bộ 5 truy vấn đều trả về các chunk không liên quan (0/5 câu đúng trong top-3). Nếu tích hợp mô hình embedding ngữ nghĩa thực sự (như OpenAI hoặc Local MiniLM), kết quả truy xuất chắc chắn sẽ đạt độ chính xác cao nhờ khả năng khớp ngữ nghĩa thực tế.

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Tôi học được cách các thành viên thiết lập các trường metadata có tính bao quát cao và cách họ phân loại các mức độ bài viết (difficulty) một cách khoa học để tối ưu hóa bộ lọc.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Nhóm bạn đã có ý tưởng cực kỳ hay khi viết các bộ parser/chunker tùy biến riêng để bóc tách tệp XML/SDF theo cấu trúc cây thẻ cha-con thay vì chỉ dùng ngắt dòng văn bản thông thường, giúp tăng độ chính xác tìm kiếm vượt bậc.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Tôi sẽ thiết kế một custom chunker chuyên dụng cho các file code mô phỏng (.sdf, .urdf) để đảm bảo không một khối mã XML nào bị chia cắt nửa chừng, từ đó đảm bảo RAG cung cấp ngữ cảnh nguyên vẹn cho LLM.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 15 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 10 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **100 / 100** |
