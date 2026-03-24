# Kế Hoạch Thực Hiện — Nguyễn Văn Vũ (MSSV: 077206001635)

**Vai trò:** Thiết kế Giao diện người dùng (UI) · Trải nghiệm người dùng (UX) · Tkinter

---

## 1. Tổng Quan Nhiệm Vụ

Nguyễn Văn Vũ chịu trách nhiệm toàn bộ **giao diện đồ họa** của ứng dụng, sử dụng thư viện **Tkinter** tích hợp sẵn trong Python. Giao diện phải:

1. Thân thiện, trực quan, dễ sử dụng ngay cả với người không rành kỹ thuật.
2. Tích hợp đầy đủ với ba thuật toán (DP, Greedy, B&B) thông qua API chung.
3. Hiển thị biểu đồ so sánh thời gian thực thi bằng `matplotlib`.

---

## 2. Phân Tích Yêu Cầu UI

### 2.1 Các Màn Hình Cần Xây Dựng

| Màn hình | Mô tả |
|---|---|
| **Cửa sổ chính** | Điểm vào của ứng dụng, chứa tất cả chức năng chính |
| **Panel Quản lý Trang bị** | Hiển thị danh sách, thêm/sửa/xóa trang bị |
| **Form Nhập Trang bị** | Dialog nhỏ để nhập thông tin trang bị mới hoặc chỉnh sửa |
| **Panel Thiết lập Đầu vào** | Nhập số Vàng tối đa, chọn thuật toán |
| **Panel Kết quả** | Hiển thị trang bị được chọn, tổng sức mạnh, vàng dư |
| **Cửa sổ Biểu đồ** | So sánh thời gian thực thi của 3 thuật toán |

### 2.2 Nguyên Tắc UX

- Màu sắc chủ đạo theo theme **League of Legends**: vàng đồng (`#C89B3C`), nền tối (`#1E1E2E`), chữ sáng.
- Phản hồi trực quan khi nút được nhấn (hiệu ứng hover, trạng thái loading).
- Thông báo lỗi rõ ràng khi người dùng nhập sai (ví dụ: nhập chữ vào ô số Vàng).
- Kết quả phải hiển thị ngay lập tức sau khi thuật toán chạy xong.

---

## 3. Thiết Kế Chi Tiết Các Thành Phần

### 3.1 Cửa Sổ Chính (`ui/main_window.py`)

**Bố cục (Layout):**

```
┌─────────────────────────────────────────────────────────┐
│  [Logo LOL]   L.O.L Item Optimizer — Nhóm 2             │
├─────────────────┬───────────────────────────────────────┤
│                 │  ┌─ Thiết lập ──────────────────────┐ │
│  Danh sách      │  │  Số Vàng tối đa: [_________]     │ │
│  Trang bị       │  │  Thuật toán:  ☑DP  ☑Greedy  ☑B&B │ │
│  (TreeView)     │  │  [  Chạy Phân Tích  ]             │ │
│                 │  └──────────────────────────────────┘ │
│  [Thêm] [Sửa]  │  ┌─ Kết quả ────────────────────────┐ │
│  [Xóa]  [Load] │  │  (Tab: DP | Greedy | B&B)         │ │
│                 │  │  Trang bị đã chọn: ...            │ │
│                 │  │  Tổng Sức Mạnh: ... | Vàng dư: . │ │
│                 │  └──────────────────────────────────┘ │
│                 │  [ Xem Biểu đồ So sánh ]              │
└─────────────────┴───────────────────────────────────────┘
```

**Widget chính:**
- `ttk.Treeview` cho danh sách trang bị (cột: Tên, Gold, Power, Ratio).
- `ttk.Entry` cho ô nhập số Vàng.
- `ttk.Checkbutton` × 3 để chọn thuật toán.
- `ttk.Button` cho các hành động (Thêm, Sửa, Xóa, Load, Chạy).
- `ttk.Notebook` (tab) để hiển thị kết quả từng thuật toán.

### 3.2 Panel Quản Lý Trang Bị

**Chức năng cần cài đặt:**

- **Thêm trang bị:** Mở `ItemDialog`, lấy thông tin, thêm vào danh sách và cập nhật `TreeView`.
- **Sửa trang bị:** Chọn hàng trong `TreeView`, mở `ItemDialog` với dữ liệu điền sẵn.
- **Xóa trang bị:** Xác nhận bằng `messagebox.askyesno`, xóa khỏi danh sách.
- **Load từ JSON:** Mở `filedialog.askopenfilename`, đọc file `items_data.json`, cập nhật `TreeView`.
- **Lưu JSON:** `filedialog.asksaveasfilename`, ghi danh sách hiện tại ra file.

### 3.3 Form Nhập Trang Bị (`ItemDialog`)

Dialog đơn giản (`tk.Toplevel`) với:
- Ô nhập **Tên trang bị** (`Entry`)
- Ô nhập **Giá Vàng** (`Entry`, chỉ nhận số nguyên dương)
- Ô nhập **Điểm Sức Mạnh** (`Entry`, chỉ nhận số thực dương)
- Nút **[Lưu]** và **[Hủy]**

**Validation:**
- Tên không được để trống.
- Giá Vàng phải là số nguyên dương (> 0).
- Điểm Sức Mạnh phải là số thực dương (> 0).
- Hiển thị thông báo lỗi inline (Label đỏ) nếu nhập sai.

### 3.4 Panel Kết Quả

Dùng `ttk.Notebook` với 3 tab tương ứng 3 thuật toán. Mỗi tab gồm:

- **Bảng trang bị được chọn** (`TreeView`: Tên, Gold, Power)
- **Thông tin tổng kết:**
  - Tổng Sức Mạnh đạt được
  - Tổng Vàng đã dùng / Số Vàng còn dư
  - Thời gian thực thi (ms)
- **Badge màu** trực quan:
  - Xanh lá ✅ = tối ưu (DP, B&B)
  - Vàng ⚠️ = heuristic (Greedy)

### 3.5 Cửa Sổ Biểu Đồ So Sánh

Sử dụng `matplotlib` nhúng vào Tkinter qua `FigureCanvasTkAgg`:

- **Biểu đồ cột (Bar Chart):** So sánh thời gian thực thi (ms) của 3 thuật toán.
- **Biểu đồ cột (Bar Chart):** So sánh Tổng Sức Mạnh đạt được của 3 thuật toán.
- Trục X: Tên thuật toán; Trục Y: Thời gian (ms) / Điểm sức mạnh.
- Màu sắc khác nhau cho từng thuật toán.
- Thêm nhãn giá trị trên đỉnh mỗi cột.

---

## 4. Tích Hợp Với Các Module Khác

### 4.1 Gọi Thuật Toán

```python
# Trong main_window.py, khi nhấn "Chạy Phân Tích"
from algorithms.dp import solve as dp_solve
from algorithms.greedy import solve as greedy_solve
from algorithms.branch_and_bound import solve as bnb_solve

def run_analysis():
    max_gold = int(gold_entry.get())
    results = {}
    if dp_checkbox.get():
        results['DP'] = dp_solve(items, max_gold)
    if greedy_checkbox.get():
        results['Greedy'] = greedy_solve(items, max_gold)
    if bnb_checkbox.get():
        results['B&B'] = bnb_solve(items, max_gold)
    display_results(results)
```

### 4.2 Hiển Thị Kết Quả

- Sau khi `run_analysis()` hoàn thành, cập nhật từng tab trong `Notebook`.
- Nếu chỉ chạy 1 thuật toán → chỉ cập nhật tab đó, không xóa kết quả cũ của tab khác.

### 4.3 Xử Lý Lỗi UI

- Nếu chưa load dữ liệu mà nhấn "Chạy" → hiển thị `messagebox.showerror`.
- Nếu ô số Vàng trống hoặc không hợp lệ → highlight đỏ ô đó và hiển thị thông báo.
- Trong khi chạy thuật toán → hiển thị cursor "wait" (`root.config(cursor="wait")`).

---

## 5. Phân Công Phối Hợp Với Huỳnh Gia Huy

Huỳnh Gia Huy hỗ trợ Nguyễn Văn Vũ trong các công việc:

- **Kiểm thử UI:** Thử nghiệm tất cả các chức năng Thêm/Sửa/Xóa/Load với bộ dữ liệu thật.
- **Test hiển thị:** Đảm bảo tên trang bị dài không bị cắt trong `TreeView`.
- **Feedback UX:** Đưa ra nhận xét về sự thuận tiện, dễ dùng từ góc nhìn người dùng game.

---

## 6. Timeline & Mốc Hoàn Thành

| Tuần | Công việc |
|---|---|
| **Tuần 1** | Nghiên cứu Tkinter (`ttk`, `Notebook`, `TreeView`), thiết kế wireframe bố cục |
| **Tuần 2** | Cài đặt cửa sổ chính, Panel danh sách trang bị, `ItemDialog` với validation |
| **Tuần 3** | Tích hợp thuật toán (chờ Lê Thiên Lộc và Đỗ Đình Chiến hoàn thành), Panel kết quả |
| **Tuần 4** | Cửa sổ biểu đồ `matplotlib`, tinh chỉnh giao diện, test toàn diện với Huỳnh Gia Huy |

---

## 7. Rủi Ro & Biện Pháp Giảm Thiểu

| Rủi ro | Khả năng | Biện pháp |
|---|---|---|
| Tkinter bị đóng băng (freeze) khi B&B chạy lâu | Cao | Chạy thuật toán trong `threading.Thread` riêng, cập nhật UI qua `root.after()` |
| Biểu đồ matplotlib không hiển thị đúng trong Tkinter | Thấp | Dùng `FigureCanvasTkAgg` đúng cách, tham khảo ví dụ tích hợp |
| Giao diện trông xấu trên màn hình độ phân giải khác | Trung bình | Dùng `grid` layout với `sticky`, thử nghiệm trên nhiều độ phân giải |
| Thuật toán chưa xong khi cần tích hợp | Trung bình | Dùng mock function trả về dữ liệu giả để phát triển UI độc lập |
