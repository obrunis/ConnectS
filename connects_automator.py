"""
ConnectS — Database Connection String Automator
================================================
Professional tool for Oracle TNS configuration automation.

Architecture:
  • domain   : pure business logic (no I/O)
  • services : file & process operations
  • ui       : custom tkinter components with glassmorphism design
  • app      : main application composition
"""

from __future__ import annotations

import os
import re
import subprocess
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog, scrolledtext
from typing import Callable, Optional


# =============================================================================
# DOMAIN LAYER  –  Pure business logic
# =============================================================================

@dataclass(frozen=True)
class TnsEntry:
    """Represents a valid tnsnames.ora entry."""
    alias: str
    raw_block: str


@dataclass(frozen=True)
class ConfigUpdate:
    """Parameters for MegaConfig.xml update."""
    oracle_alias: str
    logon_username: str


class TnsParseError(ValueError):
    """Raised when connect string format is invalid."""


def parse_tns_string(raw: str) -> TnsEntry:
    """Parse raw TNS connect string text."""
    raw = raw.strip()
    if not raw:
        raise TnsParseError("Paste the connect string provided by DBA.")

    match = re.match(r'^([A-Za-z0-9_\-\.]+)\s*=', raw)
    if not match:
        raise TnsParseError("Invalid format. String must start with ALIAS =")

    alias = match.group(1).strip()
    block = raw.rstrip("\n") + "\n\n"
    return TnsEntry(alias=alias, raw_block=block)


def build_xml_update(oracle_alias: str, logon_username: str) -> ConfigUpdate:
    """Validate and package values for XML update."""
    if not oracle_alias.strip():
        raise ValueError("<ORACLE> field cannot be empty.")
    if not logon_username.strip():
        raise ValueError("<LOGONUSERNAME> field cannot be empty.")
    return ConfigUpdate(oracle_alias.strip(), logon_username.strip())


# =============================================================================
# SERVICE LAYER  –  File & process I/O
# =============================================================================

_ENCODING = "latin-1"


def _read_file(path: str) -> str:
    with open(path, "r", encoding=_ENCODING) as fh:
        return fh.read()


def _write_file(path: str, content: str) -> None:
    with open(path, "w", encoding=_ENCODING) as fh:
        fh.write(content)


def _alias_exists_in(content: str, alias: str) -> bool:
    pattern = rf'^\s*{re.escape(alias)}\s*='
    return bool(re.search(pattern, content, re.MULTILINE | re.IGNORECASE))


def save_tns_entry(tns_path: str, entry: TnsEntry) -> str:
    """Insert or replace entry in tnsnames.ora."""
    if not os.path.exists(tns_path):
        _write_file(tns_path, entry.raw_block)
        return f"File created and entry '{entry.alias}' inserted."

    content = _read_file(tns_path)

    if _alias_exists_in(content, entry.alias):
        pattern = rf'(^|\n){re.escape(entry.alias)}\s*=.*?(?=\n[A-Za-z0-9_\-\.]|\Z)'
        updated = re.sub(
            pattern,
            "\n" + entry.raw_block.rstrip("\n"),
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )
        _write_file(tns_path, updated)
        return f"Alias '{entry.alias}' already existed — entry updated."

    if not content.endswith("\n"):
        content += "\n"
    _write_file(tns_path, content + entry.raw_block)
    return f"Entry '{entry.alias}' inserted in tnsnames.ora."


def apply_config_update(config_path: str, update: ConfigUpdate) -> str:
    """Update <ORACLE> and <LOGONUSERNAME> tags in MegaConfig.xml."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"File not found: {config_path}")

    content = original = _read_file(config_path)

    content = re.sub(
        r'(<ORACLE>)(.*?)(</ORACLE>)',
        rf'\g<1>{update.oracle_alias}\g<3>',
        content,
        flags=re.IGNORECASE,
    )
    content = re.sub(
        r'(<LOGONUSERNAME>)(.*?)(</LOGONUSERNAME>)',
        rf'\g<1>{update.logon_username}\g<3>',
        content,
        flags=re.IGNORECASE,
    )

    if content == original:
        raise ValueError("<ORACLE> or <LOGONUSERNAME> tags not found in XML.")

    _write_file(config_path, content)
    return (
        f"MegaConfig.xml updated:\n"
        f"  <ORACLE>        → {update.oracle_alias}\n"
        f"  <LOGONUSERNAME> → {update.logon_username}"
    )


def launch_executable(exe_path: str) -> None:
    """Launch Windows executable independently."""
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"Executable not found: {exe_path}")

    flags = 0
    if os.name == "nt":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

    subprocess.Popen(
        [exe_path],
        cwd=os.path.dirname(exe_path) or ".",
        creationflags=flags,
        close_fds=True,
    )


# =============================================================================
# DESIGN SYSTEM  –  Cyber/Glassmorphism Theme
# =============================================================================

class DS:
    """
    ConnectS Design System — Cyber aesthetic with glassmorphism.
    Blue + Black palette with transparency and neon accents.
    """

    # Color palette - Cyber Blue + Deep Black
    BG           = "#0A0E14"   # Deep black with blue undertone
    SURFACE      = "#141922"   # Dark surface for cards
    SURFACE_GLASS= "#1A2332"   # Glassmorphism layer
    BORDER       = "#1E3A5F"   # Deep blue border
    BORDER_GLOW  = "#0066FF"   # Neon blue glow
    
    PRIMARY      = "#0066FF"   # Electric blue
    PRIMARY_HOVER= "#0052CC"   # Darker blue on hover
    ACCENT       = "#00D9FF"   # Cyan neon
    
    SUCCESS      = "#00E5A0"   # Bright cyan-green
    WARNING      = "#FFB800"   # Amber
    ERROR        = "#FF3366"   # Hot pink-red
    
    TEXT         = "#E8EDF5"   # Blue-tinted white
    TEXT_DIM     = "#7A8BA0"   # Muted blue-gray
    TEXT_MONO    = "#A0B5D0"   # Code text color

    # Typography - Technical aesthetic
    FONT_DISPLAY = ("Bahnschrift SemiBold", 16)  # Modern geometric
    FONT_TITLE   = ("Segoe UI Semibold", 11)
    FONT_BODY    = ("Segoe UI", 9)
    FONT_LABEL   = ("Segoe UI", 9)
    FONT_MONO    = ("Consolas", 9)
    FONT_SMALL   = ("Segoe UI", 8)

    # Spacing & sizing
    PAD_XS  = 4
    PAD_SM  = 8
    PAD_MD  = 14
    PAD_LG  = 22
    PAD_XL  = 32

    # Effects
    SHADOW_COLOR = "#000000"
    GLOW_INTENSITY = 2  # px


# =============================================================================
# GLASSMORPHISM COMPONENTS
# =============================================================================

class GlassCard(tk.Frame):
    """Card with glassmorphism effect - layered semi-transparent frames."""

    def __init__(self, master, **kw):
        kw["bg"] = DS.SURFACE
        kw["relief"] = "flat"
        kw["bd"] = 0
        super().__init__(master, **kw)

        # Glow border effect (simulated with colored frame)
        glow = tk.Frame(self, bg=DS.BORDER_GLOW, height=1)
        glow.pack(fill="x", side="top")

        # Inner glass layer
        self.glass = tk.Frame(self, bg=DS.SURFACE_GLASS)
        self.glass.pack(fill="both", expand=True, padx=1, pady=1)

        # Content area
        self.body = tk.Frame(self.glass, bg=DS.SURFACE_GLASS)
        self.body.pack(fill="both", expand=True, padx=DS.PAD_MD, pady=DS.PAD_MD)
        self.body.columnconfigure(1, weight=1)


class StepCard(tk.Frame):
    """Pipeline step card with numbered badge."""

    def __init__(self, master, step: int, title: str, **kw):
        kw["bg"] = DS.SURFACE
        super().__init__(master, **kw)

        # Top accent line
        tk.Frame(self, bg=DS.ACCENT, height=2).pack(fill="x")

        # Header with step badge
        header = tk.Frame(self, bg=DS.SURFACE)
        header.pack(fill="x", padx=DS.PAD_MD, pady=(DS.PAD_SM, DS.PAD_XS))

        # Step badge with glow effect
        badge_frame = tk.Frame(header, bg=DS.PRIMARY, bd=0)
        badge_frame.pack(side="left")
        
        tk.Label(
            badge_frame,
            text=f" {step} ",
            bg=DS.PRIMARY,
            fg="#FFFFFF",
            font=("Bahnschrift", 9, "bold"),
            padx=6, pady=2,
        ).pack()

        tk.Label(
            header,
            text=f"   {title}",
            bg=DS.SURFACE,
            fg=DS.TEXT,
            font=DS.FONT_TITLE,
        ).pack(side="left")

        # Body
        self.body = tk.Frame(self, bg=DS.SURFACE)
        self.body.pack(fill="both", expand=True, padx=DS.PAD_MD, pady=DS.PAD_MD)
        self.body.columnconfigure(1, weight=1)


class CyberEntry(tk.Entry):
    """Entry with cyber aesthetic - glowing border on focus."""

    def __init__(self, master, **kw):
        kw.setdefault("bg", DS.SURFACE_GLASS)
        kw.setdefault("fg", DS.TEXT)
        kw.setdefault("insertbackground", DS.ACCENT)
        kw.setdefault("relief", "flat")
        kw.setdefault("font", DS.FONT_BODY)
        kw.setdefault("highlightthickness", 2)
        kw.setdefault("highlightbackground", DS.BORDER)
        kw.setdefault("highlightcolor", DS.BORDER_GLOW)
        kw.setdefault("bd", 6)
        super().__init__(master, **kw)


class CyberText(scrolledtext.ScrolledText):
    """Multi-line text with monospace font and cyber styling."""

    def __init__(self, master, **kw):
        kw.setdefault("bg", DS.SURFACE_GLASS)
        kw.setdefault("fg", DS.TEXT_MONO)
        kw.setdefault("insertbackground", DS.ACCENT)
        kw.setdefault("relief", "flat")
        kw.setdefault("font", DS.FONT_MONO)
        kw.setdefault("highlightthickness", 2)
        kw.setdefault("highlightbackground", DS.BORDER)
        kw.setdefault("highlightcolor", DS.BORDER_GLOW)
        kw.setdefault("bd", 8)
        kw.setdefault("wrap", "none")
        super().__init__(master, **kw)


class CyberSpinbox(tk.Spinbox):
    """Spinbox with cyber theme."""

    def __init__(self, master, **kw):
        kw.setdefault("bg", DS.SURFACE_GLASS)
        kw.setdefault("fg", DS.TEXT)
        kw.setdefault("insertbackground", DS.ACCENT)
        kw.setdefault("relief", "flat")
        kw.setdefault("font", DS.FONT_BODY)
        kw.setdefault("highlightthickness", 2)
        kw.setdefault("highlightbackground", DS.BORDER)
        kw.setdefault("highlightcolor", DS.BORDER_GLOW)
        kw.setdefault("bd", 4)
        kw.setdefault("buttonbackground", DS.PRIMARY)
        super().__init__(master, **kw)


class NeonButton(tk.Button):
    """Primary action button with neon glow effect."""

    def __init__(self, master, **kw):
        kw.setdefault("bg", DS.PRIMARY)
        kw.setdefault("fg", "#FFFFFF")
        kw.setdefault("activebackground", DS.PRIMARY_HOVER)
        kw.setdefault("activeforeground", "#FFFFFF")
        kw.setdefault("relief", "flat")
        kw.setdefault("font", ("Bahnschrift SemiBold", 10))
        kw.setdefault("cursor", "hand2")
        kw.setdefault("bd", 0)
        kw.setdefault("padx", 22)
        kw.setdefault("pady", 10)
        super().__init__(master, **kw)
        
        self._default_bg = kw.get("bg", DS.PRIMARY)
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)

    def _on_hover(self, _):
        self.config(bg=DS.PRIMARY_HOVER)

    def _on_leave(self, _):
        self.config(bg=self._default_bg)


class GhostButton(tk.Button):
    """Secondary button with outline style."""

    def __init__(self, master, **kw):
        kw.setdefault("bg", DS.SURFACE)
        kw.setdefault("fg", DS.TEXT_DIM)
        kw.setdefault("activebackground", DS.SURFACE_GLASS)
        kw.setdefault("activeforeground", DS.TEXT)
        kw.setdefault("relief", "flat")
        kw.setdefault("font", DS.FONT_BODY)
        kw.setdefault("cursor", "hand2")
        kw.setdefault("bd", 0)
        kw.setdefault("padx", 14)
        kw.setdefault("pady", 7)
        super().__init__(master, **kw)
        self.bind("<Enter>", lambda _: self.config(fg=DS.TEXT))
        self.bind("<Leave>", lambda _: self.config(fg=DS.TEXT_DIM))


class IconButton(tk.Button):
    """Compact icon button (for browse dialogs)."""

    def __init__(self, master, **kw):
        kw.setdefault("bg", DS.SURFACE_GLASS)
        kw.setdefault("fg", DS.TEXT_DIM)
        kw.setdefault("activebackground", DS.PRIMARY)
        kw.setdefault("activeforeground", "#FFFFFF")
        kw.setdefault("relief", "flat")
        kw.setdefault("font", DS.FONT_BODY)
        kw.setdefault("cursor", "hand2")
        kw.setdefault("bd", 0)
        kw.setdefault("padx", 10)
        kw.setdefault("pady", 6)
        super().__init__(master, **kw)
        self.bind("<Enter>", lambda _: self.config(bg=DS.PRIMARY, fg="#FFFFFF"))
        self.bind("<Leave>", lambda _: self.config(bg=DS.SURFACE_GLASS, fg=DS.TEXT_DIM))


def labeled_row(
    parent: tk.Frame,
    row: int,
    label: str,
    widget: tk.Widget,
    browse_cmd: Optional[Callable] = None,
    pady: tuple = (0, 8),
) -> None:
    """Create label + widget [+ browse button] grid row."""
    tk.Label(
        parent,
        text=label,
        bg=DS.SURFACE,
        fg=DS.TEXT_DIM,
        font=DS.FONT_LABEL,
        anchor="w",
    ).grid(row=row, column=0, sticky="w", padx=(0, DS.PAD_SM), pady=pady)

    col_span = 1 if browse_cmd else 2
    widget.grid(row=row, column=1, columnspan=col_span, sticky="ew", pady=pady)

    if browse_cmd:
        IconButton(parent, text="···", command=browse_cmd).grid(
            row=row, column=2, padx=(6, 0), pady=pady
        )


# =============================================================================
# CYBER LOG PANEL
# =============================================================================

class CyberLogPanel(tk.Frame):
    """Log panel with syntax highlighting."""

    def __init__(self, master, **kw):
        kw["bg"] = DS.BG
        super().__init__(master, **kw)
        self._build()

    def _build(self) -> None:
        # Header
        header = tk.Frame(self, bg=DS.SURFACE)
        header.pack(fill="x")

        tk.Frame(header, bg=DS.ACCENT, height=2).pack(fill="x", side="bottom")

        inner = tk.Frame(header, bg=DS.SURFACE, pady=DS.PAD_SM)
        inner.pack(fill="x", padx=DS.PAD_MD)

        tk.Label(
            inner,
            text="EXECUTION LOG",
            bg=DS.SURFACE,
            fg=DS.TEXT_DIM,
            font=("Bahnschrift", 8, "bold"),
        ).pack(side="left")

        GhostButton(inner, text="Clear", command=self.clear).pack(side="right")

        # Log text
        self._text = tk.Text(
            self,
            bg="#0D1117",
            fg=DS.TEXT_MONO,
            insertbackground=DS.ACCENT,
            relief="flat",
            font=DS.FONT_MONO,
            highlightthickness=0,
            bd=DS.PAD_SM,
            state="disabled",
            wrap="none",
        )
        self._text.pack(fill="both", expand=True)

        # Scrollbar
        vsb = tk.Scrollbar(
            self._text,
            orient="vertical",
            command=self._text.yview,
            bg=DS.SURFACE,
            troughcolor=DS.BG,
            relief="flat",
            bd=0,
        )
        self._text.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

        # Color tags
        self._text.tag_configure("success", foreground=DS.SUCCESS)
        self._text.tag_configure("warning", foreground=DS.WARNING)
        self._text.tag_configure("error", foreground=DS.ERROR)
        self._text.tag_configure("info", foreground=DS.ACCENT)
        self._text.tag_configure("divider", foreground=DS.BORDER)
        self._text.tag_configure("default", foreground=DS.TEXT_MONO)

    def _resolve_tag(self, line: str) -> str:
        stripped = line.lstrip()
        for prefix, tag in [
            ("✅", "success"), ("⚠", "warning"), ("❌", "error"),
            ("▶", "info"), ("⏳", "warning"), ("🔍", "info"),
            ("═", "divider"),
        ]:
            if stripped.startswith(prefix):
                return tag
        return "default"

    def append(self, message: str) -> None:
        """Append message to log (thread-safe)."""
        def _insert():
            self._text.config(state="normal")
            self._text.insert("end", message + "\n", self._resolve_tag(message))
            self._text.see("end")
            self._text.config(state="disabled")
        self._text.after(0, _insert)

    def clear(self) -> None:
        self._text.config(state="normal")
        self._text.delete("1.0", "end")
        self._text.config(state="disabled")


# =============================================================================
# MAIN APPLICATION
# =============================================================================

_DEFAULT_BASE = r"C:\Mega"

_DEFAULT_PATHS = {
    "tns":      os.path.join(_DEFAULT_BASE, "tnsnames.ora"),
    "config":   os.path.join(_DEFAULT_BASE, "MegaConfig.xml"),
    "mcm":      os.path.join(_DEFAULT_BASE, "MegaConnectionManager.exe"),
    "registro": os.path.join(_DEFAULT_BASE, "Mega_Registro_App.exe"),
}


class ConnectSApp(tk.Tk):
    """
    ConnectS - Database Connection String Automator
    
    Cyber-themed UI with glassmorphism design.
    Handles Oracle TNS configuration automation.
    """

    def __init__(self):
        super().__init__()
        self.title("ConnectS — Database Connection Automator")
        self.configure(bg=DS.BG)
        self.minsize(820, 800)
        self.resizable(True, True)
        
        # Enable window transparency (85% opacity)
        self.attributes("-alpha", 0.96)
        
        self._build_ui()
        self._populate_defaults()

    def _build_ui(self) -> None:
        self._build_header()
        
        # Main content with padding
        content = tk.Frame(self, bg=DS.BG)
        content.pack(fill="both", expand=True, padx=DS.PAD_XL, pady=(0, DS.PAD_MD))
        content.columnconfigure(0, weight=1)
        content.rowconfigure(4, weight=1)

        self._build_step1(content, row=0)
        self._build_step2(content, row=1)
        self._build_step3(content, row=2)
        self._build_actions(content, row=3)
        self._build_log(content, row=4)

    def _build_header(self) -> None:
        # Header bar with gradient effect (simulated)
        bar = tk.Frame(self, bg=DS.SURFACE)
        bar.pack(fill="x")

        # Neon accent line at bottom
        tk.Frame(bar, bg=DS.ACCENT, height=3).pack(fill="x", side="bottom")

        inner = tk.Frame(bar, bg=DS.SURFACE)
        inner.pack(fill="x", padx=DS.PAD_XL, pady=DS.PAD_LG)

        # Logo/title
        title_frame = tk.Frame(inner, bg=DS.SURFACE)
        title_frame.pack(side="left")

        tk.Label(
            title_frame,
            text="Connect",
            bg=DS.SURFACE,
            fg=DS.PRIMARY,
            font=("Bahnschrift SemiBold", 18),
        ).pack(side="left")

        tk.Label(
            title_frame,
            text="S",
            bg=DS.SURFACE,
            fg=DS.ACCENT,
            font=("Bahnschrift SemiBold", 18),
        ).pack(side="left")

        tk.Label(
            inner,
            text="  │  Database Connection String Automator",
            bg=DS.SURFACE,
            fg=DS.TEXT_DIM,
            font=("Segoe UI", 10),
        ).pack(side="left", padx=(DS.PAD_SM, 0))

        # Version badge
        version = tk.Frame(inner, bg=DS.PRIMARY, bd=0)
        version.pack(side="right")
        tk.Label(
            version,
            text=" v2.1 ",
            bg=DS.PRIMARY,
            fg="#FFFFFF",
            font=("Bahnschrift", 8, "bold"),
            padx=4, pady=2,
        ).pack()

    def _build_step1(self, parent: tk.Frame, row: int) -> None:
        card = StepCard(parent, step=1, title="TNS Connect String")
        card.grid(row=row, column=0, sticky="ew", pady=(0, DS.PAD_SM))

        body = card.body
        self._tns_path = CyberEntry(body)
        labeled_row(
            body, 0, "tnsnames.ora path:",
            self._tns_path,
            browse_cmd=lambda: self._browse(
                self._tns_path, [("ORA", "*.ora"), ("All", "*.*")]
            )
        )

        tk.Label(
            body,
            text="Connect String (paste here):",
            bg=DS.SURFACE,
            fg=DS.TEXT_DIM,
            font=DS.FONT_LABEL,
            anchor="w",
        ).grid(row=1, column=0, sticky="nw", padx=(0, DS.PAD_SM), pady=(0, 4))

        self._tns_input = CyberText(body, height=7)
        self._tns_input.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(0, 4))

    def _build_step2(self, parent: tk.Frame, row: int) -> None:
        card = StepCard(parent, step=2, title="Update MegaConfig.xml")
        card.grid(row=row, column=0, sticky="ew", pady=(0, DS.PAD_SM))

        body = card.body
        self._cfg_path = CyberEntry(body)
        labeled_row(
            body, 0, "MegaConfig.xml path:",
            self._cfg_path,
            browse_cmd=lambda: self._browse(
                self._cfg_path, [("XML", "*.xml"), ("All", "*.*")]
            )
        )

        self._oracle_tag = CyberEntry(body)
        labeled_row(body, 1, "<ORACLE> (TNS alias):", self._oracle_tag)

        self._logon_tag = CyberEntry(body)
        labeled_row(body, 2, "<LOGONUSERNAME> (owner):", self._logon_tag)

        GhostButton(
            body,
            text="⚡ Auto-detect alias from string above",
            command=self._auto_detect_alias,
        ).grid(row=3, column=1, sticky="w", pady=(4, 0))

    def _build_step3(self, parent: tk.Frame, row: int) -> None:
        card = StepCard(parent, step=3, title="Execute MCM → Registration")
        card.grid(row=row, column=0, sticky="ew", pady=(0, DS.PAD_SM))

        body = card.body
        self._mcm_path = CyberEntry(body)
        labeled_row(
            body, 0, "MegaConnectionManager.exe:",
            self._mcm_path,
            browse_cmd=lambda: self._browse(self._mcm_path, [("EXE", "*.exe")])
        )

        self._reg_path = CyberEntry(body)
        labeled_row(
            body, 1, "Mega_Registro_App.exe:",
            self._reg_path,
            browse_cmd=lambda: self._browse(self._reg_path, [("EXE", "*.exe")])
        )

        # Wait time row
        wait_row = tk.Frame(body, bg=DS.SURFACE)
        wait_row.grid(row=2, column=0, columnspan=3, sticky="w", pady=(DS.PAD_SM, 0))

        tk.Label(
            wait_row,
            text="⏱  Wait",
            bg=DS.SURFACE,
            fg=DS.TEXT_DIM,
            font=DS.FONT_LABEL,
        ).pack(side="left")

        self._wait_var = tk.IntVar(value=15)
        CyberSpinbox(
            wait_row,
            from_=5, to=120,
            width=5,
            textvariable=self._wait_var,
        ).pack(side="left", padx=8)

        tk.Label(
            wait_row,
            text="seconds between MCM and Registration app",
            bg=DS.SURFACE,
            fg=DS.TEXT_DIM,
            font=DS.FONT_SMALL,
        ).pack(side="left")

    def _build_actions(self, parent: tk.Frame, row: int) -> None:
        bar = tk.Frame(parent, bg=DS.BG)
        bar.grid(row=row, column=0, sticky="ew", pady=DS.PAD_MD)

        self._run_btn = NeonButton(
            bar,
            text="▶  EXECUTE FULL PROCESS",
            command=self._start_pipeline,
        )
        self._run_btn.pack(side="left")

        self._status_lbl = tk.Label(
            bar,
            text="",
            bg=DS.BG,
            fg=DS.TEXT_DIM,
            font=DS.FONT_BODY,
        )
        self._status_lbl.pack(side="left", padx=DS.PAD_MD)

    def _build_log(self, parent: tk.Frame, row: int) -> None:
        self._log_panel = CyberLogPanel(parent)
        self._log_panel.grid(row=row, column=0, sticky="nsew", pady=(0, 0))

    def _populate_defaults(self) -> None:
        for entry, key in [
            (self._tns_path, "tns"),
            (self._cfg_path, "config"),
            (self._mcm_path, "mcm"),
            (self._reg_path, "registro"),
        ]:
            entry.insert(0, _DEFAULT_PATHS[key])

    def _browse(self, entry: CyberEntry, filetypes: list) -> None:
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)

    def _log(self, message: str) -> None:
        self._log_panel.append(message)

    def _set_running(self, running: bool) -> None:
        if running:
            self._run_btn.config(state="disabled", text="⏳  PROCESSING...")
            self._status_lbl.config(text="Running...", fg=DS.WARNING)
        else:
            self._run_btn.config(state="normal", text="▶  EXECUTE FULL PROCESS")
            self._status_lbl.config(text="")

    def _auto_detect_alias(self) -> None:
        raw = self._tns_input.get("1.0", "end")
        try:
            entry = parse_tns_string(raw)
            self._oracle_tag.delete(0, "end")
            self._oracle_tag.insert(0, entry.alias)
            self._log(f"🔍 Alias auto-detected: {entry.alias}")
        except TnsParseError as exc:
            self._log(f"⚠ {exc}")

    def _start_pipeline(self) -> None:
        """Launch pipeline in daemon thread."""
        self._set_running(True)
        threading.Thread(target=self._run_pipeline, daemon=True).start()

    def _run_pipeline(self) -> None:
        try:
            self._step1_tns()
            self._step2_config()
            self._step3_mcm()
            self._step4_registro()
            self._log_success()
        except Exception as exc:
            self._log(f"❌ {exc}")
        finally:
            self.after(0, lambda: self._set_running(False))

    def _step1_tns(self) -> None:
        self._log("\n═══════════════════════════════════════════")
        self._log("  STARTING CONNECTS AUTOMATION")
        self._log("═══════════════════════════════════════════")
        self._log("\n[1/4] Updating tnsnames.ora...")

        raw = self._tns_input.get("1.0", "end")
        entry = parse_tns_string(raw)

        if not self._oracle_tag.get().strip():
            alias = entry.alias
            self.after(0, lambda: (
                self._oracle_tag.delete(0, "end"),
                self._oracle_tag.insert(0, alias),
            ))

        result = save_tns_entry(self._tns_path.get().strip(), entry)
        self._log(f"✅ {result}")

    def _step2_config(self) -> None:
        self._log("\n[2/4] Updating MegaConfig.xml...")
        update = build_xml_update(self._oracle_tag.get(), self._logon_tag.get())
        result = apply_config_update(self._cfg_path.get().strip(), update)
        self._log(f"✅ {result}")

    def _step3_mcm(self) -> None:
        self._log("\n[3/4] Executing MegaConnectionManager.exe...")
        launch_executable(self._mcm_path.get().strip())
        self._log("✅ MegaConnectionManager.exe launched.")

        wait = max(5, self._wait_var.get())
        self._log(f"\n⏳ Waiting {wait}s for MCM to stabilize...")
        for remaining in range(wait, 0, -1):
            self._log(f"   ...{remaining}s")
            time.sleep(1)

    def _step4_registro(self) -> None:
        self._log("\n[4/4] Executing Mega_Registro_App.exe...")
        launch_executable(self._reg_path.get().strip())
        self._log("✅ Mega_Registro_App.exe launched.")

    def _log_success(self) -> None:
        self._log("\n═══════════════════════════════════════════")
        self._log("  ✅  PROCESS COMPLETED SUCCESSFULLY!")
        self._log("═══════════════════════════════════════════\n")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app = ConnectSApp()
    app.mainloop()
