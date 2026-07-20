#!/usr/bin/env python3
"""
PasswordGenerator — générateur de mots de passe et phrases de passe
local, sécurisé, sans connexion réseau.
"""

import secrets
import string
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib

AMBIGUOUS = "Il1O0"

WORDLIST = [
    "arbre","soleil","ballon","guitare","falaise","ordinateur","marmotte","biscuit",
    "chateau","riviere","nuage","chapeau","renard","bouteille","clavier","fenetre",
    "jardin","montagne","valise","lampe","crayon","tigre","ocean","navire","planete",
    "voyage","lumiere","musique","vallee","foret","ruisseau","fleur","oiseau",
    "ecureuil","chocolat","chambre","bureau","cahier","horloge","miroir","coussin",
    "chemise","pantalon","chaussure","desert","volcan","cascade","rivage","etoile",
    "comete","galaxie","satellite","fusee","navette","capsule","astronome","telescope",
    "boussole","lanterne","bougie","portail","escalier","grenier","cave","balcon",
    "terrasse","veranda","pelouse","potager","verger","ruche","miel"
]


class PasswordGeneratorWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="PasswordGenerator")
        self.set_default_size(600, 520)
        self.set_border_width(16)

        # Thème clair
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", False)

        self.load_css()

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(root)

        # Zone d'affichage
        display = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        root.pack_start(display, False, False, 0)

        self.entry = Gtk.Entry()
        self.entry.set_editable(False)
        self.entry.set_hexpand(True)
        self.entry.get_style_context().add_class("title-4")
        display.pack_start(self.entry, True, True, 0)

        self.btn_visibility = Gtk.Button()
        self.icon_visibility = Gtk.Image.new_from_icon_name("eye-not-looking-symbolic", Gtk.IconSize.BUTTON)
        self.btn_visibility.set_image(self.icon_visibility)
        self.btn_visibility.connect("clicked", self.toggle_visibility)
        display.pack_start(self.btn_visibility, False, False, 0)

        btn_copy = Gtk.Button()
        btn_copy.set_image(Gtk.Image.new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.BUTTON))
        btn_copy.connect("clicked", self.copy_to_clipboard)
        display.pack_start(btn_copy, False, False, 0)

        # Barre de force
        self.strength = Gtk.LevelBar()
        self.strength.set_min_value(0)
        self.strength.set_max_value(4)
        root.pack_start(self.strength, False, False, 0)

        self.strength_label = Gtk.Label(label="")
        self.strength_label.set_halign(Gtk.Align.START)
        root.pack_start(self.strength_label, False, False, 0)

        root.pack_start(Gtk.Separator(), False, False, 4)

        # Sections en plein écran
        fullscreen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        root.pack_start(fullscreen, True, True, 0)

        exp_classic = Gtk.Expander(label="Mot de passe classique")
        fullscreen.pack_start(exp_classic, False, False, 0)
        exp_classic.add(self.build_classic())

        exp_phrase = Gtk.Expander(label="Phrase de passe")
        fullscreen.pack_start(exp_phrase, False, False, 0)
        exp_phrase.add(self.build_passphrase())

        exp_adv = Gtk.Expander(label="Mode avancé")
        fullscreen.pack_start(exp_adv, False, False, 0)
        exp_adv.add(self.build_advanced())

        # Bouton générer
        btn_generate = Gtk.Button(label="Générer")
        btn_generate.get_style_context().add_class("suggested-action")
        btn_generate.connect("clicked", lambda w: self.generate())
        root.pack_start(btn_generate, False, False, 0)

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.generate()
        self.show_all()

    # ------------------------
    # CSS clair
    # ------------------------
    def load_css(self):
        css = Gtk.CssProvider()
        css.load_from_data(b"""
            * { font-size: 14px; }

            window { background: #fafafa; }

            entry {
                background: #ffffff;
                border: 1px solid #cccccc;
                padding: 6px;
                border-radius: 6px;
            }

            button {
                background: #e8e8e8;
                border-radius: 6px;
                padding: 6px 10px;
            }

            button:hover { background: #dcdcdc; }

            .suggested-action {
                background: #4a90e2;
                color: white;
                border-radius: 6px;
            }

            .suggested-action:hover { background: #3b7ac0; }

            expander {
                background: #ffffff;
                border: 1px solid #dddddd;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(screen, css, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    # ------------------------
    # Section classique
    # ------------------------
    def build_classic(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.pack_start(h, False, False, 0)
        h.pack_start(Gtk.Label(label="Longueur :"), False, False, 0)

        adj = Gtk.Adjustment(value=16, lower=6, upper=64, step_increment=1)
        self.spin_len = Gtk.SpinButton(adjustment=adj)
        h.pack_start(self.spin_len, False, False, 0)

        self.opt_upper = Gtk.CheckButton(label="Majuscules (A-Z)")
        self.opt_upper.set_active(True)
        box.pack_start(self.opt_upper, False, False, 0)

        self.opt_lower = Gtk.CheckButton(label="Minuscules (a-z)")
        self.opt_lower.set_active(True)
        box.pack_start(self.opt_lower, False, False, 0)

        self.opt_digits = Gtk.CheckButton(label="Chiffres (0-9)")
        self.opt_digits.set_active(True)
        box.pack_start(self.opt_digits, False, False, 0)

        self.opt_symbols = Gtk.CheckButton(label="Symboles (!@#$...)")
        self.opt_symbols.set_active(True)
        box.pack_start(self.opt_symbols, False, False, 0)

        self.opt_no_amb = Gtk.CheckButton(label="Exclure caractères ambigus")
        box.pack_start(self.opt_no_amb, False, False, 0)

        return box

    # ------------------------
    # Section phrase de passe
    # ------------------------
    def build_passphrase(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        info = Gtk.Label(label="Une phrase de passe est robuste et facile à retenir.")
        info.set_line_wrap(True)
        box.pack_start(info, False, False, 0)

        h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.pack_start(h, False, False, 0)
        h.pack_start(Gtk.Label(label="Nombre de mots :"), False, False, 0)

        adj = Gtk.Adjustment(value=4, lower=3, upper=10, step_increment=1)
        self.spin_words = Gtk.SpinButton(adjustment=adj)
        h.pack_start(self.spin_words, False, False, 0)

        return box

    # ------------------------
    # Section avancée
    # ------------------------
    def build_advanced(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self.opt_start_upper = Gtk.CheckButton(label="Commencer par une majuscule")
        box.pack_start(self.opt_start_upper, False, False, 0)

        self.opt_end_digit = Gtk.CheckButton(label="Terminer par un chiffre")
        box.pack_start(self.opt_end_digit, False, False, 0)

        self.opt_no_repeat = Gtk.CheckButton(label="Interdire les répétitions")
        box.pack_start(self.opt_no_repeat, False, False, 0)

        return box

    # ------------------------
    # Génération
    # ------------------------
    def generate(self):
        if self.spin_words.get_parent().get_parent().get_expanded():
            self.generate_passphrase()
        elif self.opt_start_upper.get_parent().get_parent().get_expanded():
            self.generate_advanced()
        else:
            self.generate_classic()

    def generate_classic(self):
        alphabet = ""
        if self.opt_upper.get_active(): alphabet += string.ascii_uppercase
        if self.opt_lower.get_active(): alphabet += string.ascii_lowercase
        if self.opt_digits.get_active(): alphabet += string.digits
        if self.opt_symbols.get_active(): alphabet += "!@#$%^&*()-_=+[]{};:,.?"

        if self.opt_no_amb.get_active():
            alphabet = "".join(c for c in alphabet if c not in AMBIGUOUS)

        length = self.spin_len.get_value_as_int()
        pwd = "".join(secrets.choice(alphabet) for _ in range(length))

        self.entry.set_text(pwd)
        self.update_strength(pwd, len(alphabet))

    def generate_passphrase(self):
        n = self.spin_words.get_value_as_int()
        words = [secrets.choice(WORDLIST) for _ in range(n)]
        pwd = "-".join(words)

        self.entry.set_text(pwd)
        entropy = n * (len(WORDLIST).bit_length() - 1)
        self.update_strength(pwd, len(WORDLIST), entropy)

    def generate_advanced(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
        length = self.spin_len.get_value_as_int()

        pwd = ""
        while len(pwd) < length:
            c = secrets.choice(alphabet)
            if self.opt_no_repeat.get_active() and pwd.endswith(c):
                continue
            pwd += c

        if self.opt_start_upper.get_active():
            pwd = pwd[0].upper() + pwd[1:]

        if self.opt_end_digit.get_active():
            pwd = pwd[:-1] + secrets.choice(string.digits)

        self.entry.set_text(pwd)
        self.update_strength(pwd, len(alphabet))

    # ------------------------
    # Utilitaires
    # ------------------------
    def update_strength(self, pwd, pool, custom=None):
        entropy = custom if custom is not None else len(pwd) * (pool.bit_length() - 1)

        if entropy < 40: lvl, txt = 1, "Faible"
        elif entropy < 70: lvl, txt = 2, "Correct"
        elif entropy < 100: lvl, txt = 3, "Fort"
        else: lvl, txt = 4, "Très fort"

        self.strength.set_value(lvl)
        self.strength_label.set_text(f"Force : {txt} (~{entropy} bits)")

    def toggle_visibility(self, w):
        vis = self.entry.get_visibility()
        self.entry.set_visibility(not vis)
        icon = "eye-not-looking-symbolic" if vis else "eye-open-negative-filled-symbolic"
        self.icon_visibility.set_from_icon_name(icon, Gtk.IconSize.BUTTON)

    def copy_to_clipboard(self, w):
        txt = self.entry.get_text()
        if not txt:
            return
        self.clipboard.set_text(txt, -1)
        self.clipboard.store()

        pop = Gtk.Popover.new(w)
        lbl = Gtk.Label(label="Copié !")
        lbl.set_margin_top(6)
        lbl.set_margin_bottom(6)
        lbl.set_margin_start(10)
        lbl.set_margin_end(10)
        pop.add(lbl)
        pop.show_all()
        pop.popup()
        GLib.timeout_add(1200, pop.popdown)


class PasswordGeneratorApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="fr.hastag.PasswordGenerator")

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = PasswordGeneratorWindow(self)
        win.present()


if __name__ == "__main__":
    PasswordGeneratorApp().run()
