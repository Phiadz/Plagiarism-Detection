# Kế Hoạch Thực Hiện — Lê Thiên Lộc (MSSV: 079306040024)

**Vai trò:** Thiết kế kiến trúc phần mềm · Cài đặt thuật toán Quy hoạch động · Quản lý Git

---

## 1. Tổng Quan Nhiệm Vụ

Lê Thiên Lộc chịu trách nhiệm đặt nền tảng kỹ thuật cho toàn bộ dự án. Gồm ba mảng công việc chính:

1. Thiết kế kiến trúc tổng thể (cấu trúc thư mục, phân chia module).
2. Cài đặt thuật toán **Quy hoạch động (Dynamic Programming – DP)** – thuật toán cốt lõi đảm bảo kết quả tối ưu.
3. Quản lý phiên bản mã nguồn qua **Git** và điều phối merge giữa các thành viên.

---

## 2. Thiết Kế Kiến Trúc Phần Mềm

### 2.1 Cấu Trúc Thư Mục Đề Xuất

```
L.O.L-Item-Optimizer/
├── main.py                  # Điểm khởi động ứng dụng
├── items_data.json          # Dữ liệu trang bị (do Huỳnh Gia Huy cung cấp)
├── algorithms/
│   ├── __init__.py
│   ├── dp.py                # Thuật toán Quy hoạch động (file này)
│   ├── greedy.py            # Thuật toán Tham lam (Đỗ Đình Chiến)
│   └── branch_and_bound.py  # Quay lui nhánh cận (Đỗ Đình Chiến)
├── models/
│   ├── __init__.py
│   └── item.py              # Lớp dữ liệu Item (trang bị)
├── ui/
│   ├── __init__.py
│   ├── main_window.py       # Cửa sổ chính Tkinter (Nguyễn Văn Vũ)
│   └── result_view.py       # Màn hình hiển thị kết quả (Nguyễn Văn Vũ)
├── utils/
│   ├── __init__.py
│   ├── data_loader.py       # Đọc/ghi JSON
│   └── timer.py             # Đo thời gian thực thi
└── ke-hoach-thuc-hien/      # Tài liệu kế hoạch nhóm
```

### 2.2 Luồng Dữ Liệu (Data Flow)

```
[items_data.json] → data_loader.py → [danh sách Item]
                                          ↓
                               [Nhập số Vàng từ UI]
                                          ↓
                    ┌─────────────────────┼─────────────────────┐
                 dp.py             greedy.py         branch_and_bound.py
                    └─────────────────────┼─────────────────────┘
                                          ↓
                               [Kết quả + Thời gian]
                                          ↓
                                    result_view.py
```

### 2.3 Lớp Dữ Liệu `Item`

Định nghĩa lớp `Item` trong `models/item.py`:

```python
class Item:
    def __init__(self, name: str, gold: int, power: float):
        self.name  = name    # Tên trang bị (ví dụ: "Vô Cực Kiếm")
        self.gold  = gold    # Giá Vàng (trọng lượng w_i)
        self.power = power   # Điểm Sức Mạnh (giá trị v_i)

    def ratio(self) -> float:
        """Tỷ lệ Sức Mạnh / Vàng, dùng cho thuật toán Tham lam."""
        return self.power / self.gold if self.gold > 0 else 0
```

### 2.4 Giao Diện Lập Trình (API) Giữa Các Module

Mỗi thuật toán phải tuân thủ chữ ký hàm chung để UI gọi thống nhất:

```python
def solve(items: list[Item], max_gold: int) -> dict:
    """
    Trả về dict:
    {
        "selected_items": list[Item],  # Danh sách trang bị được chọn
        "total_power":    float,       # Tổng Sức Mạnh đạt được
        "gold_used":      int,         # Tổng Vàng đã dùng
        "gold_remaining": int,         # Vàng còn dư
        "exec_time_ms":   float,       # Thời gian thực thi (mili-giây)
    }
    """
```

---

## 3. Cài Đặt Thuật Toán Quy Hoạch Động

### 3.1 Nguyên Lý

Xây dựng bảng `dp[i][w]` = điểm Sức Mạnh tối đa khi xét `i` trang bị đầu tiên với ngân sách Vàng là `w`.

**Công thức truy hồi:**

```
dp[i][w] = dp[i-1][w]                              nếu gold[i] > w
dp[i][w] = max(dp[i-1][w], dp[i-1][w-gold[i]] + power[i])   nếu gold[i] <= w
```

### 3.2 Kế Hoạch Cài Đặt (`algorithms/dp.py`)

**Bước 1 – Khởi tạo bảng:**
- Tạo bảng 2 chiều kích thước `(N+1) × (W+1)`, giá trị khởi tạo bằng 0.
- `N` = số lượng trang bị, `W` = số Vàng tối đa.

**Bước 2 – Điền bảng:**
- Duyệt hai vòng lặp lồng nhau: `i` từ 1 đến N, `w` từ 0 đến W.
- Áp dụng công thức truy hồi ở trên.

**Bước 3 – Truy vết kết quả (Backtracking):**
- Bắt đầu từ ô `dp[N][W]`.
- Nếu `dp[i][w] != dp[i-1][w]` → trang bị `i` được chọn, trừ `w -= gold[i]`, lùi `i`.
- Lặp lại cho đến khi `i = 0`.

**Bước 4 – Đo thời gian:**
- Dùng `time.perf_counter()` để đo chính xác thời gian thực thi (tránh dùng `time.time()` vì độ phân giải thấp).

**Bước 5 – Tối ưu bộ nhớ (tùy chọn nâng cao):**
- Thay bảng 2 chiều bằng mảng 1 chiều duyệt ngược từ W về 0.
- Giảm bộ nhớ từ O(N×W) xuống O(W), nhưng mất khả năng truy vết.
- **Quyết định:** Triển khai phiên bản bảng đầy đủ trước; nếu RAM là vấn đề thì thêm nhánh tối ưu sau.

### 3.3 Xử Lý Trường Hợp Đặc Biệt

| Trường hợp | Xử lý |
|---|---|
| `max_gold = 0` | Trả về danh sách rỗng, tổng sức mạnh = 0 |
| Danh sách `items` rỗng | Trả về kết quả rỗng |
| Trang bị có `gold > max_gold` | Bỏ qua hoàn toàn (vẫn đưa vào N nhưng không bao giờ chọn) |
| Điểm Sức Mạnh = 0 | Cho phép (trang bị vẫn hợp lệ, chỉ không có giá trị) |

### 3.4 Kiểm Thử Đơn Vị (Unit Test)

Viết file `tests/test_dp.py` với các test case:

1. **Trường hợp cơ bản:** 3 trang bị, W = 5000 Gold → kiểm tra kết quả đúng theo tính tay.
2. **Trường hợp biên:** W = 0, danh sách rỗng.
3. **Trường hợp tất cả vừa túi:** Chọn được tất cả trang bị.
4. **So sánh với Branch & Bound:** Cùng input, kết quả `total_power` phải bằng nhau.

---

## 4. Quản Lý Git

### 4.1 Quy Trình Làm Việc Với Git

```
main (nhánh ổn định)
  └── develop (nhánh tích hợp)
        ├── feature/dp-algorithm        ← Lê Thiên Lộc
        ├── feature/greedy-bnb          ← Đỗ Đình Chiến
        ├── feature/ui-tkinter          ← Nguyễn Văn Vũ
        ├── feature/test-data           ← Huỳnh Gia Huy
        └── docs/report-and-slides      ← Hoàng Văn Hưng
```

### 4.2 Quy Tắc Commit

- **Format:** `[tên-module] mô tả ngắn gọn`
- **Ví dụ:**
  - `[dp] implement core DP table filling`
  - `[architecture] add Item model and data_loader`
  - `[merge] integrate greedy from feature/greedy-bnb`

### 4.3 Quy Trình Merge

1. Mỗi thành viên **không được** commit thẳng vào `main` hoặc `develop`.
2. Tạo Pull Request (PR) từ nhánh feature vào `develop`.
3. Lê Thiên Lộc review và merge sau khi ít nhất 1 thành viên khác approve.
4. Khi `develop` ổn định, merge vào `main` cho milestone quan trọng.

### 4.4 Giải Quyết Xung Đột (Conflict)

- Ưu tiên trao đổi trực tiếp với thành viên liên quan trước khi merge.
- Mỗi module có owner rõ ràng → tránh xung đột chồng chéo.
- File `items_data.json` là "read-only" sau khi Huỳnh Gia Huy hoàn thành.

---

## 5. Timeline & Mốc Hoàn Thành

| Tuần | Công việc |
|---|---|
| **Tuần 1** | Thiết kế kiến trúc, tạo cấu trúc thư mục, định nghĩa `Item` model và `data_loader` |
| **Tuần 2** | Cài đặt thuật toán DP (bảng 2D + truy vết), viết unit test cơ bản |
| **Tuần 3** | Tích hợp DP vào UI (kết nối với Nguyễn Văn Vũ), kiểm tra luồng end-to-end |
| **Tuần 4** | Tối ưu bộ nhớ (nếu cần), review code toàn bộ nhóm, merge `develop → main` |

---

## 6. Rủi Ro & Biện Pháp Giảm Thiểu

| Rủi ro | Khả năng | Biện pháp |
|---|---|---|
| Bộ nhớ không đủ khi W lớn (>50.000 Gold) | Trung bình | Dùng bảng 1D tối ưu bộ nhớ song song với bảng 2D đầy đủ |
| Xung đột merge khi nhiều người sửa cùng file | Thấp | Quy định ownership rõ ràng cho từng file |
| Kết quả DP không khớp với Branch & Bound | Thấp | Viết test so sánh chéo ngay từ đầu |
| Deadline trễ | Trung bình | Buffer 3 ngày cuối tuần 4 để xử lý tồn đọng |
