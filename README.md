# 🛡️ L.O.L Item Optimizer: Giải Quyết Bài Toán Cái Balo (0/1 Knapsack Problem)

## 📌 Giới thiệu Dự án
Dự án này là chương trình mô phỏng và phân tích hiệu suất của các thuật toán kinh điển trong việc giải quyết **Bài toán Cái Balo (0/1 Knapsack Problem)**. 

Thay vì sử dụng các ví dụ xếp hàng hóa khô khan, nhóm chúng tôi ứng dụng bài toán này vào tựa game **Liên Minh Huyền Thoại (League of Legends)**. Mục tiêu của chương trình là tìm ra tổ hợp trang bị tối ưu nhất cho một vị tướng để đạt được ngưỡng sức mạnh cao nhất, dựa trên lượng Vàng (Gold) đang có giới hạn.

Dự án được thực hiện nhằm mục đích phục vụ môn học **Phân tích Thiết kế Giải thuật**.

## 🎮 Mô tả Bài toán trong ngữ cảnh Liên Minh Huyền Thoại
Bài toán Cái Balo 0/1 được ánh xạ vào game như sau:
* **Cái Balo (Knapsack):** Túi đồ của tướng.
* **Trọng lượng tối đa (Capacity - $W$):** Tổng số **Vàng** tối đa mà người chơi đang sở hữu.
* **Đồ vật (Items):** Các trang bị trong cửa hàng LOL (Vô Cực Kiếm, Mũ Phù Thủy, Giáp Máu...). Mỗi trang bị chỉ được mua tối đa 1 lần (đặc trưng của 0/1 Knapsack).
* **Trọng lượng đồ vật ($w_i$):** Giá **Vàng** của trang bị.
* **Giá trị đồ vật ($v_i$):** **Điểm Sức Mạnh** tổng hợp của trang bị (được tính toán dựa trên các chỉ số như SMCK, SMPT, Máu, Điểm hồi kỹ năng...).

**Mục tiêu:** Chọn ra một tập hợp các trang bị sao cho tổng Điểm Sức Mạnh là **lớn nhất** mà tổng giá Vàng không vượt quá số Vàng đang có.

## ⚙️ Các Thuật Toán Áp Dụng và Phân Tích
Chương trình cài đặt và so sánh trực tiếp 3 thuật toán sau:

### 1. Quy hoạch động (Dynamic Programming - DP)
* **Cách hoạt động:** Thuật toán chia bài toán lớn thành các bài toán con nhỏ hơn và lưu kết quả vào một bảng phương án 2 chiều. Công thức truy hồi cốt lõi: 
    $$V[i][w] = \max(V[i-1][w], V[i-1][w - w_i] + v_i)$$
* **Đánh giá:** Đây là thuật toán **luôn đảm bảo tìm ra kết quả tối ưu tuyệt đối**. Tuy nhiên, độ phức tạp thời gian và không gian là $O(N \times W)$ (với $N$ là số trang bị, $W$ là số Vàng). Khi số Vàng ($W$) lên đến hàng chục ngàn, thuật toán này sẽ tiêu tốn rất nhiều bộ nhớ.

### 2. Thuật toán Tham lam (Greedy Algorithm)
* **Cách hoạt động:** Tính tỷ lệ "Sức mạnh trên mỗi Đồng Vàng" ($v_i / w_i$) cho từng trang bị. Sau đó, sắp xếp các trang bị theo tỷ lệ này giảm dần và ưu tiên nhặt các trang bị có tỷ lệ cao nhất cho đến khi hết Vàng.
* **Đánh giá:** Tốc độ chạy cực kỳ nhanh, độ phức tạp chỉ phụ thuộc vào thuật toán sắp xếp $O(N \log N)$. Tuy nhiên, **kết quả thường không phải là tối ưu nhất** vì thuật toán có thể bị kẹt ở "tối ưu cục bộ" (chọn một món đồ tỷ lệ cao nhưng chiếm quá nhiều Vàng, bỏ lỡ cơ hội kết hợp nhiều món đồ nhỏ có tổng sức mạnh lớn hơn).

### 3. Quay lui Nhánh cận (Branch and Bound)
* **Cách hoạt động:** Duyệt qua không gian trạng thái bằng cây nhị phân (chọn hoặc không chọn trang bị). Sử dụng một hàm đánh giá (Bound) để dự đoán giá trị tối đa có thể đạt được ở các nhánh con. Nếu giá trị dự đoán này nhỏ hơn kỷ lục hiện tại (Best Value), thuật toán sẽ cắt bỏ nhánh đó (Pruning) để tiết kiệm thời gian.
* **Đánh giá:** Vẫn đảm bảo ra kết quả tối ưu 100% giống Quy hoạch động. Trong trường hợp tốt (cắt nhánh hiệu quả), nó chạy nhanh hơn DP và tốn ít bộ nhớ hơn. Nhưng ở trường hợp xấu nhất, độ phức tạp vẫn là O(2^N).

## 🚀 Tính năng của Chương trình
1.  **Quản lý Dữ liệu Trang bị:** Cho phép người dùng Thêm/Sửa/Xóa các trang bị LOL với các thông số Giá Vàng và Điểm Sức Mạnh.
2.  **Thiết lập Đầu vào:** Nhập số Vàng tối đa mà người chơi đang có.
3.  **Thực thi Thuật toán:** Cho phép chạy độc lập hoặc chạy đồng thời cả 3 thuật toán (DP, Greedy, Branch & Bound).
4.  **Bảng Xếp Hạng & Báo Cáo:** * Hiển thị danh sách trang bị được chọn bởi từng thuật toán.
    * Tổng Sức mạnh đạt được và Số Vàng còn dư.
    * **Biểu đồ/Bảng so sánh thời gian thực thi (Execution Time)** tính bằng mili-giây, minh chứng rõ ràng sự đánh đổi giữa Tốc độ (Greedy) và Độ chính xác (DP, B&B).

## 💻 Công nghệ Sử dụng
* **Ngôn ngữ lập trình:** C# / .NET
* **Giao diện người dùng (UI):** Windows Forms (WinForms) / WPF
* **Quản lý dữ liệu:** Lưu trữ danh sách trang bị bằng cấu trúc JSON hoặc danh sách đối tượng (Object List) trong bộ nhớ.

## 🛠️ Hướng dẫn Cài đặt và Sử dụng
1. Clone repository này về máy:
   ```bash
   git clone https://github.com/your-username/LOL-Knapsack-Optimizer.git
   ```
2. Mở file solution (`.sln`) bằng **Visual Studio**.
3. Build và Run chương trình (phím `F5`).
4. Tại giao diện chính, load file dữ liệu `items_data.json` có sẵn (chứa thông tin của khoảng 50+ trang bị LOL).
5. Nhập số Vàng (ví dụ: 10000 Gold) và nhấn **"Run Analysis"**.

## 👥 Thành viên Nhóm (Nhóm 5)
| STT | Họ và Tên | Mã Số Sinh Viên | Nhiệm vụ chính |
| :--- | :--- | :--- | :--- |
| 1 | Lê Thiên Lộc | 079306040024 | Thiết kế kiến trúc phần mềm, Cài đặt thuật toán Quy hoạch động |
| 2 | Đỗ Đình Chiến | 51205005553 | Cài đặt thuật toán Tham lam & Quay lui nhánh cận |
| 3 | Nguyễn Văn Vũ | 077206001635 | Thiết kế Giao diện (UI) và trải nghiệm người dùng |
| 4 | Huỳnh Gia Huy | 079206018609 | Xây dựng bộ dữ liệu Test (chỉ số trang bị LOL), Quản lý Git |
| 5 | Hoàng Văn Hưng | 040206020805 | Viết báo cáo phân tích độ phức tạp, Chuẩn bị Slide thuyết trình |
