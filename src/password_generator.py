#!/usr/bin/env python3
"""
Password Generator — génère des mots de passe robustes localement,
sans aucune connexion réseau.
"""

import secrets
import string

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk

AMBIGUOUS_CHARS = "Il1O0"


class PasswordGeneratorWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Générateur de mots de passe")
        self.set_default_size(420, 380)
        self.set_border_width(18)
        self.set_resizable(False)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.add(root)

        # --- Champ mot de passe + bouton copier -----------------------------
        pw_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        root.pack_start(pw_box, False, False, 0)

        self.password_entry = Gtk.Entry()
        self.password_entry.set_editable(False)
        self.password_entry.set_can_focus(True)
        self.password_entry.set_hexpand(True)
        self.password_entry.get_style_context().add_class("title-4")
        pw_box.pack_start(self.password_entry, True, True, 0)

        copy_button = Gtk.Button()
        copy_icon = Gtk.Image.new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.BUTTON)
        copy_button.set_image(copy_icon)
        copy_button.set_tooltip_text("Copier dans le presse-papiers")
        copy_button.connect("clicked", self.on_copy_clicked)
        pw_box.pack_start(copy_button, False, False, 0)

        # --- Indicateur de force ---------------------------------------------
        self.strength_bar = Gtk.LevelBar()
        self.strength_bar.set_min_value(0)
        self.strength_bar.set_max_value(4)
        root.pack_start(self.strength_bar, False, False, 0)

        self.strength_label = Gtk.Label(label="")
        self.strength_label.set_halign(Gtk.Align.START)
        root.pack_start(self.strength_label, False, False, 0)

        root.pack_start(Gtk.Separator(), False, False, 4)

        # --- Longueur -----------------------------------------------------------
        length_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        root.pack_start(length_box, False, False, 0)

        length_label = Gtk.Label(label="Longueur :")
        length_label.set_halign(Gtk.Align.START)
        length_box.pack_start(length_label, False, False, 0)

        adjustment = Gtk.Adjustment(value=16, lower=6, upper=64, step_increment=1)
        self.length_spin = Gtk.SpinButton(adjustment=adjustment)
        self.length_spin.set_numeric(True)
        self.length_spin.connect("value-changed", lambda w: self.generate_password())
        length_box.pack_start(self.length_spin, False, False, 0)

        # --- Options de composition --------------------------------------------
        options_frame = Gtk.Frame(label="Caractères inclus")
        root.pack_start(options_frame, False, False, 0)

        options_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        options_box.set_border_width(10)
        options_frame.add(options_box)

        self.check_upper = Gtk.CheckButton(label="Majuscules (A-Z)")
        self.check_upper.set_active(True)
        self.check_upper.connect("toggled", lambda w: self.generate_password())
        options_box.pack_start(self.check_upper, False, False, 0)

        self.check_lower = Gtk.CheckButton(label="Minuscules (a-z)")
        self.check_lower.set_active(True)
        self.check_lower.connect("toggled", lambda w: self.generate_password())
        options_box.pack_start(self.check_lower, False, False, 0)

        self.check_digits = Gtk.CheckButton(label="Chiffres (0-9)")
        self.check_digits.set_active(True)
        self.check_digits.connect("toggled", lambda w: self.generate_password())
        options_box.pack_start(self.check_digits, False, False, 0)

        self.check_symbols = Gtk.CheckButton(label="Symboles (!@#$...)")
        self.check_symbols.set_active(True)
        self.check_symbols.connect("toggled", lambda w: self.generate_password())
        options_box.pack_start(self.check_symbols, False, False, 0)

        self.check_no_ambiguous = Gtk.CheckButton(
            label="Exclure les caractères ambigus (l, I, 1, O, 0)"
        )
        self.check_no_ambiguous.set_active(False)
        self.check_no_ambiguous.connect("toggled", lambda w: self.generate_password())
        options_box.pack_start(self.check_no_ambiguous, False, False, 0)

        # --- Bouton générer -------------------------------------------------------
        generate_button = Gtk.Button(label="Générer un nouveau mot de passe")
        generate_button.get_style_context().add_class("suggested-action")
        generate_button.connect("clicked", lambda w: self.generate_password())
        root.pack_start(generate_button, False, False, 0)

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.generate_password()

        self.show_all()

    # -------------------------------------------------------------------------
    def build_alphabet(self):
        alphabet = ""
        if self.check_upper.get_active():
            alphabet += string.ascii_uppercase
        if self.check_lower.get_active():
            alphabet += string.ascii_lowercase
        if self.check_digits.get_active():
            alphabet += string.digits
        if self.check_symbols.get_active():
            alphabet += "!@#$%^&*()-_=+[]{};:,.?"

        if self.check_no_ambiguous.get_active():
            alphabet = "".join(c for c in alphabet if c not in AMBIGUOUS_CHARS)

        return alphabet

    def generate_password(self):
        alphabet = self.build_alphabet()
        length = self.length_spin.get_value_as_int()

        if not alphabet:
            self.password_entry.set_text("")
            self.strength_label.set_text("Sélectionnez au moins un type de caractère.")
            self.strength_bar.set_value(0)
            return

        password = "".join(secrets.choice(alphabet) for _ in range(length))
        self.password_entry.set_text(password)
        self.update_strength(password, alphabet)

    def update_strength(self, password, alphabet):
        pool_size = max(len(alphabet), 1)
        entropy_bits = len(password) * (pool_size.bit_length() - 1)

        if entropy_bits < 40:
            level, text = 1, "Faible"
        elif entropy_bits < 70:
            level, text = 2, "Correct"
        elif entropy_bits < 100:
            level, text = 3, "Fort"
        else:
            level, text = 4, "Très fort"

        self.strength_bar.set_value(level)
        self.strength_label.set_text(f"Force estimée : {text} (~{entropy_bits} bits d'entropie)")

    def on_copy_clicked(self, widget):
        text = self.password_entry.get_text()
        if not text:
            return
        self.clipboard.set_text(text, -1)
        self.clipboard.store()

        toast = Gtk.Popover.new(widget)
        label = Gtk.Label(label="Copié !")
        label.set_margin_top(6)
        label.set_margin_bottom(6)
        label.set_margin_start(10)
        label.set_margin_end(10)
        toast.add(label)
        toast.show_all()
        toast.popup()
        GLib.timeout_add(1200, toast.popdown)


class PasswordGeneratorApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="fr.hastag.PasswordGenerator")

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = PasswordGeneratorWindow(self)
        win.present()


def main():
    app = PasswordGeneratorApp()
    app.run()


if __name__ == "__main__":
    main()
