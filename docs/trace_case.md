# Trace case — C-002@11

| Trường | Bằng chứng |
|---|---|
| Trial | `seeded_regression C-002@11`; report `E-seeded_regression-20261117-8831` |
| Triệu chứng | Status resolved thay vì denied; ledger=20.000đ, 1 khoản thay vì 0đ, 0 khoản. |
| Bước sai đầu tiên | **Event 3**, `model_override {"delay_days":5}`. |
| Các bước trước | Event 1 handoff đúng scope; event 2 investigator đọc DB O-202 có delay_days=2. Ticket khai 5 ngày. |
| Hệ quả | Event 4 quote 20.000đ, event 6 reply nói đã hoàn; tiền sai dù approval hợp lệ. Đây không phải bypass approval. |
| Failure mode | FM-03: tin ticket hơn fact DB. |
| Đối chứng | `fixed C-002@11`: không có override; event 3 quote amount=0, no_entitlement; event 4 reply từ chối; ledger=0, Lab8 PASS. |
| Regression test | `tests/test_lab9_regressions.py::test_lab9_ticket_override_first_wrong_step`: cùng claim/seed, xác nhận variant lỗi ghi tiền và fail; fixed không ghi tiền và pass. |
| Grader bắt lỗi | db_fact_kept, refund_amount_correct, proposal_amount_correct và pass_rate. ReplyLedgerConsistent có thể PASS vì reply phản ánh đúng khoản tiền sai đã được ghi. |
| Giới hạn | Trace cho thấy override và hậu quả, không chứng minh suy nghĩ bên trong model; MockLLM không đại diện model thật. |

Tái hiện từ `src/`:

```bash
../.venv/bin/python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
../.venv/bin/python -m lab9.trace_case --shape fixed --claim C-002 --seed 11
../.venv/bin/python -m pytest -q -m student -o addopts= -k ticket_override
```

Các failure mode khác có bằng chứng riêng trong [trace_evidence.json](trace_evidence.json), sinh lại bằng `python scripts/collect_trace_evidence.py` từ gốc repo.
