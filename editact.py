""" Simple form for editing a list of activities """
import tkinter as tk
from tkinter import ttk, messagebox

class ActivityEditorApp:
    def __init__(self, root, acts):
        self.root = root
        self.root.title("Activity editor")

        # Lista interna de objetos Activity
        self.activities = acts

        # --- Sección: tabla ---
        self.tree = ttk.Treeview(root, columns=("name", "cost", "years"), show="headings", height=8)
        self.tree.heading("name", text="Name")
        self.tree.heading("cost", text="Energy loss")
        self.tree.heading("years", text="Years loss")

        self.tree.column("name", width=150)
        self.tree.column("cost", width=80, anchor="e")
        self.tree.column("years", width=80, anchor="e")

        self.tree.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # --- Sección: entradas ---
        tk.Label(root, text="Nombre:").grid(row=1, column=0, sticky="e", padx=5)
        self.name_var = tk.StringVar()
        tk.Entry(root, textvariable=self.name_var).grid(row=1, column=1, sticky="we", padx=5)

        tk.Label(root, text="Energy loss:").grid(row=2, column=0, sticky="e", padx=5)
        self.cost_var = tk.StringVar()
        tk.Entry(root, textvariable=self.cost_var).grid(row=2, column=1, sticky="we", padx=5)

        tk.Label(root, text="Year loss:").grid(row=3, column=0, sticky="e", padx=5)
        self.years_var = tk.StringVar()
        tk.Entry(root, textvariable=self.years_var).grid(row=3, column=1, sticky="we", padx=5)

        # --- Sección: botones ---
        tk.Button(root, text="Add", command=self.add_activity).grid(row=4, column=0, pady=5)
        tk.Button(root, text="Patch", command=self.edit_selected).grid(row=4, column=1, pady=5)
        tk.Button(root, text="Delete", command=self.delete_selected).grid(row=4, column=2, pady=5)

        root.columnconfigure(1, weight=1)

        self.refresh_table()
    
    def on_select(self, event):
        """Triggered whenever the user selects a row."""
        selected = self.tree.selection()
        if not selected:
            return
        index = int(selected[0])
        act = self.activities[index]

        self.name_var.set(act[0])
        self.cost_var.set(act[1])
        self.years_var.set(act[2])

        print(event, self.tree.selection())

    def refresh_table(self):
        """Updates the table."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, act in enumerate(self.activities):
            self.tree.insert("", "end", iid=i, values=(act[0], f"{act[1]:.2f}", f"{act[2]:.2f}"))

    def add_activity(self):
        """ Adds an activity from the input fields """
        name = self.name_var.get().strip()
        try:
            cost = float(self.cost_var.get())
            years = float(self.years_var.get())
        except ValueError:
            messagebox.showerror("Error", "The energy & years losses should be numbers.")
            return

        if not name:
            messagebox.showerror("Error", "The name shouln't be empty.")
            return

        self.activities.append((name, cost, years))
        self.refresh_table()
        self.name_var.set("")
        self.cost_var.set("")
        self.years_var.set("")

    def edit_selected(self):
        """ Patches an activity from the selection and input fields """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advise", "Select an activity to patch.")
            return

        index = int(selected[0])
        name = self.name_var.get().strip()
        try:
            cost = float(self.cost_var.get())
            years = float(self.years_var.get())
        except ValueError:
            messagebox.showerror("Error", "The energy & years losses should be numbers.")
            return

        if not name:
            messagebox.showerror("Error", "The name shouln't be empty.")
            return

        self.activities[index] = (name, cost, years)
        self.name_var.set("")
        self.cost_var.set("")
        self.years_var.set("")
        self.refresh_table()

    def delete_selected(self):
        """ Deletes a selected activity """
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advise", "Select an activity to patch.")
            return

        index = int(selected[0])
        del self.activities[index]
        self.refresh_table()