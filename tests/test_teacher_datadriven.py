import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from teacher_chat import _get_student_weakness, teacher_welcome, teacher_chat, TeacherChatRequest

async def run_tests():
    print("🧪 Running Data-Driven Michael Chat & Weakness Tests...")
    
    # 1. Test open greeting with no device_id
    res_no = await teacher_welcome(lang="no")
    assert "Hva vil du at vi skal øve på i dag?" in res_no["welcome"], f"Expected open greeting, got: {res_no['welcome']}"
    print("  ✅ PASS: Open greeting NO")

    res_th = await teacher_welcome(lang="th")
    assert "วันนี้อยากให้เราฝึกเรื่องอะไรดีครับ?" in res_th["welcome"], f"Expected open greeting TH, got: {res_th['welcome']}"
    print("  ✅ PASS: Open greeting TH")

    res_en = await teacher_welcome(lang="en")
    assert "What would you like us to practice today?" in res_en["welcome"], f"Expected open greeting EN, got: {res_en['welcome']}"
    print("  ✅ PASS: Open greeting EN")

    # 2. Test teacher_chat with "Hjelp med teoriprøven"
    req_no = TeacherChatRequest(message="📝 Hjelp med teoriprøven", language="no")
    resp_no = await teacher_chat(req_no)
    assert len(resp_no.reply) > 0, "Reply must not be empty"
    print(f"  ✅ PASS: teacher_chat response NO: {resp_no.reply[:60]}...")

    req_th = TeacherChatRequest(message="📝 ช่วยเรื่องข้อสอบทฤษฎี", language="th")
    resp_th = await teacher_chat(req_th)
    assert len(resp_th.reply) > 0, "Reply must not be empty"
    print(f"  ✅ PASS: teacher_chat response TH: {resp_th.reply[:60]}...")

    print("\n🎉 ALL DATA-DRIVEN MICHAEL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_tests())
