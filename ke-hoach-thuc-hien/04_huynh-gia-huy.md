# Kế Hoạch Thực Hiện — Huỳnh Gia Huy (MSSV: 079206018609)

**Vai trò:** Xây dựng bộ dữ liệu Test · Hỗ trợ Nguyễn Văn Vũ (UI) · Hỗ trợ Hoàng Văn Hưng (báo cáo)

---

## 1. Tổng Quan Nhiệm Vụ

Huỳnh Gia Huy đảm nhận vai trò **đảm bảo chất lượng dữ liệu và hỗ trợ đa nhiệm** cho nhóm:

1. **Xây dựng bộ dữ liệu trang bị LOL** (file `items_data.json`) — nguồn dữ liệu chạy xuyên suốt toàn bộ ứng dụng.
2. **Hỗ trợ Nguyễn Văn Vũ** kiểm thử giao diện người dùng.
3. **Hỗ trợ Hoàng Văn Hưng** thu thập số liệu thực nghiệm cho báo cáo.

---

## 2. Xây Dựng Bộ Dữ Liệu Trang Bị LOL

### 2.1 Yêu Cầu Dữ Liệu

- Tối thiểu **50 trang bị** để các thuật toán có đủ không gian tìm kiếm thú vị.
- Đảm bảo **tính đa dạng**: trang bị rẻ (< 1000 Gold), trung bình (1000–3000 Gold), đắt (> 3000 Gold).
- Trang bị phải thực tế, lấy từ game LOL (phiên bản hiện tại hoặc phiên bản quen thuộc).

### 2.2 Cấu Trúc File `items_data.json`

```json
[
  {
    "name": "Vô Cực Kiếm",
    "gold": 3400,
    "power": 85.0
  },
  {
    "name": "Mũ Phù Thủy Rabadon",
    "gold": 3600,
    "power": 92.0
  },
  {
    "name": "Đoản Kiếm",
    "gold": 350,
    "power": 8.5
  }
]
```

### 2.3 Phương Pháp Tính Điểm Sức Mạnh (`power`)

Điểm Sức Mạnh là chỉ số **tổng hợp** được tính từ các chỉ số của trang bị. Công thức đề xuất:

```
power = (SMCK × 0.4) + (SMPT × 0.3) + (Máu / 100 × 0.15) + (Hồi Năng Lượng × 0.15)
```

Trong đó:
- **SMCK** (Sát thương Công kích): Ảnh hưởng đến sức mạnh công kích vật lý.
- **SMPT** (Sát thương Phép thuật): Ảnh hưởng đến sức mạnh phép thuật.
- **Máu**: Lượng máu tối đa bổ sung.
- **Hồi Năng Lượng**: Năng lượng/Mana hồi phục thêm.

> **Lưu ý:** Công thức trọng số trên chỉ là ví dụ mẫu. Nhóm có thể điều chỉnh hệ số để phù hợp hơn với meta game. Điều quan trọng là áp dụng **cùng công thức nhất quán** cho tất cả trang bị.

### 2.4 Danh Sách Trang Bị Tham Khảo (50+ mục)

Phân loại theo nhóm để đảm bảo đa dạng:

**Nhóm Trang bị Tấn công Vật lý (AD):**
- Vô Cực Kiếm (Infinity Edge), Tiễn Thần (Kraken Slayer), Kiếm Gió (Stormrazor), Đại Kiếm (B.F. Sword), Đoản Kiếm (Long Sword), Vũ Khí Titan, Kiếm Máu (Bloodthirster), ...

**Nhóm Trang bị Phép thuật (AP):**
- Mũ Rabadon, Orb Luscent, Luden's Tempest, Shadowflame, Zhonya, Void Staff, Seraph's Embrace, ...

**Nhóm Trang bị Phòng thủ (Tank):**
- Giáp Máu (Warmog's Armor), Sunfire Aegis, Thornmail, Gargoyle Stoneplate, Randuin's Omen, Force of Nature, ...

**Nhóm Trang bị Hỗ trợ (Support):**
- Moonstone Renewer, Locket of the Iron Solari, Shurelya's Battlesong, Staff of Flowing Water, ...

**Nhóm Trang bị Cơ bản (Starter/Component):**
- Đoản Kiếm, Amplifying Tome, Cloth Armor, Null-Magic Mantle, Ruby Crystal, Sapphire Crystal, ...

### 2.5 Quy Trình Xây Dựng Dữ Liệu

**Bước 1 – Thu thập chỉ số:**
- Tra cứu chỉ số trang bị từ wiki chính thức: `leagueoflegends.fandom.com/wiki`
- Ghi chú: Tên trang bị, Gold, SMCK, SMPT, Máu, Hồi Năng Lượng.

**Bước 2 – Tính điểm Sức Mạnh:**
- Dùng bảng tính (Excel/Google Sheets) để áp dụng công thức đồng đều.
- Làm tròn đến 1 chữ số thập phân.

**Bước 3 – Tạo file JSON:**
- Chuyển bảng tính thành file `items_data.json` theo cấu trúc đã định.
- Kiểm tra JSON hợp lệ bằng validator online hoặc `python -m json.tool items_data.json`.

**Bước 4 – Kiểm tra dữ liệu:**
- Đảm bảo không có tên trùng lặp.
- Đảm bảo tất cả `gold > 0` và `power > 0`.
- Đảm bảo đủ ít nhất 50 trang bị.

### 2.6 Bộ Dữ Liệu Test Đặc Biệt

Ngoài bộ dữ liệu chính, tạo thêm các bộ nhỏ để kiểm thử thuật toán:

| File | Mục đích | Số trang bị | Ghi chú |
|---|---|---|---|
| `test_small.json` | Test cơ bản | 5–10 | Có thể tính tay kết quả |
| `test_greedy_fail.json` | Minh họa Greedy không tối ưu | 4–6 | Thiết kế để Greedy chọn sai |
| `test_large.json` | Test hiệu suất | 100+ | Kiểm tra tốc độ DP và B&B |

---

## 3. Hỗ Trợ Nguyễn Văn Vũ (UI)

### 3.1 Kiểm Thử Giao Diện

Sau khi Nguyễn Văn Vũ hoàn thành từng thành phần UI, Huỳnh Gia Huy thực hiện:

**Checklist kiểm thử:**
- [ ] Load file `items_data.json` → danh sách hiển thị đủ 50+ trang bị.
- [ ] Thêm trang bị mới → xuất hiện trong danh sách.
- [ ] Sửa trang bị → thông tin cập nhật đúng.
- [ ] Xóa trang bị → biến mất khỏi danh sách.
- [ ] Nhập số Vàng không hợp lệ (chữ, âm, 0) → thông báo lỗi xuất hiện.
- [ ] Chạy phân tích → kết quả hiển thị đúng trong tab tương ứng.
- [ ] Xem biểu đồ → cửa sổ mở, biểu đồ rõ ràng.
- [ ] Đóng ứng dụng → không bị lỗi crash.

### 3.2 Báo Cáo Lỗi

- Ghi lỗi vào file `bug_report.md` (chỉ nội bộ nhóm, không commit vào repo).
- Phân loại: Lỗi nghiêm trọng (crash), Lỗi chức năng (sai kết quả), Lỗi hiển thị (giao diện).
- Ưu tiên xử lý lỗi nghiêm trọng trước.

---

## 4. Hỗ Trợ Hoàng Văn Hưng (Báo Cáo)

### 4.1 Thu Thập Số Liệu Thực Nghiệm

Chạy cả 3 thuật toán với nhiều bộ tham số khác nhau và ghi lại thời gian thực thi:

| N (số trang bị) | W (Gold) | DP (ms) | Greedy (ms) | B&B (ms) |
|---|---|---|---|---|
| 10 | 5000 | ? | ? | ? |
| 20 | 10000 | ? | ? | ? |
| 30 | 15000 | ? | ? | ? |
| 50 | 20000 | ? | ? | ? |
| 100 | 50000 | ? | ? | ? |

**Công cụ:** Chạy script Python đơn giản gọi trực tiếp các hàm `solve()`, lặp lại 5 lần và lấy trung bình.

### 4.2 Định Dạng Số Liệu Cho Báo Cáo

- Cung cấp cho Hoàng Văn Hưng dữ liệu ở dạng bảng (Markdown hoặc Excel).
- Ghi rõ cấu hình máy tính dùng để test (CPU, RAM, OS).

---

## 5. Timeline & Mốc Hoàn Thành

| Tuần | Công việc |
|---|---|
| **Tuần 1** | Thu thập chỉ số 50+ trang bị LOL, xây dựng bảng tính điểm Sức Mạnh |
| **Tuần 2** | Tạo `items_data.json` và 3 bộ dữ liệu test chuyên biệt, kiểm tra JSON hợp lệ |
| **Tuần 3** | Kiểm thử UI (khi Nguyễn Văn Vũ hoàn thành tuần 2–3), báo cáo lỗi |
| **Tuần 4** | Thu thập số liệu thực nghiệm cho Hoàng Văn Hưng, kiểm thử lần cuối toàn ứng dụng |

---

## 6. Rủi Ro & Biện Pháp Giảm Thiểu

| Rủi ro | Khả năng | Biện pháp |
|---|---|---|
| Chỉ số trang bị LOL không cập nhật (game patch) | Thấp | Ghi rõ phiên bản game trong README |
| Công thức tính `power` không hợp lý (mất cân bằng) | Trung bình | So sánh với cảm nhận thực tế: Vô Cực Kiếm phải mạnh hơn Đoản Kiếm |
| File JSON lỗi cú pháp khi nhập tay | Trung bình | Dùng script Python để tạo JSON, không nhập tay thủ công |
| Không đủ thời gian kiểm thử UI đầy đủ | Thấp | Ưu tiên checklist theo thứ tự quan trọng, bỏ qua test thẩm mỹ nếu cần |
