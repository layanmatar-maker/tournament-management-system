# pages_admin_chat.py
import tkinter as tk
from tkinter import ttk, messagebox
import data_store as ds


class AdminChatPage(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style="Content.TFrame")
        self.app = app
        self._auto_job = None

        header = ttk.Frame(self, style="Content.TFrame")
        header.pack(fill="x", padx=30, pady=(26, 10))

        ttk.Label(header, text="Admins Chat", style="Title.TLabel").pack(side="left")

        ttk.Button(header, text="Refresh", style="Primary.TButton", command=self.refresh).pack(side="right")
        ttk.Button(header, text="Clear", style="Primary.TButton", command=self.clear_chat).pack(side="right", padx=(0, 10))
        ttk.Button(header, text="Copy", style="Primary.TButton", command=self.copy_chat).pack(side="right", padx=(0, 10))

        who = self._who_am_i()
        self.status = ttk.Label(self, text=f"Logged in as: {who}", style="Sub.TLabel")
        self.status.pack(anchor="w", padx=30, pady=(0, 10))

        wrap = ttk.Frame(self, style="Content.TFrame")
        wrap.pack(fill="both", expand=True, padx=30, pady=(0, 26))

        # ===== Chat area card =====
        box = ttk.Frame(wrap, style="Card.TFrame")
        box.pack(fill="both", expand=True)

        # Text widget styled for "chat bubbles"
        self.txt = tk.Text(
            box,
            wrap="word",
            bg=self.app.COL_CARD,
            fg=self.app.COL_TEXT,
            insertbackground=self.app.COL_TEXT,
            relief="flat",
            bd=0,
            padx=14,
            pady=12,
        )
        self.txt.pack(side="left", fill="both", expand=True)
        self.txt.configure(state="disabled")

        sb = ttk.Scrollbar(box, orient="vertical", command=self.txt.yview)
        sb.pack(side="left", fill="y")
        self.txt.configure(yscrollcommand=sb.set)

        # Tags (bubble styles)
        self._setup_tags()

        # ===== Input row =====
        row = ttk.Frame(wrap, style="Content.TFrame")
        row.pack(fill="x", pady=(12, 0))

        self.msg_var = tk.StringVar()
        self.entry = tk.Text(
            row,
            height=2,
            wrap="word",
            bg=self.app.COL_PANEL,
            fg=self.app.COL_TEXT,
            insertbackground=self.app.COL_TEXT,
            relief="flat",
            bd=0,
            padx=10,
            pady=8,
        )
        self.entry.pack(side="left", fill="x", expand=True)

        btns = ttk.Frame(row, style="Content.TFrame")
        btns.pack(side="left", padx=(10, 0))

        ttk.Button(btns, text="Send", style="Primary.TButton", command=self.send).pack(fill="x")
        ttk.Button(btns, text="Auto: ON", style="Primary.TButton", command=self.toggle_auto).pack(fill="x", pady=(8, 0))

        self.auto_btn = btns.winfo_children()[-1]
        self._auto_on = True

        # Enter sends, Shift+Enter new line
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Shift-Return>", self._on_shift_enter)

        # Load initial
        self.refresh()
        self._schedule_auto_refresh()

    # -----------------------------
    # UI polish
    # -----------------------------
    def _setup_tags(self):
        # Safer fonts
        base_font = ("Segoe UI", 10)
        bold_font = ("Segoe UI", 10, "bold")

        # Timestamp + sender
        self.txt.tag_configure("meta", font=bold_font, foreground=self.app.COL_MUTED)
        self.txt.tag_configure("spacer", font=base_font)

        # Bubble-like blocks
        # Note: Text widget doesn't support rounded corners, but we fake it with padding + background
        self.txt.tag_configure("me", font=base_font, foreground="#001018", background=self.app.COL_ACCENT, lmargin1=140, lmargin2=140, rmargin=12, spacing1=6, spacing3=8)
        self.txt.tag_configure("other", font=base_font, foreground=self.app.COL_TEXT, background=self.app.COL_PANEL, lmargin1=12, lmargin2=12, rmargin=140, spacing1=6, spacing3=8)

    def _who_am_i(self) -> str:
        # supports both app.admin_role (new) and app.admin_name (old)
        who = getattr(self.app, "admin_role", None) or getattr(self.app, "admin_name", None) or "Admin"
        return str(who)

    # -----------------------------
    # Auto refresh
    # -----------------------------
    def _schedule_auto_refresh(self):
        # refresh every 2.5 seconds
        if self._auto_on:
            self._auto_job = self.after(2500, self._auto_tick)

    def _auto_tick(self):
        self.refresh(silent=True)
        self._schedule_auto_refresh()

    def toggle_auto(self):
        self._auto_on = not self._auto_on
        self.auto_btn.config(text=("Auto: ON" if self._auto_on else "Auto: OFF"))

        if not self._auto_on and self._auto_job is not None:
            try:
                self.after_cancel(self._auto_job)
            except Exception:
                pass
            self._auto_job = None
        else:
            self._schedule_auto_refresh()

    # -----------------------------
    # Refresh & render
    # -----------------------------
    def refresh(self, silent: bool = False):
        try:
            ds.load_state()
        except Exception:
            pass

        # expects ds.get_admin_chat() -> list of {"from","ts","text"}
        try:
            msgs = ds.get_admin_chat()
        except Exception:
            msgs = []

        me = self._who_am_i()

        self.txt.configure(state="normal")
        self.txt.delete("1.0", "end")

        if not msgs:
            self.txt.insert("end", "No messages yet. Type something 🔥\n", "meta")
        else:
            for m in msgs:
                sender = str(m.get("from", "Admin"))
                ts = str(m.get("ts", ""))
                text = str(m.get("text", "")).strip()

                # meta line
                meta_line = f"{sender}  •  {ts}\n" if ts else f"{sender}\n"
                self.txt.insert("end", meta_line, "meta")

                # bubble
                tag = "me" if sender == me else "other"
                self.txt.insert("end", f" {text} \n", tag)

                # spacing between messages
                self.txt.insert("end", "\n", "spacer")

        self.txt.configure(state="disabled")
        self.txt.see("end")

        if not silent:
            self.status.config(text=f"Logged in as: {me}   |   Messages: {len(msgs)}")

    # -----------------------------
    # Send
    # -----------------------------
    def _on_enter(self, e):
        # prevent newline
        self.send()
        return "break"

    def _on_shift_enter(self, e):
        # allow newline
        self.entry.insert("insert", "\n")
        return "break"

    def send(self):
        text = self.entry.get("1.0", "end").strip()
        if not text:
            return

        sender = self._who_am_i()

        try:
            ds.add_admin_message(sender, text)
        except Exception as ex:
            messagebox.showerror("Error", f"Couldn't send message:\n{ex}")
            return

        self.entry.delete("1.0", "end")
        self.refresh()

    # -----------------------------
    # Utils
    # -----------------------------
    def copy_chat(self):
        try:
            ds.load_state()
        except Exception:
            pass

        try:
            msgs = ds.get_admin_chat()
        except Exception:
            msgs = []

        out = []
        for m in msgs:
            sender = str(m.get("from", "Admin"))
            ts = str(m.get("ts", ""))
            text = str(m.get("text", "")).strip()
            if ts:
                out.append(f"[{ts}] {sender}: {text}")
            else:
                out.append(f"{sender}: {text}")

        joined = "\n".join(out).strip()
        if not joined:
            joined = "No messages."

        self.clipboard_clear()
        self.clipboard_append(joined)
        messagebox.showinfo("Copied", "Chat copied to clipboard ✅")

    def clear_chat(self):
        ok = messagebox.askyesno("Confirm", "Are you sure you want to clear all chat messages?")
        if not ok:
            return
        try:
            ds.clear_admin_chat()
        except Exception as ex:
            messagebox.showerror("Error", f"Couldn't clear chat:\n{ex}")
            return
        self.refresh()
        messagebox.showinfo("Done", "Chat cleared ✅")