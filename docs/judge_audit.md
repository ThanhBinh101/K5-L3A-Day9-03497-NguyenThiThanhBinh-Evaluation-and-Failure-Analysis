# Judge audit

Replay trên 100 nhãn/tiêu chí. FAIL là positive. Giữ nguyên CSV công khai để số liệu tái hiện được; sửa rubric/nhãn audit là đề xuất cho phiên bản dữ liệu tiếp theo.

| Tiêu chí | n | TP / FP / FN / TN | κ | Precision | Recall | Quyết định |
|---|---:|---|---:|---:|---:|---|
| tone_ok | 100 | 24 / 4 / 6 / 66 | 0.757 | 0.857 | 0.800 | Đạt floors κ≥0.6, P≥0.8, R≥0.7; có thể dùng cho tone trong pilot. |
| helpful | 100 | 9 / 0 / 21 / 70 | 0.375 | 1.000 | 0.300 | Loại khỏi gate: bỏ sót 21/30 lỗi. |

Rogan–Gladen: tone quan sát 0.28, sensitivity=0.8, specificity=66/70 → hiệu chỉnh 0.30. Helpful quan sát 0.09 → hiệu chỉnh 0.30; hiệu chỉnh prevalence không làm classifier đủ tốt để chặn từng case.

## Audit bất đồng

| Case | Judge / người | Ai đúng và lý do | Hành động sửa rubric |
|---|---|---|---|
| H-008 | PASS / FAIL | Người: “em”, “nha”, “anh check” quá suồng sã theo phong cách CS yêu cầu. | Thêm ví dụ âm cho xưng hô và đuôi câu suồng sã. |
| H-017 | PASS / FAIL | Người theo note CSV: xưng “bạn” không phù hợp khách lớn tuổi. Tuổi không hiện trong reply, cần thêm context để chấm độc lập. | Cung cấp context xưng hô; thiếu context phải chuyển review. |
| H-029 | PASS / FAIL | Người: “không cần nhắn thêm” mang giọng ra lệnh dù có “Dạ, vui lòng”. | Ưu tiên hành vi ra lệnh hơn từ lịch sự bề mặt. |
| H-042 | FAIL / PASS | Người: câu ngắn đủ ý, không bắt buộc xin lỗi trong mọi thông báo. | Chỉ yêu cầu xin lỗi khi ngữ cảnh cần; thêm ví dụ PASS ngắn. |
| H-051 | FAIL / PASS | Người: thuật ngữ “refund” được CS cho phép theo note dữ liệu. | Đưa từ được phép vào rubric, không tự phạt mọi từ tiếng Anh. |
| H-063 | PASS / FAIL | Người: hứa hoàn thêm ngoài kết quả hệ thống. | Cấm cam kết tài chính chưa có bằng chứng; tiền vẫn do grader code đối chiếu. |
| H-070 | PASS / FAIL | Người: emoji cười không phù hợp khiếu nại. | Thêm ví dụ emoji không phù hợp, không coi thân thiện là đủ. |
| H-081 | FAIL / PASS | Note CSV xác định nhãn người sai vì đọc nhầm ticket; judge đúng theo adjudication đi kèm. Chưa có ticket đầy đủ để kiểm độc lập. | Đưa vào danh sách sửa nhãn sau review; không sửa CSV gốc âm thầm. |
| H-088 | FAIL / PASS | Người: lặp “Dạ” là lỗi gõ nhỏ, không đổi giọng. | Phân biệt lỗi gõ với vi phạm tone. |
| H-094 | PASS / FAIL | Người: phản hồi mất dấu/không đúng chuẩn tiếng Việt theo rubric dữ liệu. | Thêm điều kiện chuẩn ngôn ngữ và ví dụ dịch máy. |

Helpful có precision cao vì chỉ đánh dấu những lỗi dễ, nhưng recall=0.3 và κ=0.375 không đủ. Cần rubric dựa trên trạng thái, tiền và bước tiếp theo; kiểm trên nhãn mới trước khi dùng. Judge tone chưa được kết nối vào money gate; mọi quyết định tài chính/phê duyệt vẫn chấm bằng code.

Lệnh kiểm: `python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 10` (exit 0), tương tự helpful (exit 1 **đúng kỳ vọng**). κ không xác định phải FAIL. Giới hạn: audit này dựa trên reply và note công khai; chưa có người đánh giá độc lập hay held-out mới.
