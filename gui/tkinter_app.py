"""
VERIRESUME - Tkinter Desktop Admin GUI Application
===================================================
This module implements the standalone Desktop Administration Panel using Python's
built-in Tkinter and ttk GUI libraries.

Key GUI Features Demonstrated:
1. Modern styled Tkinter window with ttk widgets and tabbed panels
2. Direct integration with low-level TCP Socket Client for network verification
3. Interactive verification form with Candidate, ID, Course, Org, and Date fields
4. File selector (filedialog) to import sample resumes or certificates
5. Live score gauge with SymPy mathematical breakdown visualization
6. Interactive Certificate History Treeview table
7. Server connectivity status monitor with health probe
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
from networking.socket_client import SocketVerificationClient
from backend.resume_parser import resume_parser
from mathematics.authenticity_model import get_symbolic_formula, get_latex_formula


class TkinterAdminApp(tk.Tk):
    """
    VERIRESUME Desktop Administration Application.
    """

    def __init__(self):
        super().__init__()

        self.title("VERIRESUME – Certificate Verification Admin Panel")
        self.geometry("960x780")
        self.minsize(880, 700)
        self.configure(bg="#0B132B")

        # Socket Client Instance
        self.client = SocketVerificationClient(
            host=config.SOCKET_HOST,
            port=config.SOCKET_PORT,
            timeout=config.SOCKET_TIMEOUT
        )

        # Verification history in memory
        self.history = []

        # Configure TTK Styles
        self._setup_styles()

        # Build UI Components
        self._build_header()
        self._build_main_content()
        self._build_status_bar()

        # Initial Server Health Check
        self.after(500, self.check_server_status)

    def _setup_styles(self):
        """Configures modern styling for Tkinter ttk widgets."""
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        # Dark theme palette
        bg_dark = "#0B132B"
        bg_card = "#1C2541"
        fg_white = "#FFFFFF"
        cyan_accent = "#00F0FF"

        self.style.configure("TFrame", background=bg_dark)
        self.style.configure("Card.TFrame", background=bg_card, relief="flat")
        self.style.configure("TLabel", background=bg_dark, foreground=fg_white, font=("Segoe UI", 10))
        self.style.configure("Card.TLabel", background=bg_card, foreground=fg_white, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", background=bg_dark, foreground=cyan_accent, font=("Segoe UI", 16, "bold"))
        self.style.configure("Subheader.TLabel", background=bg_card, foreground=cyan_accent, font=("Segoe UI", 11, "bold"))

        # Buttons
        self.style.configure("Primary.TButton", background="#0077B6", foreground="#FFFFFF", font=("Segoe UI", 10, "bold"), borderwidth=0, padding=6)
        self.style.map("Primary.TButton", background=[("active", "#0096C7")])

        self.style.configure("Success.TButton", background="#059669", foreground="#FFFFFF", font=("Segoe UI", 10, "bold"), borderwidth=0, padding=6)
        self.style.map("Success.TButton", background=[("active", "#10B981")])

        self.style.configure("Secondary.TButton", background="#3A506B", foreground="#FFFFFF", font=("Segoe UI", 9), borderwidth=0, padding=5)
        self.style.map("Secondary.TButton", background=[("active", "#4F6D7A")])

        # Entry fields
        self.style.configure("TEntry", fieldbackground="#0B132B", foreground="#FFFFFF", insertcolor="#00F0FF")

        # Treeview
        self.style.configure("Treeview", background="#1C2541", foreground="#FFFFFF", fieldbackground="#1C2541", font=("Segoe UI", 9), rowheight=24)
        self.style.configure("Treeview.Heading", background="#3A506B", foreground="#FFFFFF", font=("Segoe UI", 9, "bold"))
        self.style.map("Treeview", background=[("selected", "#0077B6")])

    def _build_header(self):
        """Top branding header."""
        header_frame = ttk.Frame(self, padding=(20, 15, 20, 10))
        header_frame.pack(fill="x")

        title_lbl = ttk.Label(header_frame, text="🛡️ VERIRESUME ADMIN PANEL", style="Header.TLabel")
        title_lbl.pack(side="left")

        subtitle_lbl = ttk.Label(
            header_frame,
            text="Academic Demonstration: Socket TCP + SymPy + Multiprocessing + Functional Programming",
            font=("Segoe UI", 9),
            foreground="#8D99AE"
        )
        subtitle_lbl.pack(side="left", padx=15)

        # Server status badge
        self.server_status_lbl = tk.Label(
            header_frame,
            text="Checking Socket Server...",
            font=("Segoe UI", 9, "bold"),
            bg="#374151",
            fg="#9CA3AF",
            padx=10,
            pady=3
        )
        self.server_status_lbl.pack(side="right")

    def _build_main_content(self):
        """Main body with left input panel and right result panel, plus bottom history table."""
        main_paned = ttk.PanedWindow(self, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=15, pady=5)

        # Left Column: Input Form & File Selector
        left_frame = ttk.Frame(main_paned, style="Card.TFrame", padding=15)
        main_paned.add(left_frame, weight=1)

        # Right Column: Verification Results & SymPy Breakdown
        right_frame = ttk.Frame(main_paned, style="Card.TFrame", padding=15)
        main_paned.add(right_frame, weight=1)

        self._build_input_form(left_frame)
        self._build_results_panel(right_frame)

        # Bottom Frame: Verification History Table
        bottom_frame = ttk.Frame(self, style="Card.TFrame", padding=10)
        bottom_frame.pack(fill="both", expand=True, padx=15, pady=(5, 10))

        ttk.Label(bottom_frame, text="📜 VERIFICATION AUDIT TRAIL", style="Subheader.TLabel").pack(anchor="w", pady=(0, 5))

        # History Treeview
        columns = ("id", "candidate", "cert_name", "cert_id", "org", "score", "status", "timestamp")
        self.tree = ttk.Treeview(bottom_frame, columns=columns, show="headings", height=5)
        
        self.tree.heading("id", text="#")
        self.tree.heading("candidate", text="Candidate Name")
        self.tree.heading("cert_name", text="Certificate Name")
        self.tree.heading("cert_id", text="Certificate ID")
        self.tree.heading("org", text="Organization")
        self.tree.heading("score", text="Score")
        self.tree.heading("status", text="Status")
        self.tree.heading("timestamp", text="Time")

        self.tree.column("id", width=30, anchor="center")
        self.tree.column("candidate", width=130)
        self.tree.column("cert_name", width=160)
        self.tree.column("cert_id", width=100)
        self.tree.column("org", width=130)
        self.tree.column("score", width=60, anchor="center")
        self.tree.column("status", width=110, anchor="center")
        self.tree.column("timestamp", width=90, anchor="center")

        tree_scroll = ttk.Scrollbar(bottom_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _build_input_form(self, parent: ttk.Frame):
        """Constructs the certificate input form."""
        ttk.Label(parent, text="📝 CERTIFICATE VERIFICATION FORM", style="Subheader.TLabel").pack(anchor="w", pady=(0, 10))

        # File Chooser Section
        file_frame = ttk.Frame(parent, style="Card.TFrame")
        file_frame.pack(fill="x", pady=(0, 12))

        choose_btn = ttk.Button(file_frame, text="📁 Choose Resume / Certificate File", style="Secondary.TButton", command=self.choose_file)
        choose_btn.pack(side="left", fill="x", expand=True)

        # Form Fields
        fields = [
            ("Candidate Name:", "candidate_var"),
            ("Certificate ID:", "id_var"),
            ("Certificate / Course Name:", "name_var"),
            ("Issuing Organization:", "org_var"),
            ("Issue Date:", "date_var"),
            ("Verification URL (Optional):", "url_var"),
        ]

        self.form_vars = {}
        for label_text, var_name in fields:
            var = tk.StringVar()
            self.form_vars[var_name] = var

            f_frame = ttk.Frame(parent, style="Card.TFrame")
            f_frame.pack(fill="x", pady=3)

            lbl = ttk.Label(f_frame, text=label_text, style="Card.TLabel", width=24, anchor="w")
            lbl.pack(side="left")

            entry = tk.Entry(f_frame, textvariable=var, bg="#0B132B", fg="#FFFFFF", insertbackground="#00F0FF", relief="solid", bd=1)
            entry.pack(side="right", fill="x", expand=True)

        # Pre-populate sample button
        preset_frame = ttk.Frame(parent, style="Card.TFrame")
        preset_frame.pack(fill="x", pady=(8, 12))

        sample1_btn = ttk.Button(preset_frame, text="Sample: Valid", style="Secondary.TButton", command=lambda: self.load_sample("valid"))
        sample1_btn.pack(side="left", fill="x", expand=True, padx=2)

        sample2_btn = ttk.Button(preset_frame, text="Sample: Mismatch", style="Secondary.TButton", command=lambda: self.load_sample("mismatch"))
        sample2_btn.pack(side="left", fill="x", expand=True, padx=2)

        sample3_btn = ttk.Button(preset_frame, text="Sample: Revoked", style="Secondary.TButton", command=lambda: self.load_sample("revoked"))
        sample3_btn.pack(side="left", fill="x", expand=True, padx=2)

        # Action Buttons
        btn_frame = ttk.Frame(parent, style="Card.TFrame")
        btn_frame.pack(fill="x", pady=(5, 0))

        verify_btn = ttk.Button(btn_frame, text="🚀 VERIFY VIA TCP SOCKET", style="Primary.TButton", command=self.verify_certificate_action)
        verify_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        clear_btn = ttk.Button(btn_frame, text="Clear", style="Secondary.TButton", command=self.clear_form)
        clear_btn.pack(side="right", padx=(5, 0))

    def _build_results_panel(self, parent: ttk.Frame):
        """Constructs the verification audit results panel."""
        ttk.Label(parent, text="📊 VERIFICATION AUDIT RESULT", style="Subheader.TLabel").pack(anchor="w", pady=(0, 10))

        # Overall Status Badge & Score Gauge
        badge_frame = ttk.Frame(parent, style="Card.TFrame")
        badge_frame.pack(fill="x", pady=(0, 10))

        self.score_display_lbl = tk.Label(
            badge_frame,
            text="-- %",
            font=("Segoe UI", 28, "bold"),
            bg="#1C2541",
            fg="#00F0FF"
        )
        self.score_display_lbl.pack(side="left", padx=10)

        self.status_display_lbl = tk.Label(
            badge_frame,
            text="READY TO VERIFY",
            font=("Segoe UI", 12, "bold"),
            bg="#374151",
            fg="#F3F4F6",
            padx=12,
            pady=6
        )
        self.status_display_lbl.pack(side="left", fill="x", expand=True, padx=5)

        # Field-level Check Flags
        self.checks_frame = ttk.Frame(parent, style="Card.TFrame")
        self.checks_frame.pack(fill="x", pady=5)

        self.check_labels = {}
        check_items = [
            ("name_match", "Candidate Name Match:"),
            ("certificate_id_match", "Certificate ID Match:"),
            ("course_match", "Course / Title Match:"),
            ("organization_match", "Organization Match:"),
            ("date_match", "Issue Date Match:"),
        ]

        for key, text in check_items:
            row = ttk.Frame(self.checks_frame, style="Card.TFrame")
            row.pack(fill="x", pady=2)

            lbl = ttk.Label(row, text=text, style="Card.TLabel", width=22, anchor="w")
            lbl.pack(side="left")

            val_lbl = tk.Label(row, text="—", font=("Segoe UI", 10, "bold"), bg="#1C2541", fg="#9CA3AF")
            val_lbl.pack(side="right")
            self.check_labels[key] = val_lbl

        # SymPy Symbolic Equation Display Box
        math_box = tk.LabelFrame(parent, text=" SymPy Mathematical Model ", font=("Segoe UI", 8, "bold"), bg="#1C2541", fg="#00F0FF", padx=8, pady=6)
        math_box.pack(fill="x", pady=(10, 5))

        formula_text = f"Formula: {get_symbolic_formula()}"
        self.math_formula_lbl = tk.Label(math_box, text=formula_text, font=("Consolas", 8), bg="#1C2541", fg="#93C5FD", wraplength=400, justify="left")
        self.math_formula_lbl.pack(anchor="w")

        # Official Registry Source & Details
        self.details_lbl = tk.Label(
            parent,
            text="Verification details will be displayed here after querying socket server.",
            font=("Segoe UI", 8),
            bg="#1C2541",
            fg="#D1D5DB",
            wraplength=400,
            justify="left"
        )
        self.details_lbl.pack(anchor="w", pady=(8, 0))

    def _build_status_bar(self):
        """Bottom status bar."""
        status_bar = tk.Frame(self, bg="#000814", height=24)
        status_bar.pack(side="bottom", fill="x")

        self.status_msg_lbl = tk.Label(status_bar, text="Ready. Socket host: 127.0.0.1:9099", font=("Segoe UI", 8), bg="#000814", fg="#8D99AE", anchor="w")
        self.status_msg_lbl.pack(side="left", padx=10)

        refresh_btn = tk.Button(status_bar, text="🔄 Test Socket", font=("Segoe UI", 7), bg="#1C2541", fg="#00F0FF", command=self.check_server_status, bd=0)
        refresh_btn.pack(side="right", padx=10)

    def check_server_status(self):
        """Pings the socket server."""
        alive = self.client.ping()
        if alive:
            self.server_status_lbl.configure(text="● Socket Server: ONLINE", bg="#065F46", fg="#34D399")
            self.status_msg_lbl.configure(text=f"Connected to TCP Socket Server at {config.SOCKET_HOST}:{config.SOCKET_PORT}")
        else:
            self.server_status_lbl.configure(text="● Socket Server: OFFLINE", bg="#7F1D1D", fg="#F87171")
            self.status_msg_lbl.configure(text=f"Cannot reach TCP Socket Server at {config.SOCKET_HOST}:{config.SOCKET_PORT}. Please start socket_server.py.")

    def load_sample(self, sample_type: str):
        """Loads preset sample data for quick viva demonstration."""
        if sample_type == "valid":
            self.form_vars["candidate_var"].set("Alice Johnson")
            self.form_vars["id_var"].set("CERT1001")
            self.form_vars["name_var"].set("Python Programming")
            self.form_vars["org_var"].set("Demo Institute")
            self.form_vars["date_var"].set("2024-05-15")
            self.form_vars["url_var"].set("")
        elif sample_type == "mismatch":
            self.form_vars["candidate_var"].set("John Doe (Mismatched)")
            self.form_vars["id_var"].set("CERT1002")
            self.form_vars["name_var"].set("Web Development")
            self.form_vars["org_var"].set("Demo Institute")
            self.form_vars["date_var"].set("2024-06-20")
            self.form_vars["url_var"].set("")
        elif sample_type == "revoked":
            self.form_vars["candidate_var"].set("Fake Candidate")
            self.form_vars["id_var"].set("CERT9999")
            self.form_vars["name_var"].set("Python Programming")
            self.form_vars["org_vars" if "org_vars" in self.form_vars else "org_var"].set("Demo Institute")
            self.form_vars["date_var"].set("2022-01-01")
            self.form_vars["url_var"].set("")

    def clear_form(self):
        """Clears all input fields and resets display."""
        for var in self.form_vars.values():
            var.set("")
        self.score_display_lbl.configure(text="-- %", fg="#00F0FF")
        self.status_display_lbl.configure(text="READY TO VERIFY", bg="#374151", fg="#F3F4F6")
        for lbl in self.check_labels.values():
            lbl.configure(text="—", fg="#9CA3AF")
        self.details_lbl.configure(text="Verification details will be displayed here after querying socket server.")

    def choose_file(self):
        """Opens file picker to load resume or certificate file."""
        file_path = filedialog.askopenfilename(
            title="Select Resume or Certificate",
            filetypes=[("Documents", "*.pdf *.docx *.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            path_obj = Path(file_path)
            parsed = resume_parser.parse_file(path_obj)
            
            if parsed.get("candidate_name") and parsed["candidate_name"] != "Candidate":
                self.form_vars["candidate_var"].set(parsed["candidate_name"])

            certs = parsed.get("certificates", [])
            if certs:
                first_cert = certs[0]
                self.form_vars["name_var"].set(first_cert.get("certificate_name", ""))
                self.form_vars["id_var"].set(first_cert.get("certificate_id", ""))
                self.form_vars["org_var"].set(first_cert.get("issuing_organization", ""))
                self.form_vars["date_var"].set(first_cert.get("issue_date", ""))
                self.form_vars["url_var"].set(first_cert.get("verification_url", ""))
                messagebox.showinfo("Document Parsed", f"Successfully extracted candidate name and {len(certs)} certificate(s) from {path_obj.name}.")
            else:
                messagebox.showinfo("Document Parsed", f"Extracted candidate details from {path_obj.name}. No certificate IDs detected in text.")
        except Exception as e:
            messagebox.showerror("Parse Error", f"Error parsing document: {e}")

    def verify_certificate_action(self):
        """Transmits form certificate payload over TCP socket."""
        cert_payload = {
            "candidate_name": self.form_vars["candidate_var"].get().strip(),
            "certificate_id": self.form_vars["id_var"].get().strip(),
            "certificate_name": self.form_vars["name_var"].get().strip(),
            "issuing_organization": self.form_vars["org_var"].get().strip(),
            "issue_date": self.form_vars["date_var"].get().strip(),
            "verification_url": self.form_vars["url_var"].get().strip(),
        }

        if not cert_payload["certificate_name"] and not cert_payload["certificate_id"]:
            messagebox.showwarning("Validation Error", "Please provide at least a Certificate Name or Certificate ID.")
            return

        self.status_msg_lbl.configure(text="Transmitting TCP socket verification request...")
        self.update_idletasks()

        # Send over TCP socket
        res = self.client.verify_certificate(cert_payload)

        # Update Display
        score = res.get("score", 0.0)
        status = res.get("status", "UNABLE_TO_VERIFY")

        # Color coding
        if status == "VERIFIED":
            color = "#10B981"
            status_bg = "#065F46"
        elif status == "REVIEW REQUIRED":
            color = "#F59E0B"
            status_bg = "#92400E"
        elif status == "SUSPICIOUS":
            color = "#EF4444"
            status_bg = "#991B1B"
        else:
            color = "#DC2626"
            status_bg = "#7F1D1D"

        self.score_display_lbl.configure(text=f"{int(score)}%", fg=color)
        self.status_display_lbl.configure(text=status, bg=status_bg, fg="#FFFFFF")

        # Update check indicators
        checks = res.get("checks", {})
        for k, lbl in self.check_labels.items():
            is_match = checks.get(k, False)
            if is_match is True or (isinstance(is_match, (int, float)) and is_match > 0.6):
                lbl.configure(text="✓ MATCH", fg="#10B981")
            elif is_match is False or is_match == 0:
                lbl.configure(text="✗ MISMATCH", fg="#EF4444")
            else:
                lbl.configure(text="~ PARTIAL", fg="#F59E0B")

        # Details
        source = res.get("verification_source", "N/A")
        details = res.get("details", "")
        self.details_lbl.configure(text=f"Source: {source}\nDetails: {details}")

        # Add to history
        item_id = len(self.history) + 1
        now_str = datetime.now().strftime("%H:%M:%S")
        self.history.append((res, cert_payload))

        self.tree.insert("", 0, values=(
            item_id,
            cert_payload["candidate_name"] or "N/A",
            cert_payload["certificate_name"] or "N/A",
            cert_payload["certificate_id"] or "N/A",
            cert_payload["issuing_organization"] or "N/A",
            f"{int(score)}%",
            status,
            now_str
        ))

        self.status_msg_lbl.configure(text=f"Verified: {status} (Score: {score}%). Socket TCP roundtrip complete.")

    def _on_tree_select(self, event):
        """Displays details when history item is clicked."""
        selected = self.tree.selection()
        if not selected:
            return
        # Fetch item values
        item = self.tree.item(selected[0])
        vals = item.get("values", [])
        if vals:
            self.status_msg_lbl.configure(text=f"Selected history record #{vals[0]} - {vals[1]} ({vals[6]})")


def run_gui():
    """Runs the Tkinter Desktop Application."""
    app = TkinterAdminApp()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
