import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import requests
import json

# ===============================
# 🔗 ใส่ Webhook URL ตรงนี้
# ===============================
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyx_WZtzg-50AatkhH6SWbbg2eV2kL1_yKrjmBhr40uhY27QIZ3k3G7MqoOoIFg_wvBSQ/exec"

# ===============================
# CONFIG (A4 300 DPI)
# ===============================
DPI = 300
MM_TO_PX = DPI / 25.4

def mm(x, y):
    return int(x * MM_TO_PX), int(y * MM_TO_PX)

def mm_w(v):
    return int(v * MM_TO_PX)

def mm_h(v):
    return int(v * MM_TO_PX)

BASELINE_OFFSET = mm_h(0.8)

SAFE_ZONE = {"x1": 0,"y1": 0,"x2": 210,"y2": 50}

FIELDS = {
    "request_dept": {"x": 47, "y": 63},
    "requester": {"x": 47, "y": 70},
    "approver": {"x": 55, "y": 78},
    "receive_date": {"x": 147, "y": 70},
    "due_date": {"x": 149, "y": 78},
    "project_name": {"x": 36, "y": 103},
    "project_size": {"x": 128, "y": 103},
    "detail": {"x": 63, "y": 110},
    "designer": {"x": 35, "y": 238},
    "designer_date": {"x": 107, "y": 237},
    "approve2": {"x": 53, "y": 245},
    "approve2_date": {"x": 107, "y": 245},
    "cb_print": {"x": 40, "y": 92},
    "cb_online": {"x": 40, "y": 99},
    "cb_booth": {"x": 75, "y": 92},
    "cb_other": {"x": 75, "y": 99},
    "cb_normal": {"x": 140, "y": 92},
    "cb_urgent": {"x": 140, "y": 99},
    "other_text": {"x": 100, "y": 95},
    "sketch": {"x": 20, "y": 153, "w": 112, "h": 81},
}

def draw_text(draw, field, text, font):
    if not text or field not in FIELDS:
        return
    p = FIELDS[field]
    x, y = mm(p["x"], p["y"])
    y += BASELINE_OFFSET
    draw.text((x, y), str(text), font=font, fill="black")

def draw_checkbox(draw, field, checked):
    if not checked or field not in FIELDS:
        return
    p = FIELDS[field]
    x, y = mm(p["x"], p["y"])
    size = mm_w(5)
    dot = int(size * 0.55)
    offset = (size - dot) // 2
    draw.ellipse([x+offset, y+offset, x+offset+dot, y+offset+dot], fill=(220,0,0))

def draw_paragraph(draw, field, text, font):
    if not text:
        return
    p = FIELDS[field]
    x, y = mm(p["x"], p["y"])
    y += BASELINE_OFFSET
    lines = textwrap.wrap(text, width=65)
    spacing = mm_h(6.2)
    for i, line in enumerate(lines[:4]):
        draw.text((x, y + i*spacing), line, font=font, fill="black")

def paste_sketch(bg, file):
    if not file:
        return
    p = FIELDS["sketch"]
    img = Image.open(file).convert("RGB")
    img.thumbnail((mm_w(p["w"]), mm_h(p["h"])))
    x, y = mm(p["x"], p["y"])
    bg.paste(img, (x, y))

def render_image(data):
    bg = Image.open("form-bg.png").convert("RGB")
    draw = ImageDraw.Draw(bg)
    font = ImageFont.truetype("THSarabunNew.ttf", 90)

    draw_text(draw,"request_dept",data["dept"],font)
    draw_text(draw,"requester",data["requester"],font)
    draw_text(draw,"approver",data["approver"],font)
    draw_text(draw,"receive_date",data["received"],font)
    draw_text(draw,"due_date",data["due"],font)
    draw_text(draw,"project_name",data["title"],font)
    draw_text(draw,"project_size",data["size"],font)
    draw_paragraph(draw,"detail",data["desc"],font)
    draw_text(draw,"designer",data["designer"],font)
    draw_text(draw,"designer_date",data["designer_date"],font)
    draw_text(draw,"approve2",data["approve2"],font)
    draw_text(draw,"approve2_date",data["approve2_date"],font)

    for cb in ["cb_print","cb_online","cb_booth","cb_other","cb_normal","cb_urgent"]:
        draw_checkbox(draw,cb,data[cb])

    if data["cb_other"]:
        draw_text(draw,"other_text",data["other_text"],font)

    paste_sketch(bg,data["sketch"])
    return bg

def export_pdf(img):
    buf = io.BytesIO()
    img.save(buf, format="PDF", resolution=300.0)
    return buf

# ===============================
# STREAMLIT UI
# ===============================
st.set_page_config("Creative Brief Generator")
st.title("📝 Creative Brief Generator")

with st.form("form"):

    dept = st.text_input("หน่วยงาน")
    requester = st.text_input("ผู้ขอ")
    approver = st.text_input("ผู้บังคับบัญชา")
    received = st.text_input("วันที่รับ")
    due = st.text_input("วันที่ต้องการ")

    st.markdown("### รูปแบบงาน")
    cb_print = st.checkbox("ออกแบบสื่อสิ่งพิมพ์")
    cb_online = st.checkbox("ออกแบบสื่อ Online")
    cb_booth = st.checkbox("ออกแบบบูธ")
    cb_other = st.checkbox("อื่นๆ")
    other_text = st.text_input("ระบุ")

    st.markdown("### ประเภทงาน")
    cb_normal = st.checkbox("งานปกติ")
    cb_urgent = st.checkbox("งานด่วน")

    title = st.text_input("ชื่องาน")
    size = st.text_input("ขนาด")
    desc = st.text_area("รายละเอียด")

    designer = st.text_input("ผู้ออกแบบ")
    designer_date = st.text_input("วันที่ (ผู้ออกแบบ)")
    approve2 = st.text_input("ผู้อนุมัติ")
    approve2_date = st.text_input("วันที่ (ผู้อนุมัติ)")
    sketch = st.file_uploader("แนบ Sketch", ["png","jpg"])

    submit = st.form_submit_button("👀 Preview + บันทึก")

if submit:

    data = {
        "dept": dept,
        "requester": requester,
        "approver": approver,
        "received": received,
        "due": due,
        "title": title,
        "size": size,
        "desc": desc,
        "designer": designer,
        "designer_date": designer_date,
        "approve2": approve2,
        "approve2_date": approve2_date,
        "cb_print": cb_print,
        "cb_online": cb_online,
        "cb_booth": cb_booth,
        "cb_other": cb_other,
        "cb_normal": cb_normal,
        "cb_urgent": cb_urgent,
        "other_text": other_text,
        "sketch": sketch
    }

    # ส่งข้อมูลไป Google Sheet
    try:
        payload = data.copy()
        payload.pop("sketch")  # ไม่ส่งรูป
        requests.post(
            WEBHOOK_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        st.success("✅ บันทึกลง Google Sheet และ Backup สำเร็จ")
    except:
        st.error("❌ ไม่สามารถส่งข้อมูลไป Google Sheet")

    img = render_image(data)
    st.image(img, use_container_width=True)

    pdf = export_pdf(img)
    st.download_button("⬇️ ดาวน์โหลด PDF",
                       pdf.getvalue(),
                       "CreativeBrief.pdf",
                       "application/pdf")
