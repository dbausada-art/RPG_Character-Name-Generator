"""RPG Character Name Generator — Modern Desktop GUI"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import sys
import os
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from generador import generar_nombre
from utils import cargar_razas

# ── Persistence ───────────────────────────────────────────────────────────────
CONFIG_PATH = os.path.join(BASE_DIR, ".gui_config.json")

def _load_config() -> dict:
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {"appearance": "Dark", "color_theme": "blue"}

def _save_config(cfg: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

# ── Race metadata ─────────────────────────────────────────────────────────────
RACES_META = {
    "humano":  {"icon": "👤", "label": "Human",  "accent": "#3A7BD5"},
    "elfo":    {"icon": "🧝", "label": "Elf",    "accent": "#2ECC71"},
    "enano":   {"icon": "⚒",  "label": "Dwarf",  "accent": "#E67E22"},
    "orco":    {"icon": "💀", "label": "Orc",    "accent": "#C0392B"},
    "gnomo":   {"icon": "🔮", "label": "Gnome",  "accent": "#8E44AD"},
    "goblin":  {"icon": "🗡",  "label": "Goblin", "accent": "#27AE60"},
    "troll":   {"icon": "🪨", "label": "Troll",  "accent": "#626567"},
    "ogro":    {"icon": "👊", "label": "Ogre",   "accent": "#E74C3C"},
    "druida":  {"icon": "🌿", "label": "Druid",  "accent": "#1ABC9C"},
}

COLOR_THEMES  = ["blue", "dark-blue", "green"]
THEME_LABELS  = ["Blue", "Dark Blue", "Forest"]
APP_TITLE     = "RPG Name Generator"
APP_VERSION   = "2.0"

# ── Reusable widgets ──────────────────────────────────────────────────────────

class NumberSpinbox(ctk.CTkFrame):
    """Compact +/− spinbox."""

    def __init__(self, master, *, min_val=1, max_val=99, initial=5, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.min_val = min_val
        self.max_val = max_val
        self._var = ctk.StringVar(value=str(initial))

        self.grid_columnconfigure(1, weight=1)
        btn_kw = dict(width=28, height=28, font=ctk.CTkFont(size=15, weight="bold"))

        ctk.CTkButton(self, text="−", command=self._dec, **btn_kw).grid(row=0, column=0)
        ctk.CTkEntry(
            self, textvariable=self._var, width=46, height=28,
            justify="center", font=ctk.CTkFont(size=13),
        ).grid(row=0, column=1, padx=4)
        ctk.CTkButton(self, text="+", command=self._inc, **btn_kw).grid(row=0, column=2)

    def _safe(self):
        try:
            return int(self._var.get())
        except ValueError:
            return self.min_val

    def _clamp(self, v):
        return max(self.min_val, min(self.max_val, v))

    def _inc(self):
        self._var.set(str(self._clamp(self._safe() + 1)))

    def _dec(self):
        self._var.set(str(self._clamp(self._safe() - 1)))

    def get(self) -> int:
        return self._clamp(self._safe())

    def set(self, v: int):
        self._var.set(str(self._clamp(v)))


class RaceCard(ctk.CTkFrame):
    """Clickable race tile with icon, label and selection highlight."""

    def __init__(self, master, key: str, meta: dict, on_select, **kw):
        super().__init__(master, corner_radius=10, cursor="hand2", **kw)
        self.key = key
        self._on_select = on_select
        self._selected = False

        self.grid_columnconfigure(0, weight=1)

        self._icon_lbl = ctk.CTkLabel(self, text=meta["icon"], font=ctk.CTkFont(size=24))
        self._icon_lbl.grid(row=0, column=0, pady=(10, 0))

        self._name_lbl = ctk.CTkLabel(
            self, text=meta["label"], font=ctk.CTkFont(size=11, weight="bold")
        )
        self._name_lbl.grid(row=1, column=0, pady=(2, 10))

        for w in (self, self._icon_lbl, self._name_lbl):
            w.bind("<Button-1>", lambda _e, k=key: self._on_select(k))
            w.bind("<Enter>", self._hover_on)
            w.bind("<Leave>", self._hover_off)

    def _hover_on(self, _=None):
        if not self._selected:
            self.configure(fg_color=("gray75", "gray30"))

    def _hover_off(self, _=None):
        if not self._selected:
            self.configure(fg_color=("gray85", "gray20"))

    def select(self, accent: str):
        self._selected = True
        self.configure(fg_color=accent)

    def deselect(self):
        self._selected = False
        self.configure(fg_color=("gray85", "gray20"))


# ── Main application ──────────────────────────────────────────────────────────

class App(ctk.CTk):

    def __init__(self):
        cfg = _load_config()
        ctk.set_appearance_mode(cfg.get("appearance", "Dark"))
        ctk.set_default_color_theme(cfg.get("color_theme", "blue"))
        super().__init__()

        self._cfg = cfg
        self.title(f"  {APP_TITLE}")
        self.geometry("1150x700")
        self.minsize(900, 580)

        self._races_data: dict = cargar_razas()
        self._selected_race: str | None = None
        self._race_cards: dict[str, RaceCard] = {}
        self._names: list[str] = []

        self._build()

    # ── Layout ───────────────────────────────────────────────────────────────

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self._build_header()
        self._build_sidebar()
        self._build_content()
        self._build_statusbar()

    def _build_header(self):
        bar = ctk.CTkFrame(self, height=64, corner_radius=0)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            bar, text="⚔  RPG Name Generator",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=14, sticky="w")

        ctrl = ctk.CTkFrame(bar, fg_color="transparent")
        ctrl.grid(row=0, column=2, padx=20)

        ctk.CTkLabel(ctrl, text="Theme:", font=ctk.CTkFont(size=11)).grid(
            row=0, column=0, padx=(0, 6)
        )
        self._theme_seg = ctk.CTkSegmentedButton(
            ctrl, values=THEME_LABELS, width=200, command=self._change_color_theme
        )
        self._theme_seg.set(
            THEME_LABELS[COLOR_THEMES.index(self._cfg.get("color_theme", "blue"))]
        )
        self._theme_seg.grid(row=0, column=1, padx=6)

        ctk.CTkLabel(ctrl, text="Mode:", font=ctk.CTkFont(size=11)).grid(
            row=0, column=2, padx=(12, 6)
        )
        self._mode_seg = ctk.CTkSegmentedButton(
            ctrl, values=["Dark", "Light", "System"], width=190, command=self._change_mode
        )
        self._mode_seg.set(self._cfg.get("appearance", "Dark"))
        self._mode_seg.grid(row=0, column=3)

    def _build_sidebar(self):
        side = ctk.CTkScrollableFrame(
            self, width=215,
            label_text="RACES",
            label_font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=0,
        )
        side.grid(row=1, column=0, sticky="nsew")
        side.grid_columnconfigure((0, 1), weight=1)

        available = [k for k in RACES_META if k in self._races_data]
        for i, key in enumerate(available):
            card = RaceCard(side, key, RACES_META[key], self._select_race)
            card.grid(row=i // 2, column=i % 2, padx=5, pady=4, sticky="ew")
            self._race_cards[key] = card

    def _build_content(self):
        main = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        main.grid(row=1, column=1, sticky="nsew")
        main.grid_rowconfigure(2, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # ── Settings card ─────────────────────────────────────────────────────
        settings = ctk.CTkFrame(main, corner_radius=12)
        settings.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        settings.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Gender
        g_frame = ctk.CTkFrame(settings, fg_color="transparent")
        g_frame.grid(row=0, column=0, padx=24, pady=16, sticky="w")
        ctk.CTkLabel(g_frame, text="GENDER", font=ctk.CTkFont(size=11, weight="bold")).pack(
            anchor="w", pady=(0, 8)
        )
        self._gender = ctk.StringVar(value="masculino")
        for val, txt in [("masculino", "♂  Masculine"), ("femenino", "♀  Feminine")]:
            ctk.CTkRadioButton(
                g_frame, text=txt, variable=self._gender, value=val,
                font=ctk.CTkFont(size=13),
            ).pack(anchor="w", pady=3)

        # Divider
        ctk.CTkFrame(settings, width=1).grid(row=0, column=1, pady=12, sticky="ns")

        # Count
        c_frame = ctk.CTkFrame(settings, fg_color="transparent")
        c_frame.grid(row=0, column=2, padx=24, pady=16)
        ctk.CTkLabel(c_frame, text="NAMES TO GENERATE", font=ctk.CTkFont(size=11, weight="bold")).pack(
            pady=(0, 8)
        )
        self._count = NumberSpinbox(c_frame, min_val=1, max_val=50, initial=10)
        self._count.pack()

        # Syllables
        s_frame = ctk.CTkFrame(settings, fg_color="transparent")
        s_frame.grid(row=0, column=3, padx=24, pady=16)
        ctk.CTkLabel(s_frame, text="SYLLABLE RANGE", font=ctk.CTkFont(size=11, weight="bold")).pack(
            pady=(0, 8)
        )
        syl_row = ctk.CTkFrame(s_frame, fg_color="transparent")
        syl_row.pack()
        ctk.CTkLabel(syl_row, text="Min", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=(0, 4))
        self._min_s = NumberSpinbox(syl_row, min_val=2, max_val=8, initial=2)
        self._min_s.grid(row=0, column=1, padx=4)
        ctk.CTkLabel(syl_row, text="Max", font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=4)
        self._max_s = NumberSpinbox(syl_row, min_val=2, max_val=8, initial=4)
        self._max_s.grid(row=0, column=3, padx=(4, 0))

        # ── Generate button ───────────────────────────────────────────────────
        self._gen_btn = ctk.CTkButton(
            main, text="⚔  Generate Names",
            height=48, corner_radius=10,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._generate,
        )
        self._gen_btn.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="ew")

        # ── Results card ──────────────────────────────────────────────────────
        results = ctk.CTkFrame(main, corner_radius=12)
        results.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="nsew")
        results.grid_rowconfigure(1, weight=1)
        results.grid_columnconfigure(0, weight=1)

        rh = ctk.CTkFrame(results, fg_color="transparent")
        rh.grid(row=0, column=0, padx=12, pady=(12, 4), sticky="ew")
        rh.grid_columnconfigure(0, weight=1)

        self._res_title = ctk.CTkLabel(
            rh, text="Generated Names", font=ctk.CTkFont(size=14, weight="bold")
        )
        self._res_title.grid(row=0, column=0, sticky="w")

        btn_row = ctk.CTkFrame(rh, fg_color="transparent")
        btn_row.grid(row=0, column=1)
        for txt, cmd in [
            ("📋 Copy", self._copy),
            ("💾 Save", self._save),
            ("🗑 Clear", self._clear),
        ]:
            ctk.CTkButton(
                btn_row, text=txt, width=88, height=30,
                font=ctk.CTkFont(size=12), command=cmd,
            ).pack(side="left", padx=3)

        self._textbox = ctk.CTkTextbox(
            results,
            font=ctk.CTkFont(family="Consolas", size=13),
            state="disabled",
            wrap="word",
        )
        self._textbox.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")

    def _build_statusbar(self):
        bar = ctk.CTkFrame(self, height=26, corner_radius=0)
        bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        bar.grid_propagate(False)

        self._status_lbl = ctk.CTkLabel(
            bar, text="  Select a race to begin",
            font=ctk.CTkFont(size=11), anchor="w",
        )
        self._status_lbl.pack(side="left", fill="x", expand=True, padx=8)

        ctk.CTkLabel(
            bar, text=f"{APP_TITLE}  v{APP_VERSION}  •  {len(RACES_META)} races  ",
            font=ctk.CTkFont(size=11), anchor="e",
        ).pack(side="right")

    # ── Actions ───────────────────────────────────────────────────────────────

    def _select_race(self, key: str):
        for k, card in self._race_cards.items():
            if k == key:
                card.select(RACES_META[k]["accent"])
            else:
                card.deselect()
        self._selected_race = key
        meta = RACES_META[key]
        self._set_status(f"  {meta['icon']}  {meta['label']} selected")

    def _generate(self):
        if not self._selected_race:
            self._set_status("  ⚠  Please select a race first", error=True)
            return

        race = self._races_data.get(self._selected_race, {})
        gender = self._gender.get()
        gdata = race.get(gender)

        if not gdata:
            self._set_status(f"  ⚠  No {gender} data for {self._selected_race}", error=True)
            return

        count = self._count.get()
        min_s = self._min_s.get()
        max_s = max(min_s, self._max_s.get())
        self._max_s.set(max_s)

        names: set[str] = set()
        for _ in range(count * 30):
            if len(names) >= count:
                break
            names.add(generar_nombre(gdata, min_s, max_s).capitalize())

        self._names = sorted(names)
        self._render_names()

        meta = RACES_META[self._selected_race]
        glabel = "Masculine" if gender == "masculino" else "Feminine"
        self._set_status(
            f"  ✓  {len(self._names)} {meta['label']} ({glabel}) names generated"
        )

    def _render_names(self):
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        for i, name in enumerate(self._names, 1):
            self._textbox.insert("end", f"  {i:>2}.  {name}\n")
        self._textbox.configure(state="disabled")
        count_str = f"  ({len(self._names)})" if self._names else ""
        self._res_title.configure(text=f"Generated Names{count_str}")

    def _copy(self):
        if not self._names:
            self._set_status("  ⚠  No names to copy", error=True)
            return
        self.clipboard_clear()
        self.clipboard_append("\n".join(self._names))
        self._set_status(f"  ✓  {len(self._names)} names copied to clipboard")

    def _save(self):
        if not self._names:
            self._set_status("  ⚠  No names to save", error=True)
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")],
            title="Save Names",
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("\n".join(self._names))
                self._set_status(f"  ✓  Saved → {os.path.basename(path)}")
            except OSError as exc:
                self._set_status(f"  ✗  Save failed: {exc}", error=True)

    def _clear(self):
        self._names = []
        self._render_names()
        self._set_status("  Names cleared")

    def _change_mode(self, mode: str):
        ctk.set_appearance_mode(mode)
        self._cfg["appearance"] = mode
        _save_config(self._cfg)
        self._set_status(f"  Appearance: {mode}")

    def _change_color_theme(self, label: str):
        theme = COLOR_THEMES[THEME_LABELS.index(label)]
        if theme == self._cfg.get("color_theme", "blue"):
            return
        self._cfg["color_theme"] = theme
        _save_config(self._cfg)
        if messagebox.askyesno(
            "Restart Required",
            f"Color theme '{label}' will apply after a restart.\n\nRestart now?",
            parent=self,
        ):
            self.destroy()
            subprocess.Popen([sys.executable] + sys.argv)

    def _set_status(self, msg: str, *, error: bool = False):
        self._status_lbl.configure(
            text=msg, text_color="#FF6B6B" if error else None
        )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
