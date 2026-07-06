import json
import os
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.animation import Animation

KV = '''
Screen:
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: app.theme_cls.bg_normal

        MDTopAppBar:
            title: "Contacts"
            elevation: 0
            right_action_items: [["theme-light-dark", lambda x: app.toggle_theme()]]

        MDTextField:
            id: search
            hint_text: "Search..."
            mode: "round"
            size_hint_x: 0.9
            pos_hint: {"center_x": 0.5}
            on_text: app.search_contact(self.text)

        ScrollView:
            MDBoxLayout:
                id: contact_list
                orientation: "vertical"
                spacing: dp(8)
                padding: dp(12)
                size_hint_y: None
                height: self.minimum_height

        MDFloatingActionButton:
            icon: "plus"
            pos_hint: {"right": 0.95, "y": 0.03}
            on_release: app.open_add_dialog()
'''

FILE = "contacts.json"


class ContactApp(MDApp):
    contacts = []

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        self.screen = Builder.load_string(KV)
        self.load_contacts()
        return self.screen

    # 🌗 تغییر تم
    def toggle_theme(self):
        self.theme_cls.theme_style = (
            "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        )

    # 📥 لود
    def load_contacts(self):
        if os.path.exists(FILE):
            try:
                with open(FILE, "r") as f:
                    self.contacts = json.load(f)
            except:
                self.contacts = []
        self.sort_contacts()
        self.refresh_list()

    # 💾 ذخیره
    def save_contacts(self):
        with open(FILE, "w") as f:
            json.dump(self.contacts, f)

    # 🔤 مرتب‌سازی
    def sort_contacts(self):
        self.contacts.sort(key=lambda x: x["name"].lower())

    # 🔠 گروه‌بندی
    def group_contacts(self, data):
        grouped = {}
        for c in data:
            letter = c["name"][0].upper()
            grouped.setdefault(letter, []).append(c)
        return dict(sorted(grouped.items()))

    # 🔄 رفرش UI
    def refresh_list(self, data=None):
        container = self.screen.ids.contact_list
        container.clear_widgets()

        data = data if data else self.contacts
        grouped = self.group_contacts(data)

        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.fitimage import FitImage

        for letter, contacts in grouped.items():

            # 🔤 هدر A,B,C
            header = MDLabel(
                text=letter,
                bold=True,
                font_style="H6",
                size_hint_y=None,
                height=dp(28),
                theme_text_color="Secondary"
            )
            container.add_widget(header)

            for c in contacts:

                card = MDCard(
                    radius=[18],
                    elevation=0,
                    size_hint_y=None,
                    height=dp(72),
                    padding=(dp(12), dp(10)),
                    md_bg_color=self.theme_cls.bg_light
                )

                root = MDBoxLayout(
                    spacing=dp(12),
                    padding=(dp(4), 0)
                )

                avatar = FitImage(
                    source=c.get("image", "avatar.png"),
                    size_hint=(None, None),
                    size=(dp(44), dp(44)),
                    radius=[22],
                )

                text_box = MDBoxLayout(
                    orientation="vertical",
                    spacing=dp(2)
                )

                name = MDLabel(
                    text=c["name"],
                    font_style="H6"
                )

                phone = MDLabel(
                    text=c["phone"],
                    font_style="Body2",
                    theme_text_color="Secondary"
                )

                text_box.add_widget(name)
                text_box.add_widget(phone)

                root.add_widget(avatar)
                root.add_widget(text_box)
                card.add_widget(root)

                # 🎬 انیمیشن
                card.opacity = 0
                Animation(opacity=1, duration=0.2).start(card)

                # 👉 کلیک
                card.bind(on_release=lambda x, item=c: self.open_actions(item))

                # 👉 swipe حذف
                card.bind(on_touch_move=lambda w, touch, item=c: self.handle_swipe(w, touch, item))

                container.add_widget(card)

    # 🔍 جستجو
    def search_contact(self, text):
        filtered = [
            c for c in self.contacts
            if text.lower() in c["name"].lower()
        ]
        self.refresh_list(filtered)

    # ➕ افزودن
    def open_add_dialog(self):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.boxlayout import MDBoxLayout

        self.name_field = MDTextField(hint_text="Name", mode="round")
        self.phone_field = MDTextField(hint_text="Phone", mode="round")
        self.image_field = MDTextField(hint_text="Image path (optional)", mode="round")

        content = MDBoxLayout(
            orientation="vertical",
            spacing=15,
            size_hint_y=None,
            height=dp(220)
        )

        content.add_widget(self.name_field)
        content.add_widget(self.phone_field)
        content.add_widget(self.image_field)

        self.dialog = MDDialog(
            title="New Contact",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="SAVE", on_release=self.add_contact)
            ]
        )
        self.dialog.open()

    def add_contact(self, *args):
        name = self.name_field.text.strip()
        phone = self.phone_field.text.strip()
        image = self.image_field.text.strip() or "avatar.png"

        if name and phone:
            self.contacts.append({
                "name": name,
                "phone": phone,
                "image": image
            })
            self.sort_contacts()
            self.save_contacts()
            self.refresh_list()

        self.dialog.dismiss()

    # 📋 اکشن‌ها
    def open_actions(self, contact):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton

        self.selected_obj = contact

        self.dialog = MDDialog(
            title="Options",
            buttons=[
                MDFlatButton(text="Delete", on_release=self.delete_contact),
            ]
        )
        self.dialog.open()

    # 👉 swipe
    def handle_swipe(self, widget, touch, contact):
        if touch.dx < -40:
            self.contacts.remove(contact)
            self.save_contacts()
            self.refresh_list()

    # ❌ حذف
    def delete_contact(self, *args):
        if hasattr(self, "selected_obj"):
            self.contacts.remove(self.selected_obj)

        self.save_contacts()
        self.refresh_list()
        try:
            self.dialog.dismiss()
        except:
            pass


ContactApp().run()
