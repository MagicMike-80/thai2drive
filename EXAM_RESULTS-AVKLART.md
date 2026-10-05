# Avklaring: eksamenshistorikk i Michael V4

**Kildekontroll 5. oktober 2026:** Michael V4 bruker eksamenshistorikk indirekte i læringsminnet.

1. `fetch_student_learning_memory` henter svakt tema via `_get_student_weakness` i `backend/teacher_chat.py:3723-3726`.
2. `_get_student_weakness` kaller `ai_learning.get_teacher_category_stats` i `backend/teacher_chat.py:3625`.
3. `get_teacher_category_stats` leser `quiz_attempts` og `exam_results` i `backend/ai_learning.py:423-477`. Den samler ordinære svar og eksamenshistorikk, med egne eksamenskilder i funksjonen.
4. `_build_system_prompt` i `backend/teacher_chat.py:1006` leser ingen av disse samlingene selv. Den bygger prompten med læringsminnet den får som argument.

Dette lukker spørsmålet om `exam_results` er med i kildebanen. Fil- og linjereferansene er kodebevis; de er ikke i seg selv en produksjonstest av en konkret elevs historikk.
