# Day 9: evaluation, failure analysis và regression gate cho LogiX-VN

Agent có thể chạy xong nhưng hoàn tiền sai, bỏ qua quyết định host hoặc reply khác ledger. Bài làm bổ sung eval harness với nhãn tách riêng, grader code, calibration judge, paired bootstrap và CI gate để phát hiện các lỗi này trước merge.

## Thay đổi

- Tích hợp runtime/dữ liệu Day8 nguyên bản để repo Day9 chạy độc lập, không thay logic `src/lab8/`.
- Taxonomy FM-01 đến FM-09, eval set v1 14 item và v2 28 item, mỗi item chạy 5 seed.
- Hoàn thiện confusion matrix, P/R, Cohen κ, Rogan–Gladen, bootstrap paired và estimator pass@k/pass^k có validation.
- Thêm grader approval, ledger amount, reply/ledger và proposal amount; regression test từ trace C-002 và lỗi trừ trước C-013.
- Slice gate money_movement/adversarial/denial; integrity chống report thiếu dòng, trùng dòng, chọn seed, grader crash, đổi slice và nới spec.
- Bổ sung eval card, judge audit, trace case, PRD v1.1, harness map và lệnh kiểm tra end-to-end.

## Bằng chứng local

Chạy từ gốc repo: `python scripts/verify_day9.py`. Toàn bộ output lưu trong `src/reports/verification.txt`.

```text
swarm baseline vs itself: exit 0 — merge
fixed: exit 0 — merge
seeded_regression:
  pass_rate 0.7143; baseline 0.9857
  Δ -0.271 CI [-0.500, -0.057]
exit 1 — blocked: refund_amount_correct, pass_rate, reply_ledger_consistent, proposal_amount_correct

detection 100.00% (target >=80%) · false alarms 0.00% (target <=10%)
mutation score 3/3 · false alarms 0
A/A: mọi metric delta +0.0000
```

Bốn trap được chạy trực tiếp qua CLI gate, đều exit 1 với INTEGRITY: evaluator_errors_as_nan, dropped_failing_rows, cherry_picked_seeds, loosened_spec. Fixed và honest_refactor đều merge.

Tone judge κ=.757, precision=.857, recall=.8 đạt floors. Helpful κ=.375, recall=.3 bị loại, dù precision=1.0.

## Giới hạn và trạng thái nộp

Chỉ đo MockLLM/fixture và judge replay, chưa kiểm hidden grader hoặc người dùng thật. Bộ seed nhỏ không bắt ổn định mọi lỗi hiếm. Parser reply chưa hiểu tiền bằng chữ; absent reply event không được xem là bằng chứng chất lượng diễn đạt.

Đã chuẩn bị code, report và nội dung PR ở local. Chưa push, chưa tạo PR, chưa có kết quả GitHub Actions hoặc phê duyệt Product. Khi nộp, dùng nhánh `starter/d09` theo đề hoặc nhánh được maintainer cho phép; PR vào main của repo nhóm. Nếu cần nộp trên repo Day8, chỉ overlay phần Day9 và docs, giữ nguyên `.gitignore`/runtime Day8 như hướng dẫn đề.
