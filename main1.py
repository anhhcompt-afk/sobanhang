import json
import os
import tkinter as tk
from tkinter import messagebox, ttk

DATA_FILE = "ban_hang_data.json"


class SalesApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Ứng Dụng Sổ Bán Hàng")
    self.root.geometry("850x600")

    # Dữ liệu
    self.products = {}  # {ten_sp: {"price": gia, "qty": soluong}}
    self.orders = []  # Danh sách đơn hàng

    self.load_data()

    # Giao diện chính chia làm các Tab
    self.notebook = ttk.Notebook(root)
    self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Tab 1: Tạo đơn hàng & Bán hàng
    self.tab_sales = ttk.Frame(self.notebook)
    self.notebook.add(self.tab_sales, text="🛒 Bán Hàng")
    self.setup_sales_tab()

    # Tab 2: Quản lý sản phẩm (Kho)
    self.tab_inventory = ttk.Frame(self.notebook)
    self.notebook.add(self.tab_inventory, text="📦 Quản Lý Kho")
    self.setup_inventory_tab()

    # Tab 3: Lịch sử đơn hàng
    self.tab_history = ttk.Frame(self.notebook)
    self.notebook.add(self.tab_history, text="📜 Lịch Sử Đơn Hàng")
    self.setup_history_tab()

  # ================= TAB 1: BÁN HÀNG =================
  def setup_sales_tab(self):
    frame_left = ttk.LabelFrame(
        self.tab_sales, text="Chọn sản phẩm", padding=10
    )
    frame_left.pack(
        side="left", fill="both", expand=True, padx=5, pady=5
    )

    ttk.Label(frame_left, text="Chọn sản phẩm:").pack(
        anchor="w", pady=(0, 5)
    )
    self.product_combobox = ttk.Combobox(
        frame_left, state="readonly", width=30
    )
    self.product_combobox.pack(anchor="w", pady=(0, 10))
    self.update_product_combobox()

    ttk.Label(frame_left, text="Số lượng:").pack(anchor="w", pady=(0, 5))
    self.qty_entry = ttk.Entry(frame_left, width=15)
    self.qty_entry.insert(0, "1")
    self.qty_entry.pack(anchor="w", pady=(0, 10))

    add_btn = ttk.Button(
        frame_left, text="➕ Thêm vào đơn", command=self.add_to_cart
    )
    add_btn.pack(anchor="w", pady=5)

    # Giỏ hàng bên phải tab bán hàng
    frame_right = ttk.LabelFrame(
        self.tab_sales, text="Chi tiết đơn hàng", padding=10
    )
    frame_right.pack(
        side="right", fill="both", expand=True, padx=5, pady=5
    )

    columns = ("name", "price", "qty", "total")
    self.cart_tree = ttk.Treeview(
        frame_right, columns=columns, show="headings", height=12
    )
    self.cart_tree.heading("name", text="Tên sản phẩm")
    self.cart_tree.heading("price", text="Đơn giá")
    self.cart_tree.heading("qty", text="Số lượng")
    self.cart_tree.heading("total", text="Thành tiền")

    self.cart_tree.column("name", width=150)
    self.cart_tree.column("price", width=80, anchor="e")
    self.cart_tree.column("qty", width=60, anchor="center")
    self.cart_tree.column("total", width=90, anchor="e")
    self.cart_tree.pack(fill="both", expand=True, pady=(0, 10))

    self.total_label = ttk.Label(
        frame_right,
        text="Tổng tiền: 0 VNĐ",
        font=("Arial", 12, "bold"),
        foreground="red",
    )
    self.total_label.pack(anchor="e", pady=(0, 10))

    checkout_btn = ttk.Button(
        frame_right, text="✅ Thanh toán & Lưu đơn", command=self.checkout
    )
    checkout_btn.pack(anchor="e")

  # ================= TAB 2: QUẢN LÝ KHO =================
  def setup_inventory_tab(self):
    frame_form = ttk.LabelFrame(
        self.tab_inventory, text="Thông tin sản phẩm", padding=10
    )
    frame_form.pack(fill="x", padx=5, pady=5)

    ttk.Label(frame_form, text="Tên sản phẩm:").grid(
        row=0, column=0, sticky="w", pady=5
    )
    self.inv_name_entry = ttk.Entry(frame_form, width=25)
    self.inv_name_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame_form, text="Giá bán (VNĐ):").grid(
        row=1, column=0, sticky="w", pady=5
    )
    self.inv_price_entry = ttk.Entry(frame_form, width=25)
    self.inv_price_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(frame_form, text="Số lượng tồn:").grid(
        row=2, column=0, sticky="w", pady=5
    )
    self.inv_qty_entry = ttk.Entry(frame_form, width=25)
    self.inv_qty_entry.grid(row=2, column=1, padx=5, pady=5)

    save_prod_btn = ttk.Button(
        frame_form, text="💾 Lưu sản phẩm", command=self.save_product
    )
    save_prod_btn.grid(row=3, column=0, columnspan=2, pady=10)

    # Bảng danh sách sản phẩm
    columns = ("name", "price", "qty")
    self.inv_tree = ttk.Treeview(
        self.tab_inventory, columns=columns, show="headings", height=10
    )
    self.inv_tree.heading("name", text="Tên sản phẩm")
    self.inv_tree.heading("price", text="Giá bán")
    self.inv_tree.heading("qty", text="Số lượng tồn")
    self.inv_tree.pack(fill="both", expand=True, padx=5, pady=5)

    self.update_inventory_table()

  # ================= TAB 3: LỊCH SỬ ĐƠN HÀNG =================
  def setup_history_tab(self):
    columns = ("id", "time", "items", "total")
    self.history_tree = ttk.Treeview(
        self.tab_history, columns=columns, show="headings", height=15
    )
    self.history_tree.heading("id", text="Mã đơn")
    self.history_tree.heading("time", text="Thời gian")
    self.history_tree.heading("items", text="Chi tiết sản phẩm")
    self.history_tree.heading("total", text="Tổng tiền")

    self.history_tree.column("id", width=60, anchor="center")
    self.history_tree.column("time", width=140, anchor="center")
    self.history_tree.column("items", width=350)
    self.history_tree.column("total", width=100, anchor="e")
    self.history_tree.pack(fill="both", expand=True, padx=5, pady=5)

    self.update_history_table()

  # ================= CÁC HÀM XỬ LÝ LOGIC =================
  def load_data(self):
    if os.path.exists(DATA_FILE):
      try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
          data = json.load(f)
          self.products = data.get("products", {})
          self.orders = data.get("orders", [])
      except:
        pass

  def save_data(self):
    data = {"products": self.products, "orders": self.orders}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
      json.dump(data, f, ensure_ascii=False, indent=4)

  def update_product_combobox(self):
    product_list = [
        f"{name} (Còn: {info['qty']})" for name, info in self.products.items()
    ]
    self.product_combobox["values"] = product_list

  def update_inventory_table(self):
    for item in self.inv_tree.get_children():
      self.inv_tree.delete(item)
    for name, info in self.products.items():
      self.inv_tree.insert(
          "",
          "end",
          values=(
              name,
              f"{info['price']:,.0f} VNĐ".replace(",", "."),
              info["qty"],
          ),
      )

  def update_history_table(self):
    for item in self.history_tree.get_children():
      self.history_tree.delete(item)
    for order in reversed(self.orders):
      items_str = ", ".join(
          [
              f"{i['name']} (x{i['qty']})"
              for i in order["items"]
          ]
      )
      self.history_tree.insert(
          "",
          "end",
          values=(
              order["id"],
              order["time"],
              items_str,
              f"{order['total']:,.0f} VNĐ".replace(",", "."),
          ),
      )

  def save_product(self):
    name = self.inv_name_entry.get().strip()
    price_str = self.inv_price_entry.get().strip()
    qty_str = self.inv_qty_entry.get().strip()

    if not name or not price_str or not qty_str:
      messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin sản phẩm!")
      return

    try:
      price = float(price_str)
      qty = int(qty_str)
    except ValueError:
      messagebox.showerror("Lỗi", "Giá và số lượng phải là số!")
      return

    self.products[name] = {"price": price, "qty": qty}
    self.save_data()
    self.update_inventory_table()
    self.update_product_combobox()

    self.inv_name_entry.delete(0, tk.END)
    self.inv_price_entry.delete(0, tk.END)
    self.inv_qty_entry.delete(0, tk.END)
    messagebox.addAction = messagebox.showinfo(
        "Thành công", f"Đã lưu sản phẩm {name}!"
    )

  def add_to_cart(self):
    selection = self.product_combobox.get()
    if not selection:
      messagebox.showerror("Lỗi", "Vui lòng chọn sản phẩm!")
      return

    # Lấy tên sản phẩm từ chuỗi combobox "Tên (Còn: X)"
    name = selection.split(" (Còn:")[0]
    try:
      qty_to_buy = int(self.qty_entry.get())
      if qty_to_buy <= 0:
        raise ValueError
    except ValueError:
      messagebox.showerror("Lỗi", "Số lượng mua phải là số nguyên lớn hơn 0!")
      return

    current_stock = self.products[name]["qty"]
    if qty_to_buy > current_stock:
      messagebox.showerror(
          "Lỗi", f"Số lượng tồn kho không đủ! (Chỉ còn {current_stock})"
      )
      return

    price = self.products[name]["price"]
    total_price = price * qty_to_buy

    # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa, nếu có thì cộng dồn
    existing_item = None
    for child in self.cart_tree.get_children():
      item_vals = self.cart_tree.item(child, "values")
      if item_vals[0] == name:
        existing_item = child
        break

    if existing_item:
      old_vals = self.cart_tree.item(existing_item, "values")
      new_qty = int(old_vals[2]) + qty_to_buy
      if new_qty > current_stock:
        messagebox.showerror("Lỗi", "Tổng số lượng vượt quá tồn kho!")
        return
      new_total = new_qty * price
      self.cart_tree.item(
          existing_item,
          values=(
              name,
              f"{price:,.0f}".replace(",", "."),
              new_qty,
              f"{new_total:,.0f}".replace(",", "."),
          ),
      )
    else:
      self.cart_tree.insert(
          "",
          "end",
          values=(
              name,
              f"{price:,.0f}".replace(",", "."),
              qty_to_buy,
              f"{total_price:,.0f}".replace(",", "."),
          ),
      )

    self.calculate_cart_total()

  def calculate_cart_total(self):
    total = 0
    for child in self.cart_tree.get_children():
      vals = self.cart_tree.item(child, "values")
      # Chuyển đổi định dạng tiền tệ về số để cộng
      item_total = float(vals[3].replace(".", "").replace(" VNĐ", ""))
      total += item_total
    self.total_label.config(
        text=f"Tổng tiền: {total:,.0f} VNĐ".replace(",", ".")
    )

  def checkout(self):
    children = self.cart_tree.get_children()
    if not children:
      messagebox.showerror("Lỗi", "Giỏ hàng trống!")
      return

    import datetime

    order_items = []
    order_total = 0

    for child in children:
      vals = self.cart_tree.item(child, "values")
      name = vals[0]
      price = float(vals[1].replace(".", ""))
      qty = int(vals[2])
      item_total = float(vals[3].replace(".", ""))

      order_items.append(
          {"name": name, "price": price, "qty": qty, "total": item_total}
      )
      order_total += item_total

      # Trừ kho sản phẩm
      self.products[name]["qty"] -= qty

    # Tạo đơn hàng mới
    new_order = {
        id: len(self.orders) + 1,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": order_items,
        "total": order_total,
    }
    # Gán ID dạng số đơn hàng tăng dần
    new_order["id"] = len(self.orders) + 1

    self.orders.append(new_order)
    self.save_data()

    # Reset giỏ hàng và cập nhật giao diện
    for child in children:
      self.cart_tree.delete(child)
    self.total_label.config(text="Tổng tiền: 0 VNĐ")

    self.update_inventory_table()
    self.update_product_combobox()
    self.update_history_table()

    messagebox.showinfo("Thành công", "Thanh toán đơn hàng thành công!")


if __name__ == "__main__":
  root = tk.Tk()
  app = SalesApp(root)
  root.mainloop()
