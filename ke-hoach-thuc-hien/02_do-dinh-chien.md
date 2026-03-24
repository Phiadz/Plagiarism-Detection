# Kế Hoạch Thực Hiện — Đỗ Đình Chiến (MSSV: 51205005553)

**Vai trò:** Cài đặt thuật toán Tham lam (Greedy) · Cài đặt thuật toán Quay lui Nhánh Cận (Branch and Bound)

---

## 1. Tổng Quan Nhiệm Vụ

Đỗ Đình Chiến chịu trách nhiệm triển khai **hai trong ba thuật toán** cốt lõi của dự án:

1. **Thuật toán Tham lam (Greedy)** – nhanh nhất, không đảm bảo tối ưu.
2. **Thuật toán Quay lui Nhánh Cận (Branch and Bound – B&B)** – chậm hơn Greedy nhưng đảm bảo kết quả tối ưu tuyệt đối như DP.

Cả hai thuật toán đều nằm trong thư mục `algorithms/` và phải tuân thủ giao diện lập trình (API) chung do Lê Thiên Lộc thiết kế.

---

## 2. Thuật Toán Tham Lam (Greedy)

### 2.1 Nguyên Lý

Tính **tỷ lệ hiệu quả** cho từng trang bị: `ratio = power / gold`

Sắp xếp danh sách trang bị theo `ratio` giảm dần, sau đó tham lam chọn trang bị từ cao xuống thấp, miễn là còn đủ Vàng.

### 2.2 Kế Hoạch Cài Đặt (`algorithms/greedy.py`)

**Bước 1 – Tính tỷ lệ:**
- Duyệt qua toàn bộ `items`, tính `item.ratio()` cho từng phần tử.

**Bước 2 – Sắp xếp:**
- Sắp xếp bản sao của danh sách theo `ratio` giảm dần.
- **Quan trọng:** Sắp xếp trên bản sao (không sửa danh sách gốc) để không ảnh hưởng đến các thuật toán khác.

**Bước 3 – Vòng lặp tham lam:**
- Duyệt qua danh sách đã sắp xếp.
- Nếu `item.gold <= gold_remaining` → chọn trang bị đó, trừ vàng còn lại.
- Nếu không đủ vàng → bỏ qua (không quay lại).

**Bước 4 – Tổng hợp và trả về kết quả:**
- Tính tổng `power` và tổng `gold` của các trang bị đã chọn.
- Bao bọc trong `time.perf_counter()` để đo thời gian.

### 2.3 Ví Dụ Minh Họa

| Trang bị | Gold | Power | Ratio |
|---|---|---|---|
| Vô Cực Kiếm | 3400 | 85 | 0.025 |
| Đoản Kiếm | 350 | 10 | 0.029 |
| Giáp Máu | 2900 | 70 | 0.024 |
| Mũ Phù Thủy | 3100 | 90 | 0.029 |

Với W = 4000 Gold, Greedy sắp xếp theo ratio và chọn: Đoản Kiếm (350) + Mũ Phù Thủy (3100) = 3450 Gold, Power = 100. DP có thể tìm ra kết quả khác tốt hơn trong trường hợp tổng quát.

### 2.4 Giới Hạn Đã Biết

- Greedy có thể **bỏ lỡ tổ hợp tối ưu** khi các trang bị có `ratio` tương đương nhau nhưng kết hợp theo cách khác lại tốt hơn.
- Cần ghi chú rõ trong tài liệu và trong phần so sánh kết quả trên UI.

---

## 3. Thuật Toán Quay Lui Nhánh Cận (Branch and Bound)

### 3.1 Nguyên Lý

Duyệt cây nhị phân trạng thái: mỗi nút đại diện cho quyết định **chọn** hoặc **không chọn** trang bị thứ `i`.

**Hàm đánh giá (Upper Bound):**
Dùng relaxation phân số (fractional knapsack): lấy toàn bộ các trang bị có ratio cao nhất còn lại, và có thể lấy **phân số** của trang bị cuối cùng nếu không đủ Vàng. Đây là ước lượng lạc quan nhất về giá trị tối đa có thể đạt được từ nút hiện tại.

**Pruning (Cắt nhánh):**
Nếu `upper_bound(nút) <= best_value_hiện_tại` → cắt bỏ nhánh, không duyệt tiếp.

### 3.2 Kế Hoạch Cài Đặt (`algorithms/branch_and_bound.py`)

**Bước 1 – Tiền xử lý:**
- Sắp xếp `items` theo `ratio` giảm dần (tối ưu hóa hiệu quả cắt nhánh).
- Lưu danh sách trang bị đã sắp xếp để dùng trong hàm bound.

**Bước 2 – Cài đặt hàm `upper_bound(level, gold_remaining, current_power)`:**
- Từ trang bị `level+1` trở đi, tham lam tích lũy sức mạnh theo fractional knapsack.
- Trả về `current_power + sức_mạnh_tối_đa_có_thể_thêm`.

**Bước 3 – Duyệt cây (BFS với Priority Queue hoặc DFS đệ quy):**

*Lựa chọn triển khai:* **BFS với hàng đợi ưu tiên (Best-First Search)**
- Ưu tiên duyệt nút có `upper_bound` cao nhất.
- Thường cắt nhánh sớm hơn DFS, hiệu quả trong thực tế.

*Cấu trúc nút:*
```python
# (upper_bound, level, gold_remaining, current_power, selected_items)
```

**Bước 4 – Cập nhật kỷ lục:**
- Khi duyệt đến nút lá (level = N) hoặc không thể tiếp tục, cập nhật `best_value` và `best_items` nếu tốt hơn.

**Bước 5 – Trả về kết quả** theo cấu trúc API chung.

### 3.3 Xử Lý Trường Hợp Đặc Biệt

| Trường hợp | Xử lý |
|---|---|
| N = 0 hoặc W = 0 | Trả về kết quả rỗng ngay lập tức |
| Tất cả trang bị đắt hơn W | Trả về rỗng |
| N quá lớn (>30 trang bị, W nhỏ) | B&B vẫn hiệu quả do cắt nhánh sớm |
| N lớn, W rất lớn | Có thể chậm hơn DP; cần thông báo người dùng |

### 3.4 Tối Ưu Hiệu Suất

- **Pruning sớm:** Trước khi đẩy nút vào queue, kiểm tra `upper_bound > best_value`.
- **Giới hạn thời gian (timeout):** Thêm cơ chế dừng sau N giây (tùy chọn), trả về kết quả tốt nhất hiện có.
- **Giảm bộ nhớ:** Không lưu toàn bộ `selected_items` trong mỗi nút; thay vào đó chỉ lưu bitmask hoặc index.

---

## 4. Kiểm Thử

### 4.1 Unit Test cho Greedy (`tests/test_greedy.py`)

1. **Test cơ bản:** Đầu vào biết trước kết quả tay → kiểm tra `selected_items` và `total_power`.
2. **Test biên:** W = 0, danh sách rỗng, 1 trang bị.
3. **Test "Greedy không tối ưu":** Thiết kế input mà Greedy chọn tệ hơn DP → đây là ví dụ minh họa điểm yếu, không phải bug.

### 4.2 Unit Test cho Branch & Bound (`tests/test_bnb.py`)

1. **So sánh với DP:** Cùng input, `total_power` của B&B phải **bằng** DP.
2. **Test hiệu suất:** Với N = 20 trang bị, B&B phải hoàn thành trong dưới 5 giây.
3. **Test trường hợp biên:** Tương tự Greedy.

### 4.3 Test So Sánh Ba Thuật Toán (`tests/test_comparison.py`)

- Chạy cả 3 thuật toán trên cùng một bộ dữ liệu.
- Đảm bảo: `total_power(DP) == total_power(B&B) >= total_power(Greedy)`.
- Đảm bảo: `exec_time(Greedy) < exec_time(DP)` (thường đúng với N lớn).

---

## 5. Timeline & Mốc Hoàn Thành

| Tuần | Công việc |
|---|---|
| **Tuần 1** | Nghiên cứu lý thuyết B&B, thiết lập nhánh `feature/greedy-bnb`, cài đặt Greedy cơ bản |
| **Tuần 2** | Cài đặt B&B (hàm bound + BFS), viết unit test Greedy và B&B cơ bản |
| **Tuần 3** | Tối ưu B&B (pruning, timeout), viết test so sánh ba thuật toán, tích hợp với UI |
| **Tuần 4** | Sửa lỗi phát sinh, review code, hỗ trợ Lê Thiên Lộc merge vào `develop` |

---

## 6. Rủi Ro & Biện Pháp Giảm Thiểu

| Rủi ro | Khả năng | Biện pháp |
|---|---|---|
| B&B quá chậm với bộ dữ liệu lớn | Trung bình | Thêm timeout, cải thiện hàm bound |
| Lỗi trong hàm upper_bound dẫn đến kết quả sai | Trung bình | So sánh kết quả B&B với DP trên nhiều test case |
| Tràn bộ nhớ do queue quá lớn | Thấp | Giới hạn kích thước queue hoặc chuyển sang DFS có giới hạn độ sâu |
| Kết quả Greedy bị nhầm là "sai" | Thấp | Chú thích rõ trong UI rằng Greedy là heuristic, không phải optimal |
