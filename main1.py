import datetime
import json
import os
import streamlit as st

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Sổ Bán Hàng Pro", page_icon="🛒", layout="wide"
)

DATA_FILE = "ban_hang_data.json"
VALID_KEYS = ["SBH-FREE-2026", "SBH-PRO-9999", "SBH-VIP-8888"]  # Danh sách Key kích hoạt mẫu


# Load & Save Data
def load_data():
  if os.path.exists(DATA_FILE):
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      pass
  return {"products": {}, "orders": []}


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


data = load_data()

# Quản lý trạng thái đăng nhập / Kích hoạt Key
if "is_activated" not in st.session_state:
  st.session_state.is_activated = False

# Sidebar: Bản quyền & Đăng ký gói
st.sidebar.title("🔐 Bản Quyền Ứng Dụng")

if not st.session_state.is_activated:
  license_key = st.sidebar.text_input(
      "Nhập License Key để sử dụng:", type="password"
  )
  if st.sidebar.button("Kích hoạt Key"):
    if license_key in VALID_KEYS:
      st.session_state.is_activated = True
      st.sidebar.success("Kích hoạt thành công! Bạn có thể sử dụng ứng dụng.")
      st.rerun()
    else:
      st.sidebar.error("Key không hợp lệ. Vui lòng kiểm tra lại!")

st.sidebar.markdown("---")
st.sidebar.subheader("💳 Đăng ký gói / Gia hạn")

with st.sidebar.expander("📌 Bảng giá các gói dịch vụ", expanded=False):
  st.markdown("""
    * **Gói Cơ Bản (1 Tháng):** `50.000 VNĐ`
    * **Gói Nâng Cao (6 Tháng):** `250.000 VNĐ`
    * **Gói VIP (1 Năm):** `450.000 VNĐ`
    """)

with st.sidebar.expander("🏦 Thông tin chuyển khoản", expanded=False):
  st.markdown("""
    * **Ngân hàng:** MB Bank (MB)
    * **Chủ tài khoản:** HOANG HAI AN
    * **Số tài khoản:** `0030132291981`
    * **Nội dung CK:** `<Số điện thoại của bạn> - <Tên gói>`
    """)
  st.info(
      "📌 **Lưu ý:** Sau khi chuyển khoản, vui lòng gửi thông tin đăng ký bên"
      " dưới hoặc liên hệ trực tiếp để nhận Key kích hoạt."
  )

# Form đăng ký nhận Key
with st.sidebar.form("register_form"):
  st.subheader("📩 Đăng ký nhận Key")
  user_phone = st.text_input("Số điện thoại nhận Key:")
  user_email = st.text_input("Email nhận Key:")
  selected_plan = st.selectbox(
      "Chọn gói dịch vụ:",
      ["Gói Cơ Bản (50k/tháng)", "Gói Nâng Cao (250k/6tháng)", "Gói VIP (450k/năm)"],
  )
  submitted = st.form_submit_button("Gửi thông tin đăng ký")

  if submitted:
    if user_phone or user_email:
      st.success(
          "Đã ghi nhận thông tin! Yêu cầu của bạn đã được gửi tới Quản trị"
          " viên."
      )
      st.caption(
          "📲 Hotline/Zalo hỗ trợ: **0964058714**\n📧 Email hỗ trợ:"
          " **anhh.compt@gmail.com**"
      )
    else:
      st.warning("Vui lòng nhập Số điện thoại hoặc Email!")

# GIAO DIỆN CHÍNH
st.title("🛒 Ứng Dụng Sổ Bán Hàng")

if not st.session_state.is_activated:
  st.warning(
      "⚠️ **Ứng dụng chưa được kích hoạt.** Vui lòng xem thông tin đăng ký gói"
      " dịch vụ ở thanh bên trái (Sidebar) để nhận Key kích hoạt!"
  )
else:
  tab_sales, tab_inventory, tab_history = st.tabs(
      ["🛒 Bán Hàng", "📦 Quản Lý Kho", "📜 Lịch Sử Đơn Hàng"]
  )

  # TAB 1: BÁN HÀNG
  with tab_sales:
    st.subheader("Tạo đơn hàng")
    if not data["products"]:
      st.info("Chưa có sản phẩm trong kho. Vui lòng thêm sản phẩm ở tab 'Quản Lý Kho'.")
    else:
      if "cart" not in st.session_state:
        st.session_state.cart = []

      col1, col2 = st.columns([1, 2])

      with col1:
        prod_options = [
            f"{name} (Tồn: {info['qty']} - Giá: {info['price']:,.0f}đ)"
            for name, info in data["products"].items()
        ]
        selected_prod_str = st.selectbox("Chọn sản phẩm", prod_options)
        selected_prod_name = selected_prod_str.split(" (Tồn:")[0]

        max_stock = data["products"][selected_prod_name]["qty"]
        qty = st.number_input("Số lượng", min_value=1, max_value=max(1, max_stock), value=1)

        if st.button("➕ Thêm vào giỏ hàng"):
          if max_stock < qty:
            st.error("Số lượng tồn kho không đủ!")
          else:
            st.session_state.cart.append({
                "name": selected_prod_name,
                "price": data["products"][selected_prod_name]["price"],
                "qty": qty,
                "total": data["products"][selected_prod_name]["price"] * qty,
            })
            st.success(f"Đã thêm {selected_prod_name} vào giỏ!")

      with col2:
        st.write("### Chi tiết giỏ hàng")
        if st.session_state.cart:
          total_order = sum(item["total"] for item in st.session_state.cart)
          st.dataframe(st.session_state.cart, use_container_width=True)
          st.markdown(f"### **Tổng tiền: {total_order:,.0f} VNĐ**")

          col_btn1, col_btn2 = st.columns(2)
          with col_btn1:
            if st.button("✅ Thanh Toán & Lưu Đơn", type="primary"):
              for item in st.session_state.cart:
                data["products"][item["name"]]["qty"] -= item["qty"]

              new_order = {
                  "id": len(data["orders"]) + 1,
                  "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  "items": st.session_state.cart,
                  "total": total_order,
              }
              data["orders"].append(new_order)
              save_data(data)
              st.session_state.cart = []
              st.success("Thanh toán đơn hàng thành công!")
              st.rerun()
          with col_btn2:
            if st.button("🗑️ Xóa giỏ hàng"):
              st.session_state.cart = []
              st.rerun()
        else:
          st.write("Giỏ hàng đang trống.")

  # TAB 2: QUẢN LÝ KHO
  with tab_inventory:
    st.subheader("Thêm/Cập nhật sản phẩm vào kho")
    with st.form("inventory_form"):
      p_name = st.text_input("Tên sản phẩm")
      p_price = st.number_input("Giá bán (VNĐ)", min_value=0.0, step=1000.0)
      p_qty = st.number_input("Số lượng nhập kho", min_value=0, step=1)
      submit_p = st.form_submit_button("💾 Lưu sản phẩm")

      if submit_p:
        if p_name:
          data["products"][p_name] = {"price": p_price, "qty": p_qty}
          save_data(data)
          st.success(f"Đã cập nhật sản phẩm: {p_name}")
          st.rerun()
        else:
          st.error("Vui lòng nhập tên sản phẩm!")

    st.subheader("Danh sách sản phẩm trong kho")
    if data["products"]:
      inv_list = [
          {"Tên sản phẩm": k, "Giá (VNĐ)": v["price"], "Số lượng tồn": v["qty"]}
          for k, v in data["products"].items()
      ]
      st.dataframe(inv_list, use_container_width=True)

  # TAB 3: LỊCH SỬ ĐƠN HÀNG
  with tab_history:
    st.subheader("Lịch sử giao dịch")
    if data["orders"]:
      history_display = []
      for o in reversed(data["orders"]):
        items_detail = ", ".join([f"{i['name']} (x{i['qty']})" for i in o["items"]])
        history_display.append({
            "Mã đơn": o["id"],
            "Thời gian": o["time"],
            "Chi tiết sản phẩm": items_detail,
            "Tổng tiền (VNĐ)": f"{o['total']:,.0f}",
        })
      st.dataframe(history_display, use_container_width=True)
    else:
      st.write("Chưa có đơn hàng nào được thực hiện.")
