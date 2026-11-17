# Evaluation Studio — UI Day 9

Chạy từ gốc repo:

```bash
cd src
../.venv/bin/python -m lab9.dashboard --port 8099
```

Mở http://127.0.0.1:8099. Ctrl+C để dừng server.

## Các màn hình

1. Tổng quan: chọn eval set v1/v2 và biến thể; xem metric, so baseline, paired CI, gate verdict, từng slice.
2. Metric & so sánh: ngưỡng và vai trò blocking; lọc item/seed/slice, chỉ lượt thất bại, xuất JSON.
3. Phân tích trace: bộ evidence cố định cho FM-01 đến FM-09, đánh dấu bước sai đầu tiên, ledger và nhãn kỳ vọng. Bộ chọn variant không thay đổi evidence cố định này.
4. Hướng dẫn M5–M7: giải thích từng bước, ví dụ từ kết quả công khai và giới hạn của đánh giá.

## Dữ liệu và chạy lại

UI dùng report sinh bởi harness và gọi `gate.check` thực. Nếu chưa có report tương ứng, adapter chạy eval; nút Chạy đánh giá luôn chạy lại. Runtime dùng MockLLM, không gọi API model hoặc chuyển tiền thật. Cache mới nằm trong `src/reports/dashboard_<version>_<shape>.json`, không ghi đè baseline và không đưa vào Git. Các lượt eval được serialize vì harness dùng trace và dữ liệu tương đối.

Server chỉ phục vụ ba static asset được allowlist và hai API đọc dữ liệu/trace; POST chạy lại chỉ nhận shape/version hợp lệ. Bind 127.0.0.1. Đây là công cụ local, chưa phải dịch vụ production.

## Kiểm chứng

- 38 test Python qua, gồm kiểm report adapter, slice thật, input không hợp lệ và rerun không ghi đè baseline.
- JavaScript qua `node --check`.
- Kiểm trình duyệt: v1/v2, fixed/slice_regression, fresh rerun, lọc E-014 và chỉ fail trả 3 lượt, trace FM-03 event 3, tab M7, xuất JSON được nối với report.
- Viewport 390px: document width bằng viewport, không tràn ngang toàn trang. Bảng có cuộn ngang bên trong.
- GitHub CI/hidden grader chưa chạy cho phần UI. Kết quả full assignment trước UI nằm trong `src/reports/verification.txt` (34 test ở lần đó).

Ảnh preview: [dashboard-preview.jpg](dashboard-preview.jpg).
