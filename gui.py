import os
import json
import csv
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# File paths for persistent storage
sources_file = "sources.json"
data_entries_file = "ResearchTopicNetwork.csv"

# Default sources dictionary
default_sources = {
    "Working Memory": "Concept",
    "AX-CPT": "Method",
    "Cognitive Control": "Concept",
    "Emotional Resilience": "Concept",
    "Executive Functions": "Concept",
    "Eye Tracking": "Method",
    "Network Modeling": "Method",
    "Latent Variable Modeling": "Method",
    "ACT-R": "Method",
    "Tactile Perception": "Concept",
    "Cognitive Modeling": "Method",
    "Virtual Reality": "Method",
    "Psychophysics": "Method",
    "Event Cognition": "Concept"
}


# -----------------------------
# Load/Save Sources
# -----------------------------
def load_sources():
    if os.path.exists(sources_file):
        with open(sources_file, "r") as f:
            return json.load(f)
    else:
        return default_sources.copy()


def save_sources(sources_dict):
    with open(sources_file, "w") as f:
        json.dump(sources_dict, f, indent=4)


# -----------------------------
# Load/Save Data Entries
# -----------------------------
def load_data_entries():
    entries = []
    if os.path.exists(data_entries_file):
        with open(data_entries_file, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                entries.append((row["Source"], row["Target"], row["Type"], row["Subject"]))
    return entries


def save_data_entries(entries):
    with open(data_entries_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Source", "Target", "Type", "Subject"])
        for entry in entries:
            writer.writerow(entry)


# -----------------------------
# Main Application
# -----------------------------
sources_dict = load_sources()
data_entries = load_data_entries()

root = tk.Tk()
root.title("Research Data Input")

# Create a canvas and a vertical scrollbar for it
canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

# Pack the canvas and scrollbar
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Create a frame inside the canvas which will contain your GUI widgets
scrollable_frame = ttk.Frame(canvas)

# Make the scrollable_frame expand to the canvas' width
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

# Add the frame to the canvas
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def _bind_mousewheel(event):
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

def _unbind_mousewheel(event):
    canvas.unbind_all("<MouseWheel>")

# Bind the mouse wheel when the cursor enters the canvas and unbind when it leaves
canvas.bind("<Enter>", _bind_mousewheel)
canvas.bind("<Leave>", _unbind_mousewheel)

# ----------------------------
# Section: Input New Data
# ----------------------------
input_frame = tk.LabelFrame(scrollable_frame, text="Input New Data", padx=10, pady=10)
input_frame.pack(padx=10, pady=10, fill="x")

tk.Label(input_frame, text="Title of Project:").grid(row=0, column=0, sticky="w")
project_entry = tk.Entry(input_frame, width=50)
project_entry.grid(row=0, column=1, padx=5, pady=5)

checkbox_frame = tk.LabelFrame(input_frame, text="Select Source Tags", padx=10, pady=10)
checkbox_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="w")

checkbox_vars = {}


def update_checkboxes():
    for widget in checkbox_frame.winfo_children():
        widget.destroy()
    checkbox_vars.clear()

    concept_sources = sorted([s for s, subj in sources_dict.items() if subj == "Concept"])
    method_sources = sorted([s for s, subj in sources_dict.items() if subj == "Method"])

    row_index = 0
    if concept_sources:
        header = tk.Label(checkbox_frame, text="Concepts", font=("Arial", 10, "bold"))
        header.grid(row=row_index, column=0, sticky="w", pady=(0, 5))
        row_index += 1
        for source in concept_sources:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(checkbox_frame, text=f"{source} (Concept)", variable=var)
            chk.grid(row=row_index, column=0, sticky="w")
            checkbox_vars[source] = var
            row_index += 1

    if concept_sources and method_sources:
        row_index += 1

    if method_sources:
        header = tk.Label(checkbox_frame, text="Methods", font=("Arial", 10, "bold"))
        header.grid(row=row_index, column=0, sticky="w", pady=(0, 5))
        row_index += 1
        for source in method_sources:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(checkbox_frame, text=f"{source} (Method)", variable=var)
            chk.grid(row=row_index, column=0, sticky="w")
            checkbox_vars[source] = var
            row_index += 1


update_checkboxes()


def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    if os.path.exists(data_entries_file):
        with open(data_entries_file, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                tree.insert("", tk.END, values=(row["Source"], row["Target"], row["Type"], row["Subject"]))


def submit_data():
    project_title = project_entry.get().strip()
    if not project_title:
        messagebox.showerror("Error", "Please enter a project title.")
        return

    new_entries = []
    for source, var in checkbox_vars.items():
        if var.get():
            subject = sources_dict[source]
            new_entries.append((source, project_title, "Undirected", subject))

    if not new_entries:
        messagebox.showerror("Error", "Please select at least one source tag.")
        return

    data_entries.extend(new_entries)
    save_data_entries(data_entries)
    refresh_table()

    project_entry.delete(0, tk.END)
    for var in checkbox_vars.values():
        var.set(False)

    messagebox.showinfo("Success", f"Added {len(new_entries)} new data entries.")


submit_button = tk.Button(input_frame, text="Submit New Data", command=submit_data)
submit_button.grid(row=2, column=0, columnspan=2, pady=10)

# ----------------------------
# Section: Add New Source Tag
# ----------------------------
new_source_frame = tk.LabelFrame(scrollable_frame, text="Add New Source Tag", padx=10, pady=10)
new_source_frame.pack(padx=10, pady=10, fill="x")

tk.Label(new_source_frame, text="Source Name:").grid(row=0, column=0, sticky="w")
new_source_entry = tk.Entry(new_source_frame, width=30)
new_source_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(new_source_frame, text="Subject Type:").grid(row=1, column=0, sticky="w")
subject_var = tk.StringVar(value="Concept")
subject_dropdown = ttk.Combobox(new_source_frame, textvariable=subject_var, values=["Concept", "Method"],
                                state="readonly", width=27)
subject_dropdown.grid(row=1, column=1, padx=5, pady=5)


def add_new_source():
    source_name = new_source_entry.get().strip()
    subject_type = subject_var.get().strip()
    if not source_name:
        messagebox.showerror("Error", "Please enter a source name.")
        return
    if source_name in sources_dict:
        messagebox.showerror("Error", "Source already exists.")
        return
    sources_dict[source_name] = subject_type
    save_sources(sources_dict)
    update_checkboxes()
    delete_source_dropdown['values'] = sorted(list(sources_dict.keys()))
    new_source_entry.delete(0, tk.END)
    messagebox.showinfo("Success", f"Added new source: {source_name} ({subject_type}).")


add_source_button = tk.Button(new_source_frame, text="Add New Source", command=add_new_source)
add_source_button.grid(row=2, column=0, columnspan=2, pady=10)

# ----------------------------
# Section: Delete Source Tag
# ----------------------------
delete_source_frame = tk.LabelFrame(scrollable_frame, text="Delete Source Tag", padx=10, pady=10)
delete_source_frame.pack(padx=10, pady=10, fill="x")

tk.Label(delete_source_frame, text="Select Source to Delete:").grid(row=0, column=0, sticky="w")
delete_source_var = tk.StringVar()
delete_source_dropdown = ttk.Combobox(delete_source_frame, textvariable=delete_source_var,
                                      values=sorted(list(sources_dict.keys())), state="readonly", width=27)
delete_source_dropdown.grid(row=0, column=1, padx=5, pady=5)


def delete_source():
    source_to_delete = delete_source_var.get()
    if not source_to_delete:
        messagebox.showerror("Error", "Please select a source to delete.")
        return

    related_entries = [entry for entry in data_entries if entry[0] == source_to_delete]
    if related_entries:
        related_projects = "\n".join(sorted(set([entry[1] for entry in related_entries])))
        message = (f"Warning: The source '{source_to_delete}' is used in the following project(s):\n\n"
                   f"{related_projects}\n\nDeleting it may affect your data entries. Do you want to proceed?")
        confirm = messagebox.askyesno("Confirm Deletion", message)
        if not confirm:
            return
    else:
        confirm = messagebox.askyesno("Confirm Deletion",
                                      f"Are you sure you want to delete source: {source_to_delete}?")
        if not confirm:
            return

    del sources_dict[source_to_delete]
    save_sources(sources_dict)
    update_checkboxes()
    delete_source_dropdown['values'] = sorted(list(sources_dict.keys()))
    # Remove data entries that use the deleted source
    data_entries[:] = [entry for entry in data_entries if entry[0] != source_to_delete]
    save_data_entries(data_entries)
    refresh_table()
    messagebox.showinfo("Success", f"Deleted source: {source_to_delete}.")


delete_button = tk.Button(delete_source_frame, text="Delete Source", command=delete_source)
delete_button.grid(row=1, column=0, columnspan=2, pady=10)

# ----------------------------
# Section: Display Data Entries
# (Scrollable Treeview for CSV contents)
# ----------------------------
output_frame = tk.LabelFrame(scrollable_frame, text="Data Entries", padx=10, pady=10)
output_frame.pack(padx=10, pady=10, fill="both", expand=True)

columns = ("Source", "Target", "Type", "Subject")
tree = ttk.Treeview(output_frame, columns=columns, show="headings", selectmode="extended")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor="w")

scroll_y = ttk.Scrollbar(output_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scroll_y.set)
scroll_y.pack(side="right", fill="y")
tree.pack(side="left", fill="both", expand=True)


def on_tree_mousewheel(event):
    """Scroll the Treeview vertically when the mouse wheel is used."""
    tree.yview_scroll(int(-1*(event.delta/120)), "units")
    return "break"  # Prevent the event from propagating further


# Bind the mouse wheel event to the Treeview
tree.bind("<MouseWheel>", on_tree_mousewheel)

# Optionally, set the Treeview focus on mouse enter, so you don't have to click first
def focus_tree(event):
    tree.focus_set()


tree.bind("<Enter>", focus_tree)


def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    if os.path.exists(data_entries_file):
        with open(data_entries_file, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for r in reader:
                tree.insert("", tk.END, values=(r["Source"], r["Target"], r["Type"], r["Subject"]))


refresh_table()


# ----------------------------
# Section: Delete Selected Data Entry
# ----------------------------
def delete_selected_entries():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showerror("Error", "Please select at least one data entry to delete.")
        return

    for item in selected_items:
        values = tree.item(item)["values"]
        # Convert the list of values to a tuple for comparison
        entry_tuple = tuple(values)
        # Remove all occurrences matching the selected tuple
        data_entries[:] = [entry for entry in data_entries if entry != entry_tuple]

    save_data_entries(data_entries)
    refresh_table()
    messagebox.showinfo("Success", "Selected data entries have been deleted.")


delete_button = tk.Button(scrollable_frame, text="Delete Selected Entry", command=delete_selected_entries)
delete_button.pack(padx=10, pady=10)

# ----------------------------
# Section: Save table
# ----------------------------


# Button to refresh (save) the table data from the CSV file
save_table_button = tk.Button(scrollable_frame, text="Save Table", command=refresh_table)
save_table_button.pack(padx=10, pady=10)

# ----------------------------
# Section: Display node/network graph
# ----------------------------


def display_graph():
    try:
        # Use sys.executable to ensure you run the same Python interpreter
        subprocess.Popen([sys.executable, "graph.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch graph script: {e}")


# Create a button that calls display_graph when pressed
display_graph_button = tk.Button(scrollable_frame, text="Display Graph", command=display_graph)
display_graph_button.pack(padx=10, pady=10)

scrollable_frame.mainloop()
