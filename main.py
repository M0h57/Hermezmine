import os
import json
import socket
import threading

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, Line

# ── Colours ──────────────────────────────────────────────────────────────────
BG       = get_color_from_hex("#0d0f14")
SURFACE  = get_color_from_hex("#161922")
CARD     = get_color_from_hex("#1e2230")
ACCENT   = get_color_from_hex("#00c8ff")
ACCENT2  = get_color_from_hex("#0066ff")
DANGER   = get_color_from_hex("#ff3b5c")
SUCCESS  = get_color_from_hex("#00e5a0")
TEXT     = get_color_from_hex("#e8eaf0")
MUTED    = get_color_from_hex("#5a6070")

Window.clearcolor = BG

# ── Persistent storage ────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.expanduser("~"), ".hermez_data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"ips": [], "ports": ["9021", "9090"], "last_payload": ""}

def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

# ── Helpers ───────────────────────────────────────────────────────────────────
def make_btn(text, bg=CARD, color=TEXT, bold=False, height=dp(48), font_size=dp(14)):
    return Button(
        text=text,
        size_hint_y=None,
        height=height,
        background_normal="",
        background_color=bg,
        color=color,
        bold=bold,
        font_size=font_size
    )

def make_input(hint="", text="", password=False):
    return TextInput(
        hint_text=hint,
        text=text,
        size_hint_y=None,
        height=dp(44),
        multiline=False,
        background_color=CARD,
        foreground_color=TEXT,
        hint_text_color=MUTED,
        cursor_color=ACCENT,
        padding=[dp(12), dp(10)],
        font_size=dp(14),
        password=password
    )

def section_label(text):
    return Label(
        text=f"[color=#00c8ff][b]{text}[/b][/color]",
        markup=True,
        size_hint_y=None,
        height=dp(28),
        halign="left",
        font_size=dp(12)
    )

# ── Main Screen ───────────────────────────────────────────────────────────────
class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.data = load_data()
        self.selected_payload = self.data.get("last_payload", "")
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))

        # ── Header
        hdr = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        title = Label(
            text="[b][color=#00c8ff]HERMEZ[/color][color=#ffffff] LINK[/color][/b]",
            markup=True, font_size=dp(22),
            size_hint_x=0.7, halign="left"
        )
        title.bind(size=title.setter("text_size"))
        mgr_btn = make_btn("≡ MANAGE", bg=SURFACE, color=ACCENT,
                           height=dp(40), font_size=dp(12))
        mgr_btn.bind(on_press=lambda *_: self.go_manage())
        hdr.add_widget(title)
        hdr.add_widget(mgr_btn)
        root.add_widget(hdr)

        # ── Corrected Native Divider Line Widget
        divider = Label(size_hint_y=None, height=dp(2))
        def draw_divider(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*MUTED[:3], 0.3)
                Line(points=[instance.x, instance.y, instance.x + instance.width, instance.y], width=1)
        divider.bind(size=draw_divider, pos=draw_divider)
        root.add_widget(divider)

        # ── IP row
        root.add_widget(section_label("TARGET IP"))
        ip_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.ip_input = make_input("192.168.x.x",
                                   text=self.data["ips"][0] if self.data["ips"] else "")
        ip_pick = make_btn("▾", bg=ACCENT2, height=dp(44), font_size=dp(18))
        ip_pick.size_hint_x = 0.18
        ip_pick.bind(on_press=lambda *_: self.show_picker("ip"))
        ip_row.add_widget(self.ip_input)
        ip_row.add_widget(ip_pick)
        root.add_widget(ip_row)

        # ── Port row
        root.add_widget(section_label("PORT"))
        port_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.port_input = make_input("9021",
                                     text=self.data["ports"][0] if self.data["ports"] else "9021")
        port_pick = make_btn("▾", bg=ACCENT2, height=dp(44), font_size=dp(18))
        port_pick.size_hint_x = 0.18
        port_pick.bind(on_press=lambda *_: self.show_picker("port"))
        port_row.add_widget(self.port_input)
        port_row.add_widget(port_pick)
        root.add_widget(port_row)

        # ── Payload
        root.add_widget(section_label("PAYLOAD"))
        self.payload_label = Label(
            text=self._short_path(self.selected_payload) or "No file selected",
            color=MUTED if not self.selected_payload else TEXT,
            size_hint_y=None, height=dp(36),
            halign="left", font_size=dp(12),
            text_size=(Window.width - dp(32), None)
        )
        browse_btn = make_btn("📂  BROWSE PAYLOAD", bg=SURFACE, color=ACCENT,
                              height=dp(44))
        browse_btn.bind(on_press=lambda *_: self.browse_payload())
        root.add_widget(self.payload_label)
        root.add_widget(browse_btn)

        # ── Send button
        send_btn = make_btn("⚡  SEND PAYLOAD", bg=ACCENT, color=BG,
                            bold=True, height=dp(56), font_size=dp(16))
        send_btn.bind(on_press=lambda *_: self.send_payload())
        root.add_widget(send_btn)

        # ── Log
        root.add_widget(section_label("LOG"))
        log_scroll = ScrollView(size_hint=(1, 1))
        self.log_label = Label(
            text="Ready.\n",
            color=TEXT, markup=True,
            size_hint_y=None, font_size=dp(11),
            halign="left", valign="top"
        )
        self.log_label.bind(texture_size=self.log_label.setter("size"))
        log_scroll.add_widget(self.log_label)
        root.add_widget(log_scroll)

        self.add_widget(root)

    def _short_path(self, path):
        if not path:
            return ""
        return "…/" + os.path.basename(path)

    def log(self, msg, color="#e8eaf0"):
        def _update(dt):
            self.log_label.text += f"[color={color}]{msg}[/color]\n"
        Clock.schedule_once(_update)

    def go_manage(self):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "manage"
        self.manager.get_screen("manage").refresh()

    def show_picker(self, kind):
        data = load_data()
        items = data["ips"] if kind == "ip" else data["ports"]
        if not items:
            self.log(f"No saved {kind}s yet. Add them in Manage.", "#ff3b5c")
            return

        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        popup = Popup(title=f"Select {kind.upper()}", content=content,
                      size_hint=(0.85, 0.6),
                      background_color=SURFACE, title_color=ACCENT,
                      separator_color=ACCENT)

        for item in items:
            btn = make_btn(item, bg=CARD, color=TEXT)
            def _select(_, val=item, k=kind):
                if k == "ip":
                    self.ip_input.text = val
                else:
                    self.port_input.text = val
                popup.dismiss()
            btn.bind(on_press=_select)
            content.add_widget(btn)

        cancel = make_btn("CANCEL", bg=DANGER, color=TEXT)
        cancel.bind(on_press=popup.dismiss)
        content.add_widget(cancel)
        popup.open()

    def browse_payload(self):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        popup = Popup(title="Select .bin payload", content=content,
                      size_hint=(0.95, 0.85),
                      background_color=SURFACE, title_color=ACCENT,
                      separator_color=ACCENT)

        fc = FileChooserListView(
            filters=["*.bin", "*.BIN"],
            path=os.path.expanduser("~"),
            background_color=CARD
        )
        content.add_widget(fc)

        btn_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        sel_btn = make_btn("SELECT", bg=ACCENT, color=BG, bold=True)
        can_btn = make_btn("CANCEL", bg=DANGER)
        btn_row.add_widget(sel_btn)
        btn_row.add_widget(can_btn)
        content.add_widget(btn_row)

        def _select(_):
            if fc.selection:
                self.selected_payload = fc.selection[0]
                self.payload_label.text = self._short_path(self.selected_payload)
                self.payload_label.color = TEXT
                d = load_data()
                d["last_payload"] = self.selected_payload
                save_data(d)
                self.log(f"Payload: {os.path.basename(self.selected_payload)}", "#00e5a0")
            popup.dismiss()

        sel_btn.bind(on_press=_select)
        can_btn.bind(on_press=popup.dismiss)
        popup.open()

    def send_payload(self):
        ip   = self.ip_input.text.strip()
        port = self.port_input.text.strip()
        path = self.selected_payload

        if not ip:
            self.log("❌  No IP entered.", "#ff3b5c"); return
        if not port.isdigit():
            self.log("❌  Invalid port.", "#ff3b5c"); return
        if not path or not os.path.exists(path):
            self.log("❌  Payload file not found.", "#ff3b5c"); return

        self.log(f"→  Connecting to {ip}:{port} …", "#00c8ff")
        threading.Thread(target=self._send_thread,
                         args=(ip, int(port), path), daemon=True).start()

    def _send_thread(self, ip, port, path):
        try:
            with open(path, "rb") as f:
                data = f.read()
            size = len(data)
            self.log(f"   Payload size: {size:,} bytes")

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((ip, port))
            self.log(f"✔  Connected.", "#00e5a0")

            sent = 0
            chunk = 4096
            while sent < size:
                end  = min(sent + chunk, size)
                sock.sendall(data[sent:end])
                sent = end

            sock.close()
            self.log(f"✔  Sent {sent:,} bytes successfully!", "#00e5a0")
        except ConnectionRefusedError:
            self.log("❌  Connection refused. PS5 may not be in exploit mode.", "#ff3b5c")
        except socket.timeout:
            self.log("❌  Timed out. Check IP and network.", "#ff3b5c")
        except Exception as e:
            self.log(f"❌  Error: {e}", "#ff3b5c")


# ── Manage Screen ─────────────────────────────────────────────────────────────
class ManageScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.build_ui()

    def build_ui(self):
        self.root_layout = BoxLayout(orientation="vertical",
                                     padding=dp(16), spacing=dp(10))

        # Header
        hdr = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))
        back = make_btn("← BACK", bg=SURFACE, color=ACCENT,
                        height=dp(40), font_size=dp(12))
        back.size_hint_x = 0.3
        back.bind(on_press=lambda *_: self.go_back())
        title = Label(text="[b][color=#00c8ff]MANAGE[/color][/b]",
                      markup=True, font_size=dp(20))
        hdr.add_widget(back)
        hdr.add_widget(title)
        self.root_layout.add_widget(hdr)

        # IPs section
        self.root_layout.add_widget(section_label("SAVED IPs"))
        ip_add_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.new_ip = make_input("Add new IP…")
        add_ip_btn = make_btn("+", bg=SUCCESS, color=BG, bold=True,
                              height=dp(44), font_size=dp(18))
        add_ip_btn.size_hint_x = 0.18
        add_ip_btn.bind(on_press=lambda *_: self.add_item("ip"))
        ip_add_row.add_widget(self.new_ip)
        ip_add_row.add_widget(add_ip_btn)
        self.root_layout.add_widget(ip_add_row)

        ip_scroll = ScrollView(size_hint=(1, 0.3))
        self.ip_list = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.ip_list.bind(minimum_height=self.ip_list.setter("height"))
        ip_scroll.add_widget(self.ip_list)
        self.root_layout.add_widget(ip_scroll)

        # Ports section
        self.root_layout.add_widget(section_label("SAVED PORTS"))
        port_add_row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.new_port = make_input("Add port number…")
        add_port_btn = make_btn("+", bg=SUCCESS, color=BG, bold=True,
                                height=dp(44), font_size=dp(18))
        add_port_btn.size_hint_x = 0.18
        add_port_btn.bind(on_press=lambda *_: self.add_item("port"))
        port_add_row.add_widget(self.new_port)
        port_add_row.add_widget(add_port_btn)
        self.root_layout.add_widget(port_add_row)

        port_scroll = ScrollView(size_hint=(1, 0.25))
        self.port_list = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.port_list.bind(minimum_height=self.port_list.setter("height"))
        port_scroll.add_widget(self.port_list)
        self.root_layout.add_widget(port_scroll)

        self.add_widget(self.root_layout)

    def refresh(self):
        data = load_data()
        self._populate(self.ip_list,   data["ips"],   "ip")
        self._populate(self.port_list, data["ports"], "port")

    def _populate(self, grid, items, kind):
        grid.clear_widgets()
        for item in items:
            row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
            lbl = Label(text=item, color=TEXT,
                        font_size=dp(13), halign="left", size_hint_x=0.75)
            lbl.bind(size=lbl.setter("text_size"))
            del_btn = make_btn("✕", bg=DANGER, color=TEXT,
                               height=dp(42), font_size=dp(14))
            del_btn.size_hint_x = 0.25
            del_btn.bind(on_press=lambda _, v=item, k=kind: self.delete_item(k, v))
            row.add_widget(lbl)
            row.add_widget(del_btn)
            grid.add_widget(row)

    def add_item(self, kind):
        val = (self.new_ip if kind == "ip" else self.new_port).text.strip()
        if not val:
            return
        data = load_data()
        lst = data["ips"] if kind == "ip" else data["ports"]
        if val not in lst:
            lst.append(val)
            save_data(data)
        (self.new_ip if kind == "ip" else self.new_port).text = ""
        self.refresh()

    def delete_item(self, kind, val):
        data = load_data()
        lst = data["ips"] if kind == "ip" else data["ports"]
        if val in lst:
            lst.remove(val)
            save_data(data)
        self.refresh()

    def go_back(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "main"
        self.manager.get_screen("main").data = load_data()


# ── App ────────────────────────────────────────────────────────────────────────
class HermezApp(App):
    def build(self):
        self.title = "Hermez Link"
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(ManageScreen(name="manage"))
        return sm


if __name__ == "__main__":
    HermezApp().run()
