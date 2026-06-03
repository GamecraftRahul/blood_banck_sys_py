"""
blood_bank_gui.py
A full-featured Blood Bank Management GUI (Tkinter + ttkbootstrap)
Connects to MySQL database 'blood_bank_system' (use provided SQL script earlier)
"""

import mysql.connector
from mysql.connector import Error
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox, StringVar, Toplevel
import csv
import os
import math
import datetime

# ----------------------
# DATABASE CONFIG - EDIT THESE
# ----------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "RAHUL123",  # <<-- CHANGE THIS
    "database": "blood_bank_system",
    "auth_plugin": "mysql_native_password"  # keep for compatibility
}

# ----------------------
# DB UTILITIES
# ----------------------
def get_connection():
    """Return a new DB connection."""
    return mysql.connector.connect(**DB_CONFIG)

def safe_execute(query, params=None, fetch=False):
    """Helper to execute queries safely."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        if fetch:
            return cursor.fetchall()
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        raise
    finally:
        if conn:
            conn.close()

# ----------------------
# CONSTANTS (pagination)
# ----------------------
PAGE_SIZE = 12  # rows per page (small enough to be snappy)

# ----------------------
# APPLICATION SETUP
# ----------------------
app = tb.Window(themename="minty")   # choose an attractive theme
app.title("Blood Bank Management System")
app.geometry("1100x700")

# ---------- Styles / Global fonts ----------
FONT_HEADER = ("Helvetica", 16, "bold")
FONT_NORMAL = ("Helvetica", 11)

# ----------------------
# UI COMPONENTS: top title
# ----------------------
header = tb.Frame(app)
header.pack(fill="x", pady=(10, 5), padx=12)

title_label = tb.Label(header, text="🩸 Blood Bank Management System", font=FONT_HEADER)
title_label.pack(side="left")

date_label = tb.Label(header, text=datetime.datetime.now().strftime("%b %d, %Y  •  %H:%M"), font=("Helvetica", 10))
date_label.pack(side="right")

# ----------------------
# Notebook (Tabs)
# ----------------------
notebook = ttk.Notebook(app)
notebook.pack(fill="both", expand=True, padx=12, pady=8)

# We'll create frames for each tab
frame_dashboard = ttk.Frame(notebook)
frame_donors = ttk.Frame(notebook)
frame_patients = ttk.Frame(notebook)
frame_reports = ttk.Frame(notebook)

notebook.add(frame_dashboard, text="Dashboard")
notebook.add(frame_donors, text="Donors")
notebook.add(frame_patients, text="Patients")
notebook.add(frame_reports, text="Reports")

# ----------------------
# DASHBOARD - summary cards + quick search
# ----------------------
def load_dashboard():
    """Load summary counts by blood group and totals."""
    try:
        rows = safe_execute(
            "SELECT blood_group, COUNT(*) FROM donors GROUP BY blood_group", fetch=True
        )
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not load dashboard:\n{e}")
        return

    # clear area
    for w in dash_cards_frame.winfo_children():
        w.destroy()

    # build cards for each blood group (sorted)
    rows = sorted(rows, key=lambda r: r[0] or "")
    total = 0
    for bg, cnt in rows:
        total += cnt
        card = tb.Frame(dash_cards_frame, bootstyle="info", padding=12, relief="raised")
        card.pack(side="left", padx=8, pady=8, ipadx=8, ipady=8)
        tb.Label(card, text=f"{bg}", font=("Helvetica", 14, "bold")).pack(anchor="center")
        tb.Label(card, text=f"Donors: {cnt}", font=("Helvetica", 12)).pack(anchor="center")

    # total card
    total_card = tb.Frame(dash_cards_frame, bootstyle="secondary", padding=12, relief="raised")
    total_card.pack(side="left", padx=8, pady=8, ipadx=8, ipady=8)
    tb.Label(total_card, text="Total Donors", font=("Helvetica", 14, "bold")).pack()
    tb.Label(total_card, text=str(total), font=("Helvetica", 12)).pack()

def quick_search_donors():
    """Switch to donors tab and search."""
    notebook.select(frame_donors)
    donor_search_var.set(donor_quick_search_var.get())
    donors_refresh()

# Dashboard layout
dash_top = tb.Frame(frame_dashboard)
dash_top.pack(fill="x", pady=(12,6), padx=12)

tb.Label(dash_top, text="Dashboard", font=FONT_HEADER).pack(side="left")

# quick search from dashboard
donor_quick_search_var = StringVar()
quick_search_entry = tb.Entry(dash_top, textvariable=donor_quick_search_var, width=25)
quick_search_entry.pack(side="right", padx=6)
tb.Button(dash_top, text="Search Donors ➜", bootstyle="outline-info", command=quick_search_donors).pack(side="right")

dash_cards_frame = tb.Frame(frame_dashboard)
dash_cards_frame.pack(fill="x", padx=12, pady=6)

# initial load
load_dashboard()

# ----------------------
# Shared helpers for treeview (Donors & Patients)
# ----------------------
def make_tree(parent, cols, widths=None):
    tv = ttk.Treeview(parent, columns=cols, show="headings", height=12)
    for i, col in enumerate(cols):
        tv.heading(col, text=col)
        tv.column(col, width=(widths[i] if widths else 120), anchor="center")
    vsb = ttk.Scrollbar(parent, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=vsb.set)
    return tv, vsb

# ----------------------
# DONORS TAB
# ----------------------
donor_top = tb.Frame(frame_donors)
donor_top.pack(fill="x", padx=12, pady=8)

tb.Label(donor_top, text="Donors", font=FONT_HEADER).pack(side="left")

# Search area
donor_filters = tb.Frame(frame_donors)
donor_filters.pack(fill="x", padx=12, pady=(0,6))

donor_search_var = StringVar()
donor_bg_var = StringVar()
donor_mobile_var = StringVar()

tb.Label(donor_filters, text="Name:").pack(side="left", padx=(6,4))
donor_entry = tb.Entry(donor_filters, textvariable=donor_search_var, width=20)
donor_entry.pack(side="left", padx=4)

tb.Label(donor_filters, text="Blood:").pack(side="left", padx=(8,4))
donor_bg_entry = tb.Entry(donor_filters, textvariable=donor_bg_var, width=8)
donor_bg_entry.pack(side="left", padx=4)

tb.Label(donor_filters, text="Mobile:").pack(side="left", padx=(8,4))
donor_mobile_entry = tb.Entry(donor_filters, textvariable=donor_mobile_var, width=12)
donor_mobile_entry.pack(side="left", padx=4)

tb.Button(donor_filters, text="Search", bootstyle="info", command=lambda: set_page_and_refresh('donor', 1)).pack(side="left", padx=8)
tb.Button(donor_filters, text="Show All", bootstyle="secondary", command=lambda: clear_filters_and_refresh('donor')).pack(side="left", padx=4)
tb.Button(donor_filters, text="Add Donor", bootstyle="success", command=lambda: open_donor_form()).pack(side="right", padx=6)
tb.Button(donor_filters, text="Export CSV", bootstyle="outline-primary", command=lambda: export_visible('donor')).pack(side="right", padx=6)

# Table area
donor_table_frame = tb.Frame(frame_donors)
donor_table_frame.pack(fill="both", expand=True, padx=12, pady=6)

donor_cols = ("ID", "Name", "Blood Group", "Mobile", "Address")
donor_tree, donor_vsb = make_tree(donor_table_frame, donor_cols, widths=[60,260,120,140,260])
donor_tree.pack(side="left", fill="both", expand=True)
donor_vsb.pack(side="left", fill="y")

# Row actions
donor_actions = tb.Frame(frame_donors)
donor_actions.pack(fill="x", padx=12, pady=(6,12))
tb.Button(donor_actions, text="Edit Selected", bootstyle="warning", command=lambda: edit_selected('donor')).pack(side="left", padx=6)
tb.Button(donor_actions, text="Delete Selected", bootstyle="danger", command=lambda: delete_selected('donor')).pack(side="left", padx=6)

# Pagination controls
donor_pagination = {'page': 1, 'total_pages': 1}
donor_pagination_frame = tb.Frame(frame_donors)
donor_pagination_frame.pack(fill="x", padx=12, pady=(0,12))

donor_page_label = tb.Label(donor_pagination_frame, text="Page 1 / 1")
donor_page_label.pack(side="left")

def set_page_and_refresh(kind, page):
    if kind == 'donor':
        donor_pagination['page'] = max(1, int(page))
        donors_refresh()
    else:
        patient_pagination['page'] = max(1, int(page))
        patients_refresh()

def clear_filters_and_refresh(kind):
    if kind == 'donor':
        donor_search_var.set("")
        donor_bg_var.set("")
        donor_mobile_var.set("")
        donor_pagination['page'] = 1
        donors_refresh()
    else:
        patient_search_var.set("")
        patient_bg_var.set("")
        patient_mobile_var.set("")
        patient_pagination['page'] = 1
        patients_refresh()

def donors_refresh():
    """Load donors with pagination and filters applied."""
    page = donor_pagination['page']
    offset = (page - 1) * PAGE_SIZE

    base_query = "SELECT donor_id, name, blood_group, mobile, address FROM donors WHERE 1=1"
    count_query = "SELECT COUNT(*) FROM donors WHERE 1=1"
    params = []
    where_clauses = []

    name_filter = donor_search_var.get().strip()
    if name_filter:
        where_clauses.append(" AND name LIKE %s")
        params.append(f"%{name_filter}%")

    bg_filter = donor_bg_var.get().strip()
    if bg_filter:
        where_clauses.append(" AND blood_group LIKE %s")
        params.append(f"%{bg_filter}%")

    mobile_filter = donor_mobile_var.get().strip()
    if mobile_filter:
        where_clauses.append(" AND mobile LIKE %s")
        params.append(f"%{mobile_filter}%")

    where_sql = "".join(where_clauses)
    try:
        total_rows = safe_execute(count_query + where_sql, tuple(params), fetch=True)[0][0]
        total_pages = max(1, math.ceil(total_rows / PAGE_SIZE))
        donor_pagination['total_pages'] = total_pages

        rows = safe_execute(base_query + where_sql + " ORDER BY donor_id DESC LIMIT %s OFFSET %s",
                             tuple(params + [PAGE_SIZE, offset]), fetch=True)
    except Exception as e:
        messagebox.showerror("DB Error", f"Could not fetch donors:\n{e}")
        return

    # populate tree
    donor_tree.delete(*donor_tree.get_children())
    for r in rows:
        donor_tree.insert("", "end", values=r)

    donor_page_label.config(text=f"Page {page} / {total_pages}")

def donors_prev():
    if donor_pagination['page'] > 1:
        donor_pagination['page'] -= 1
        donors_refresh()

def donors_next():
    if donor_pagination['page'] < donor_pagination['total_pages']:
        donor_pagination['page'] += 1
        donors_refresh()

# small pagination buttons
tb.Button(donor_pagination_frame, text="← Prev", bootstyle="outline-secondary", command=donors_prev).pack(side="right", padx=4)
tb.Button(donor_pagination_frame, text="Next →", bootstyle="outline-secondary", command=donors_next).pack(side="right", padx=4)

# ----------------------
# PATIENTS TAB (mirrors donors with required_blood_group)
# ----------------------
patient_top = tb.Frame(frame_patients)
patient_top.pack(fill="x", padx=12, pady=8)

tb.Label(patient_top, text="Patients", font=FONT_HEADER).pack(side="left")

patient_filters = tb.Frame(frame_patients)
patient_filters.pack(fill="x", padx=12, pady=(0,6))

patient_search_var = StringVar()
patient_bg_var = StringVar()
patient_mobile_var = StringVar()

tb.Label(patient_filters, text="Name:").pack(side="left", padx=(6,4))
patient_entry = tb.Entry(patient_filters, textvariable=patient_search_var, width=20)
patient_entry.pack(side="left", padx=4)

tb.Label(patient_filters, text="Required Blood:").pack(side="left", padx=(8,4))
patient_bg_entry = tb.Entry(patient_filters, textvariable=patient_bg_var, width=8)
patient_bg_entry.pack(side="left", padx=4)

tb.Label(patient_filters, text="Mobile:").pack(side="left", padx=(8,4))
patient_mobile_entry = tb.Entry(patient_filters, textvariable=patient_mobile_var, width=12)
patient_mobile_entry.pack(side="left", padx=4)

tb.Button(patient_filters, text="Search", bootstyle="info", command=lambda: set_page_and_refresh('patient', 1)).pack(side="left", padx=8)
tb.Button(patient_filters, text="Show All", bootstyle="secondary", command=lambda: clear_filters_and_refresh('patient')).pack(side="left", padx=4)
tb.Button(patient_filters, text="Add Patient", bootstyle="success", command=lambda: open_patient_form()).pack(side="right", padx=6)
tb.Button(patient_filters, text="Export CSV", bootstyle="outline-primary", command=lambda: export_visible('patient')).pack(side="right", padx=6)

patient_table_frame = tb.Frame(frame_patients)
patient_table_frame.pack(fill="both", expand=True, padx=12, pady=6)

patient_cols = ("ID", "Name", "Required Blood", "Mobile", "Disease")
patient_tree, patient_vsb = make_tree(patient_table_frame, patient_cols, widths=[60,260,140,140,300])
patient_tree.pack(side="left", fill="both", expand=True)
patient_vsb.pack(side="left", fill="y")

patient_actions = tb.Frame(frame_patients)
patient_actions.pack(fill="x", padx=12, pady=(6,12))
tb.Button(patient_actions, text="Edit Selected", bootstyle="warning", command=lambda: edit_selected('patient')).pack(side="left", padx=6)
tb.Button(patient_actions, text="Delete Selected", bootstyle="danger", command=lambda: delete_selected('patient')).pack(side="left", padx=6)

patient_pagination = {'page': 1, 'total_pages': 1}
patient_pagination_frame = tb.Frame(frame_patients)
patient_pagination_frame.pack(fill="x", padx=12, pady=(0,12))

patient_page_label = tb.Label(patient_pagination_frame, text="Page 1 / 1")
patient_page_label.pack(side="left")

def patients_refresh():
    page = patient_pagination['page']
    offset = (page - 1) * PAGE_SIZE

    base_query = "SELECT patient_id, name, required_blood_group, mobile, disease FROM patients WHERE 1=1"
    count_query = "SELECT COUNT(*) FROM patients WHERE 1=1"
    params = []
    where_clauses = []

    name_filter = patient_search_var.get().strip()
    if name_filter:
        where_clauses.append(" AND name LIKE %s")
        params.append(f"%{name_filter}%")

    bg_filter = patient_bg_var.get().strip()
    if bg_filter:
        where_clauses.append(" AND required_blood_group LIKE %s")
        params.append(f"%{bg_filter}%")

    mobile_filter = patient_mobile_var.get().strip()
    if mobile_filter:
        where_clauses.append(" AND mobile LIKE %s")
        params.append(f"%{mobile_filter}%")

    where_sql = "".join(where_clauses)
    try:
        total_rows = safe_execute(count_query + where_sql, tuple(params), fetch=True)[0][0]
        total_pages = max(1, math.ceil(total_rows / PAGE_SIZE))
        patient_pagination['total_pages'] = total_pages

        rows = safe_execute(base_query + where_sql + " ORDER BY patient_id DESC LIMIT %s OFFSET %s",
                             tuple(params + [PAGE_SIZE, offset]), fetch=True)
    except Exception as e:
        messagebox.showerror("DB Error", f"Could not fetch patients:\n{e}")
        return

    patient_tree.delete(*patient_tree.get_children())
    for r in rows:
        patient_tree.insert("", "end", values=r)

    patient_page_label.config(text=f"Page {page} / {total_pages}")

def patients_prev():
    if patient_pagination['page'] > 1:
        patient_pagination['page'] -= 1
        patients_refresh()

def patients_next():
    if patient_pagination['page'] < patient_pagination['total_pages']:
        patient_pagination['page'] += 1
        patients_refresh()

tb.Button(patient_pagination_frame, text="← Prev", bootstyle="outline-secondary", command=patients_prev).pack(side="right", padx=4)
tb.Button(patient_pagination_frame, text="Next →", bootstyle="outline-secondary", command=patients_next).pack(side="right", padx=4)

# ----------------------
# Forms: Add / Edit Donor & Patient
# ----------------------
def open_donor_form(edit=False, row_values=None):
    win = Toplevel(app)
    win.title("Edit Donor" if edit else "Add Donor")
    win.geometry("420x320")
    win.transient(app)
    win.grab_set()

    name_var = StringVar(value=row_values[1] if edit else "")
    bg_var = StringVar(value=row_values[2] if edit else "")
    mobile_var = StringVar(value=row_values[3] if edit else "")
    address_var = StringVar(value=row_values[4] if edit else "")

    tb.Label(win, text="Name:").pack(anchor="w", padx=12, pady=(12,4))
    e1 = tb.Entry(win, textvariable=name_var, width=40); e1.pack(padx=12)

    tb.Label(win, text="Blood Group:").pack(anchor="w", padx=12, pady=(8,4))
    e2 = tb.Entry(win, textvariable=bg_var, width=16); e2.pack(padx=12)

    tb.Label(win, text="Mobile:").pack(anchor="w", padx=12, pady=(8,4))
    e3 = tb.Entry(win, textvariable=mobile_var, width=20); e3.pack(padx=12)

    tb.Label(win, text="Address:").pack(anchor="w", padx=12, pady=(8,4))
    e4 = tb.Entry(win, textvariable=address_var, width=40); e4.pack(padx=12)

    def submit():
        name = name_var.get().strip()
        bg = bg_var.get().strip()
        mob = mobile_var.get().strip()
        addr = address_var.get().strip()
        if not name or not bg or not mob:
            messagebox.showwarning("Validation", "Name, Blood Group and Mobile are required.")
            return
        try:
            if edit:
                donor_id = row_values[0]
                safe_execute("UPDATE donors SET name=%s, blood_group=%s, mobile=%s, address=%s WHERE donor_id=%s",
                             (name, bg, mob, addr, donor_id))
                messagebox.showinfo("Success", "Donor updated.")
            else:
                safe_execute("INSERT INTO donors (name, blood_group, mobile, address) VALUES (%s,%s,%s,%s)",
                             (name, bg, mob, addr))
                messagebox.showinfo("Success", "Donor added.")
            win.destroy()
            donors_refresh()
            load_dashboard()
        except Exception as e:
            messagebox.showerror("DB Error", f"{e}")

    tb.Button(win, text="Save", bootstyle="success", command=submit).pack(pady=12)

def open_patient_form(edit=False, row_values=None):
    win = Toplevel(app)
    win.title("Edit Patient" if edit else "Add Patient")
    win.geometry("420x360")
    win.transient(app)
    win.grab_set()

    name_var = StringVar(value=row_values[1] if edit else "")
    bg_var = StringVar(value=row_values[2] if edit else "")
    mobile_var = StringVar(value=row_values[3] if edit else "")
    disease_var = StringVar(value=row_values[4] if edit else "")

    tb.Label(win, text="Name:").pack(anchor="w", padx=12, pady=(12,4))
    e1 = tb.Entry(win, textvariable=name_var, width=40); e1.pack(padx=12)

    tb.Label(win, text="Required Blood Group:").pack(anchor="w", padx=12, pady=(8,4))
    e2 = tb.Entry(win, textvariable=bg_var, width=16); e2.pack(padx=12)

    tb.Label(win, text="Mobile:").pack(anchor="w", padx=12, pady=(8,4))
    e3 = tb.Entry(win, textvariable=mobile_var, width=20); e3.pack(padx=12)

    tb.Label(win, text="Disease/Notes:").pack(anchor="w", padx=12, pady=(8,4))
    e4 = tb.Entry(win, textvariable=disease_var, width=40); e4.pack(padx=12)

    def submit():
        name = name_var.get().strip()
        bg = bg_var.get().strip()
        mob = mobile_var.get().strip()
        dis = disease_var.get().strip()
        if not name or not bg or not mob:
            messagebox.showwarning("Validation", "Name, Required Blood and Mobile are required.")
            return
        try:
            if edit:
                patient_id = row_values[0]
                safe_execute("UPDATE patients SET name=%s, required_blood_group=%s, mobile=%s, disease=%s WHERE patient_id=%s",
                             (name, bg, mob, dis, patient_id))
                messagebox.showinfo("Success", "Patient updated.")
            else:
                safe_execute("INSERT INTO patients (name, required_blood_group, mobile, disease) VALUES (%s,%s,%s,%s)",
                             (name, bg, mob, dis))
                messagebox.showinfo("Success", "Patient added.")
            win.destroy()
            patients_refresh()
        except Exception as e:
            messagebox.showerror("DB Error", f"{e}")

    tb.Button(win, text="Save", bootstyle="success", command=submit).pack(pady=12)

# ----------------------
# Edit/Delete selected
# ----------------------
def edit_selected(kind):
    if kind == 'donor':
        sel = donor_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a donor to edit.")
            return
        vals = donor_tree.item(sel[0])['values']
        open_donor_form(edit=True, row_values=vals)
    else:
        sel = patient_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a patient to edit.")
            return
        vals = patient_tree.item(sel[0])['values']
        open_patient_form(edit=True, row_values=vals)

def delete_selected(kind):
    if kind == 'donor':
        sel = donor_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a donor to delete.")
            return
        vals = donor_tree.item(sel[0])['values']
        if messagebox.askyesno("Confirm Delete", f"Delete donor '{vals[1]}' (ID {vals[0]})?"):
            try:
                safe_execute("DELETE FROM donors WHERE donor_id=%s", (vals[0],))
                messagebox.showinfo("Deleted", "Donor deleted.")
                donors_refresh()
                load_dashboard()
            except Exception as e:
                messagebox.showerror("DB Error", f"{e}")
    else:
        sel = patient_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a patient to delete.")
            return
        vals = patient_tree.item(sel[0])['values']
        if messagebox.askyesno("Confirm Delete", f"Delete patient '{vals[1]}' (ID {vals[0]})?"):
            try:
                safe_execute("DELETE FROM patients WHERE patient_id=%s", (vals[0],))
                messagebox.showinfo("Deleted", "Patient deleted.")
                patients_refresh()
            except Exception as e:
                messagebox.showerror("DB Error", f"{e}")

# ----------------------
# Export visible rows to CSV
# ----------------------
def export_visible(kind):
    if kind == 'donor':
        rows = [donor_tree.item(i)['values'] for i in donor_tree.get_children()]
        cols = donor_cols
        default_name = f"donors_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    else:
        rows = [patient_tree.item(i)['values'] for i in patient_tree.get_children()]
        cols = patient_cols
        default_name = f"patients_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    if not rows:
        messagebox.showinfo("No Data", "No visible rows to export.")
        return

    try:
        path = os.path.join(os.getcwd(), default_name)
        with open(path, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(cols)
            writer.writerows(rows)
        messagebox.showinfo("Exported", f"Exported {len(rows)} rows to:\n{path}")
    except Exception as e:
        messagebox.showerror("Export Error", f"{e}")

# ----------------------
# REPORTS TAB (simple lists & summary)
# ----------------------
def load_reports():
    # summary counts donors and patients
    try:
        d_total = safe_execute("SELECT COUNT(*) FROM donors", fetch=True)[0][0]
        p_total = safe_execute("SELECT COUNT(*) FROM patients", fetch=True)[0][0]
        by_bg = safe_execute("SELECT blood_group, COUNT(*) FROM donors GROUP BY blood_group", fetch=True)
    except Exception as e:
        messagebox.showerror("DB Error", f"{e}")
        return

    # clear
    for w in reports_frame.winfo_children():
        w.destroy()

    # summary
    sframe = tb.Frame(reports_frame)
    sframe.pack(fill="x", padx=12, pady=8)
    tb.Label(sframe, text=f"Total Donors: {d_total}", font=("Helvetica", 12, "bold")).pack(side="left", padx=8)
    tb.Label(sframe, text=f"Total Patients: {p_total}", font=("Helvetica", 12, "bold")).pack(side="left", padx=16)

    # table for blood groups
    tb.Label(reports_frame, text="Donor Count by Blood Group", font=("Helvetica", 13)).pack(anchor="w", padx=12)
    rpt = ttk.Treeview(reports_frame, columns=("Blood Group", "Count"), show="headings", height=8)
    rpt.heading("Blood Group", text="Blood Group"); rpt.heading("Count", text="Count")
    rpt.column("Blood Group", width=150, anchor="center"); rpt.column("Count", width=80, anchor="center")
    rpt.pack(padx=12, pady=6)
    for row in by_bg:
        rpt.insert("", "end", values=row)

# reports frame container
reports_frame = tb.Frame(frame_reports)
reports_frame.pack(fill="both", expand=True)
load_reports()

# ----------------------
# Initialize: load first pages
# ----------------------
donors_refresh()
patients_refresh()

# refresh dashboard when switching to it
def on_tab_changed(event):
    sel = event.widget.index("current")
    if sel == 0:
        load_dashboard()
    elif sel == 3:
        load_reports()

notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

# ----------------------
# Start mainloop
# ----------------------
app.mainloop()
