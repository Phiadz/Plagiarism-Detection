# Kế Hoạch Thực Hiện — Hoàng Văn Hưng (MSSV: 040206020805)

**Vai trò:** Viết báo cáo phân tích độ phức tạp · Giải thích các thuật toán · Tối ưu thuật toán · Chuẩn bị Slide thuyết trình

---

## 1. Tổng Quan Nhiệm Vụ

Hoàng Văn Hưng chịu trách nhiệm **tài liệu học thuật và trình bày** của dự án. Công việc gồm:

1. Viết **báo cáo phân tích độ phức tạp** đầy đủ, có căn cứ lý thuyết và số liệu thực nghiệm.
2. Giải thích rõ ràng, dễ hiểu nguyên lý của từng thuật toán.
3. Đề xuất và ghi lại các **hướng tối ưu thuật toán**.
4. Thiết kế **bộ slide thuyết trình** chuyên nghiệp cho buổi báo cáo.

---

## 2. Báo Cáo Phân Tích Độ Phức Tạp

### 2.1 Cấu Trúc Báo Cáo Đề Xuất

```
Báo cáo: L.O.L Item Optimizer — Phân tích Thuật toán
├── 1. Giới thiệu Bài toán
│   ├── Bài toán Cái Balo 0/1 — Định nghĩa hình thức
│   └── Ánh xạ vào ngữ cảnh LOL
├── 2. Phân tích Ba Thuật toán
│   ├── 2.1 Quy hoạch động (DP)
│   ├── 2.2 Thuật toán Tham lam (Greedy)
│   └── 2.3 Quay lui Nhánh Cận (Branch and Bound)
├── 3. So sánh Lý thuyết
│   └── Bảng so sánh: Độ phức tạp thời gian, không gian, đảm bảo tối ưu
├── 4. Kết quả Thực nghiệm
│   ├── Điều kiện thí nghiệm
│   ├── Bảng số liệu thời gian thực thi
│   └── Biểu đồ so sánh
├── 5. Thảo luận & Hướng Tối ưu
└── 6. Kết luận
```

### 2.2 Nội Dung Chi Tiết Từng Phần

---

#### Phần 1: Giới Thiệu Bài Toán

**Định nghĩa hình thức:**

Cho tập $n$ trang bị $\{1, 2, ..., n\}$, mỗi trang bị $i$ có giá vàng $w_i \in \mathbb{Z}^+$ và điểm sức mạnh $v_i \in \mathbb{R}^+$. Cho ngân sách $W \in \mathbb{Z}^+$.

Tìm tập con $S \subseteq \{1,...,n\}$ sao cho:

$$\text{Tối đa hóa: } \sum_{i \in S} v_i$$
$$\text{Ràng buộc: } \sum_{i \in S} w_i \leq W, \quad x_i \in \{0, 1\}$$

**Ánh xạ vào LOL:** Giải thích ngắn gọn với bảng đối chiếu (Trang bị ↔ Đồ vật; Gold ↔ Trọng lượng; Power ↔ Giá trị).

---

#### Phần 2.1: Phân Tích Quy Hoạch Động

**Nội dung cần viết:**

- Trình bày công thức truy hồi đầy đủ, có chứng minh tính đúng đắn (correctness proof) ngắn gọn.
- **Độ phức tạp thời gian:** $O(N \times W)$ — giải thích tại sao (2 vòng lặp lồng nhau).
- **Độ phức tạp không gian:** $O(N \times W)$ với bảng 2D; $O(W)$ với bảng 1D tối ưu — giải thích sự đánh đổi.
- **Tính tối ưu:** DP luôn cho kết quả tối ưu (chứng minh bằng quy nạp hoặc bằng phản chứng).
- **Giới hạn thực tế:** Khi $W = 50.000$ và $N = 100$ → bảng có 5 triệu ô → ~40 MB RAM → tính toán xem có vượt ngưỡng không.

---

#### Phần 2.2: Phân Tích Thuật Toán Tham Lam

**Nội dung cần viết:**

- Mô tả thuật toán theo từng bước (pseudo-code).
- **Độ phức tạp thời gian:** $O(N \log N)$ (do sắp xếp) + $O(N)$ (duyệt) = $O(N \log N)$.
- **Độ phức tạp không gian:** $O(N)$ (lưu danh sách sắp xếp).
- **Tính không tối ưu:** Đưa ra **ví dụ phản chứng** cụ thể:
  - 3 trang bị: (Gold=5, Power=4), (Gold=3, Power=3), (Gold=3, Power=3); W=6.
  - Greedy chọn trang bị ratio 0.8 → tổng power=4.
  - Tối ưu: Chọn 2 trang bị nhỏ → tổng power=6.
- **Trường hợp Greedy cho kết quả tối ưu:** Bài toán phân số (Fractional Knapsack) — phân biệt với 0/1.

---

#### Phần 2.3: Phân Tích Branch and Bound

**Nội dung cần viết:**

- Mô tả cấu trúc cây tìm kiếm nhị phân, vẽ sơ đồ minh họa với ví dụ nhỏ (3–4 trang bị).
- **Hàm Bound:** Giải thích tại sao dùng Fractional Knapsack làm upper bound — tính chất lạc quan.
- **Độ phức tạp:**
  - Trường hợp tốt nhất: $O(N \log N)$ (cắt hầu hết nhánh).
  - Trường hợp xấu nhất: $O(2^N)$ (không cắt được nhánh nào).
  - Trung bình trong thực tế: tốt hơn DP đáng kể khi $W$ lớn.
- **Độ phức tạp không gian:** $O(N \times 2^N)$ trong trường hợp xấu nhất (BFS), $O(N)$ cho DFS.
- **So sánh với DP:** DP tốt khi $W$ nhỏ; B&B tốt khi $N$ nhỏ hoặc khi pruning hiệu quả.

---

#### Phần 3: Bảng So Sánh Lý Thuyết

| Tiêu chí | DP | Greedy | Branch & Bound |
|---|---|---|---|
| Độ phức tạp thời gian | $O(N \times W)$ | $O(N \log N)$ | $O(2^N)$ xấu nhất |
| Độ phức tạp không gian | $O(N \times W)$ | $O(N)$ | $O(N)$ (DFS) |
| Đảm bảo kết quả tối ưu | ✅ Có | ❌ Không | ✅ Có |
| Hiệu quả khi N lớn, W nhỏ | Tốt | Tốt | Tốt (pruning hiệu quả) |
| Hiệu quả khi N nhỏ, W lớn | Kém (bộ nhớ) | Tốt | Tốt |
| Độ phức tạp cài đặt | Trung bình | Dễ | Khó |

---

#### Phần 4: Kết Quả Thực Nghiệm

**Điều kiện thí nghiệm** (Huỳnh Gia Huy cung cấp số liệu):
- CPU: [ghi rõ], RAM: [ghi rõ], OS: [ghi rõ].
- Mỗi cấu hình chạy 5 lần, lấy giá trị trung bình.

**Bảng số liệu mẫu:**

| N | W | DP (ms) | Greedy (ms) | B&B (ms) | Tối ưu DP? | Tối ưu B&B? |
|---|---|---|---|---|---|---|
| 10 | 5000 | ? | ? | ? | ? | = DP |
| 30 | 15000 | ? | ? | ? | ? | = DP |
| 50 | 30000 | ? | ? | ? | ? | = DP |
| 100 | 50000 | ? | ? | ? | ? | = DP |

**Phân tích:**
- Nhận xét xu hướng: DP tăng tuyến tính theo W, Greedy gần như hằng số, B&B biến động.
- Chỉ ra ngưỡng N/W mà B&B bắt đầu nhanh hơn DP.

---

#### Phần 5: Hướng Tối Ưu Thuật Toán

**5.1 Tối ưu Quy Hoạch Động:**
- **Tối ưu bộ nhớ:** Dùng bảng 1D duyệt ngược, giảm từ $O(N \times W)$ xuống $O(W)$.
- **Pruning sớm:** Nếu toàn bộ trang bị có tổng Gold < W, không cần điền hết bảng.
- **Sparse DP:** Khi W rất lớn nhưng các giá trị $w_i$ có nhiều ước chung, có thể rút gọn bảng.

**5.2 Tối ưu Branch and Bound:**
- **Cải thiện hàm Bound:** Dùng LP relaxation thay vì greedy fractional cho bound chặt hơn.
- **Best-First Search:** Ưu tiên duyệt nút có bound cao → cắt nhánh sớm hơn DFS.
- **Timeout:** Giới hạn thời gian, trả về kết quả tốt nhất hiện có.

**5.3 Hướng Mở Rộng (nếu có thời gian):**
- **Thuật toán di truyền (Genetic Algorithm):** Heuristic mạnh hơn Greedy, gần optimal.
- **Simulated Annealing:** Phù hợp khi N rất lớn.
- **Meet-in-the-Middle:** Tách thành 2 nhóm, giảm từ $O(2^N)$ xuống $O(2^{N/2})$.

---

## 3. Chuẩn Bị Slide Thuyết Trình

### 3.1 Cấu Trúc Bộ Slide (20–25 slides)

| Slide | Tiêu đề | Nội dung chính |
|---|---|---|
| 1 | Trang bìa | Tên dự án, nhóm 2, môn học, giảng viên |
| 2 | Mục lục | Danh sách các phần sẽ trình bày |
| 3 | Giới thiệu bài toán | 0/1 Knapsack là gì? |
| 4 | Ánh xạ vào LOL | Bảng đối chiếu, hình minh họa |
| 5–6 | Quy hoạch động | Công thức, minh họa bảng, độ phức tạp |
| 7–8 | Thuật toán Tham lam | Ví dụ, ưu/nhược điểm, phản chứng |
| 9–11 | Branch and Bound | Sơ đồ cây, hàm bound, pruning minh họa |
| 12 | Bảng so sánh lý thuyết | Bảng 3 thuật toán |
| 13 | Demo ứng dụng | Screenshot/GIF giao diện |
| 14–15 | Kết quả thực nghiệm | Bảng số liệu + biểu đồ cột |
| 16–17 | Phân tích kết quả | Nhận xét, giải thích xu hướng |
| 18 | Hướng tối ưu | Bullet points ngắn gọn |
| 19 | Phân công nhóm | Bảng thành viên + nhiệm vụ |
| 20 | Kết luận | Tóm tắt đóng góp, bài học rút ra |
| 21 | Q&A | Trang câu hỏi |

### 3.2 Nguyên Tắc Thiết Kế Slide

- **Mỗi slide chỉ có 1 ý chính.** Tránh nhồi nhét quá nhiều text.
- **Ưu tiên hình ảnh, sơ đồ** hơn đoạn văn dài.
- **Theme LOL:** Màu vàng đồng, nền tối, font rõ ràng (Arial, Calibri).
- **Công thức toán học:** Dùng LaTeX nếu dùng Beamer, hoặc equation editor trong PowerPoint.
- **Biểu đồ:** Copy trực tiếp từ kết quả thực nghiệm (matplotlib screenshot hoặc xuất PNG).

### 3.3 Chuẩn Bị Nội Dung Nói (Speaker Notes)

- Viết notes cho mỗi slide: câu mở đầu, điểm nhấn, câu chuyển tiếp sang slide tiếp theo.
- Luyện tập để trình bày trong **10–15 phút** (tùy yêu cầu giảng viên).
- Chuẩn bị trả lời câu hỏi thường gặp: "Tại sao không dùng Greedy?", "B&B tệ hơn DP khi nào?"

---

## 4. Timeline & Mốc Hoàn Thành

| Tuần | Công việc |
|---|---|
| **Tuần 1** | Nghiên cứu lý thuyết 3 thuật toán, bắt đầu phần 1–2 của báo cáo |
| **Tuần 2** | Hoàn thành phần lý thuyết báo cáo (phần 1–3), bắt đầu thiết kế slide frame |
| **Tuần 3** | Nhận số liệu thực nghiệm từ Huỳnh Gia Huy, viết phần 4–5 báo cáo, hoàn thiện slide |
| **Tuần 4** | Review toàn bộ báo cáo + slide, luyện tập thuyết trình, chỉnh sửa lần cuối |

---

## 5. Rủi Ro & Biện Pháp Giảm Thiểu

| Rủi ro | Khả năng | Biện pháp |
|---|---|---|
| Số liệu thực nghiệm đến muộn | Trung bình | Lấp placeholder trong báo cáo, điền sau |
| Không có đủ thời gian luyện tập thuyết trình | Trung bình | Luyện từng phần nhỏ xen kẽ trong tuần 3 |
| Slide quá nhiều text, nhìn không hấp dẫn | Trung bình | Peer review slide với 1 thành viên khác trước khi nộp |
| Báo cáo thiếu phần phân tích sâu | Thấp | Tham khảo các tài liệu tham khảo cụ thể (xem mục 6) |

---

## 6. Tài Liệu Tham Khảo Đề Xuất

1. Cormen, T. H., et al. *Introduction to Algorithms* (CLRS), 3rd ed. — Chương 16 (Greedy), Chương 15 (DP).
2. Papadimitriou, C. & Steiglitz, K. *Combinatorial Optimization: Algorithms and Complexity* — Bài toán Knapsack.
3. Martello, S. & Toth, P. *Knapsack Problems: Algorithms and Computer Implementations* — Tham khảo B&B chuyên sâu.
4. Trang wiki thuật toán: `en.wikipedia.org/wiki/Knapsack_problem`
5. Dữ liệu trang bị LOL: `leagueoflegends.fandom.com/wiki/Item`
