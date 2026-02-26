import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

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

# ===============================
# SAFE ZONE
# ===============================
SAFE_ZONE = {
    "x1": 0,
    "y1": 0,
    "x2": 210,
    "y2": 50
}

# ===============================
# FIELD POSITIONS (ใช้ของคุณล่าสุด)
# ===============================
FIELDS = {

    "request_dept": {"x": 47, "y": 63},
    "doc_ref": {"x": 145, "y": 63},

    "requester": {"x": 47, "y": 70},
    "receive_date": {"x": 147, "y": 70},

    "approver": {"x": 55, "y": 78},
    "due_date": {"x": 149, "y": 78},

    "project_name": {"x": 36, "y": 103},
    "project_size": {"x": 128, "y": 103},

    "cb_print": {"x": 40, "y": 92},
    "cb_booth": {"x": 75, "y": 92},
    "cb_online": {"x": 40, "y": 99},
    "cb_other": {"x": 75, "y": 99},

    "cb_normal": {"x": 140, "y": 92},
    "cb_urgent": {"x": 140, "y": 99},

    "other_text": {"x": 100, "y": 95},

    "detail": {"x": 63, "y": 110},

    "designer": {"x": 35, "y": 238},
    "designer_date": {"x": 107, "y": 237},

    "approve2": {"x": 53, "y": 245},
    "approve2_date": {"x": 107, "y": 245},

    "sketch": {"x": 20, "y": 153, "w": 112, "h": 81},
}

# ===============================
# HELPERS
# ===============================
def is_in_safe_zone(x_mm, y_mm):
    return (
        SAFE_ZONE["x1"] <= x_mm <= SAFE_ZONE["x2"] and
        SAFE_ZONE["y1"] <= y_mm <= SAFE_ZONE["y2"]
    )

def draw_text(draw, field, text, font, align="left"):

    if not text or field not in FIELDS:
        return

    p = FIELDS[field]

    if is_in_safe_zone(p["x"], p["y"]):
        return

    x, y = mm(p["x"], p["y"])
    y += BASELINE_OFFSET

    if align == "right":
        text_width = draw.textlength(str(text), font=font)
        x -= text_width

    draw.text((x, y), str(text), font=font, fill="black")


def draw_checkbox(draw, field, checked):

    if not checked or field not in FIELDS:
        return

    p = FIELDS[field]
    x, y = mm(p["x"], p["y"])

    box_size = mm_w(5)
    dot_size = int(box_size * 0.55)

    offset_x = (box_size - dot_size) // 2
    offset_y = (box_size - dot_size) // 2

    left = x + offset_x
    top = y + offset_y
    right = left + dot_size
    bottom = top + dot_size

    draw.ellipse([left, top, right, bottom], fill=(220, 0, 0))


def draw_paragraph(draw, field, text, font):

    if not text or field not in FIELDS:
        return

    p = FIELDS[field]
    x_start, y_start = mm(p["x"], p["y"])
    y_start += BASELINE_OFFSET

    lines = textwrap.wrap(text, width=65)
    spacing = mm_h(6.2)

    for i, line in enumerate(lines[:4]):
        y = y_start + (i * spacing)
        draw.text((x_start, y), line, font=font, fill="black")


def paste_sketch(bg, file):

    if not file:
        return

    p = FIELDS["sketch"]
    img = Image.open(file).convert("RGB")
    img.thumbnail((mm_w(p["w"]), mm_h(p["h"])))

    x, y = mm(p["x"], p["y"])
    bg.paste(img, (x, y))


# ===============================
# RENDER IMAGE
# ===============================
def render_image(data):

    bg = Image.open("form-bg.png").convert("RGB")
    draw = ImageDraw.Draw(bg)

    FONT = ImageFont.truetype("THSarabunNew.ttf", 90)
    FONT_BIG = ImageFont.truetype("THSarabunNew.ttf", 145)

    draw_text(draw, "request_dept", data.get("dept"), FONT)
    draw_text(draw, "requester", data.get("requester"), FONT)
    draw_text(draw, "receive_date", data.get("date"), FONT)

    draw_text(draw, "approver", data.get("approver"), FONT)
    draw_text(draw, "due_date", data.get("due"), FONT)

    draw_text(draw, "project_name", data.get("title"), FONT)
    draw_text(draw, "project_size", data.get("size"), FONT)

    draw_paragraph(draw, "detail", data.get("desc"), FONT)

    draw_text(draw, "designer", data.get("designer"), FONT)
    draw_text(draw, "designer_date", data.get("designer_date"), FONT)

    draw_text(draw, "approve2", data.get("approve2"), FONT)
    draw_text(draw, "approve2_date", data.get("approve2_date"), FONT)

    draw_checkbox(draw, "cb_print", data.get("cb_print"))
    draw_checkbox(draw, "cb_online", data.get("cb_online"))
    draw_checkbox(draw, "cb_booth", data.get("cb_booth"))
    draw_checkbox(draw, "cb_other", data.get("cb_other"))
    draw_checkbox(draw, "cb_normal", data.get("cb_normal"))
    draw_checkbox(draw, "cb_urgent", data.get("cb_urgent"))

    if data.get("cb_other"):
        draw_text(draw, "other_text", data.get("other_text"), FONT)

    paste_sketch(bg, data.get("sketch"))

    return bg


# ===============================
# EXPORT PDF
# ===============================
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

    col1, col2, col3 = st.columns(3)
    with col1:
        dept = st.text_input("หน่วยงาน")
    with col2:
        requester = st.text_input("ผู้ขอ")
    with col3:
        approver = st.text_input("ผู้บังคับบัญชา")

    col4, col5, col6 = st.columns(3)
    with col4:
        doc_no = st.text_input("เลขที่เอกสาร")
    with col5:
        received = st.text_input("วันที่รับ")
    with col6:
        due = st.text_input("วันที่ต้องการ")

    st.markdown("### รูปแบบงาน")
    col7, col8 = st.columns(2)
    with col7:
        cb_print = st.checkbox("ออกแบบสื่อสิ่งพิมพ์")
        cb_online = st.checkbox("ออกแบบสื่อ Online")
    with col8:
        cb_booth = st.checkbox("ออกแบบบูธ")
        cb_other = st.checkbox("อื่นๆ")
        other_text = st.text_input("ระบุ")

    st.markdown("### ประเภทงาน")
    col9, col10 = st.columns(2)
    with col9:
        cb_normal = st.checkbox("งานปกติ")
    with col10:
        cb_urgent = st.checkbox("งานด่วน")

    col11, col12 = st.columns(2)
    with col11:
        title = st.text_input("ชื่องาน")
    with col12:
        size = st.text_input("ขนาด")

    desc = st.text_area("รายละเอียด (สูงสุด 4 บรรทัด)")

    col13, col14, col15, col16 = st.columns(4)
    with col13:
        designer = st.text_input("ผู้ออกแบบ")
    with col14:
        designer_date = st.text_input("วันที่ (ผู้ออกแบบ)")
    with col15:
        approve2 = st.text_input("ผู้อนุมัติ")
    with col16:
        approve2_date = st.text_input("วันที่ (ผู้อนุมัติ)")

    sketch = st.file_uploader("แนบ Sketch", ["png", "jpg"])

    submit = st.form_submit_button("👀 Preview เอกสาร")


# ===============================
# PREVIEW
# ===============================
if submit:

    data = {
        "dept": dept,
        "requester": requester,
        "approver": approver,
        "date": received,
        "due": due,
        "title": title,
        "size": size,
        "desc": desc,
        "designer": designer,
        "designer_date": designer_date,
        "approve2": approve2,
        "approve2_date": approve2_date,
        "sketch": sketch,
        "cb_print": cb_print,
        "cb_online": cb_online,
        "cb_booth": cb_booth,
        "cb_other": cb_other,
        "cb_normal": cb_normal,
        "cb_urgent": cb_urgent,
        "other_text": other_text,
    }

    img = render_image(data)

    st.image(img, use_container_width=True)

    pdf = export_pdf(img)

    st.download_button(
        "⬇️ ดาวน์โหลด PDF",
        pdf.getvalue(),
        "CreativeBrief.pdf",
        "application/pdf"
    )
