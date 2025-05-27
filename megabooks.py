import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

class InvoiceSystem:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Invoice & Quote Generator")
        self.window.geometry("900x700")
        self.window.pack_propagate(False)  # Allow window to resize based on contents
        
        # Modern UI updates
        self.window.configure(bg="#f0f0f0")  # Set a light background color

        # Initialize settings_frame
        self.settings_frame = tk.Frame(self.window)
        self.settings_frame.configure(bg="#ffffff")  # Set a white background for settings frame
        self.settings_frame.pack(fill='both', expand=True)  # Pack the frame into the window

        # Update font styles
        style = ttk.Style()
        style.configure("TLabel", font=('Helvetica', 12), background="#ffffff")
        style.configure("TButton", font=('Helvetica', 12), padding=6)
        
        # Business details
        self.business_details = {
            'name': '',
            'address': '',
            'phone': '',
            'email': '',
            'abn': '',
            'bank': '',
            'bsb': '',
            'account': '',
            'logo': '',
            'invoice_terms': '',
            'currency_symbol': ''
        }

        # Initialize business_entries dictionary
        self.business_entries = {}

        # Client/Prospect management
        self.clients = []
        self.prospects = []
        self.load_clients_prospects()

        # Item management
        self.items = []  # Store all items
        self.item_counter = 0  # Counter for generating unique IDs
        self.load_items()  # Load existing items and counter

        self.load_business_details()  # Load business details on initialization
        
        # Data storage
        self.invoices = []
        self.quotes = []
        self.load_data()
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Initialize settings_frame
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text='Business Details')
        
        # Add new blank settings tab
        self.blank_settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.blank_settings_frame, text='Settings')
        
        self.create_settings_tab()  # Create settings tab after initializing business_entries
        self.create_clients_tab()  # New tab for client management
        self.create_items_tab()  # New tab for item management
        self.create_invoice_tab()
        self.create_quote_tab()
        self.create_history_tab()

        # Update all lists after UI is created
        self.update_clients_list()
        self.update_prospects_list()
        self.update_items_list()
        self.update_client_dropdown()
        self.update_quote_client_dropdown()
        self.update_item_selection()
        self.update_item_selection_quote()
    
    def create_settings_tab(self):
        # Ensure default values for new keys
        default_keys = ['name', 'address', 'phone', 'email', 'abn', 'bank', 'bsb', 'account', 'logo', 'invoice_terms', 'currency_symbol']
        for key in default_keys:
            if key not in self.business_details:
                self.business_details[key] = ""  # Set to an empty string if key is missing

        # Create a label for Business Details
        ttk.Label(self.settings_frame, text="Business Details", font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)  # Use grid for better layout
        
        fields = [
            ('Business Name:', 'name'),
            ('Address:', 'address'),
            ('Phone:', 'phone'),
            ('Email:', 'email'),
            ('ABN:', 'abn'),
            ('Bank:', 'bank'),
            ('BSB:', 'bsb'),
            ('Account:', 'account'),
            ('Company Logo Path:', 'logo'),
            ('Invoice Terms:', 'invoice_terms'),
            ('Currency Symbol:', 'currency_symbol')
        ]
        
        for row, (label, key) in enumerate(fields, start=1):
            frame = ttk.Frame(self.settings_frame)  # Create a frame for each label-entry pair
            frame.grid(row=row, pady=5, padx=5, sticky='ew')  # Use grid for alignment
            
            ttk.Label(frame, text=label).pack(side='left', padx=5)  # Pack label to the left
            entry = ttk.Entry(frame, width=40)
            entry.pack(side='left', padx=5)  # Pack entry to the left
            entry.insert(0, self.business_details[key])
            self.business_entries[key] = entry
            
            # Add tooltips for better user guidance
            entry.bind("<Enter>", lambda e, text=label: self.show_tooltip(e, text))
            entry.bind("<Leave>", self.hide_tooltip)

        ttk.Button(self.settings_frame, text="Save Business Details", 
                   command=self.save_business_details).grid(row=len(fields)+1, column=0, pady=20)  # Use grid instead of pack
        
        ttk.Button(self.settings_frame, text="Reset Business Details", 
                   command=self.reset_business_details).grid(row=len(fields)+1, column=1, pady=20)  # Reset button
        
        # Add a new feature: Theme selection
        ttk.Label(self.settings_frame, text="Select Theme:").grid(row=len(fields)+2, column=0, pady=5)
        self.theme_var = tk.StringVar(value="Light")
        ttk.Combobox(self.settings_frame, textvariable=self.theme_var, values=["Light", "Dark"]).grid(row=len(fields)+2, column=1, pady=5)
        
        # Add a new feature: Font size selection
        ttk.Label(self.settings_frame, text="Font Size:").grid(row=len(fields)+3, column=0, pady=5)
        self.font_size_var = tk.StringVar(value="12")
        ttk.Combobox(self.settings_frame, textvariable=self.font_size_var, values=["10", "12", "14", "16"]).grid(row=len(fields)+3, column=1, pady=5)
    
    def show_tooltip(self, event, text):
        # Function to show tooltip
        self.tooltip = ttk.Label(self.settings_frame, text=text, relief="solid", background="lightyellow")
        self.tooltip.place(x=event.x_root + 10, y=event.y_root + 10)

    def hide_tooltip(self, event):
        # Function to hide tooltip
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()

    def reset_business_details(self):
        # Reset all fields to empty
        for key, entry in self.business_entries.items():
            entry.delete(0, 'end')
            self.business_details[key] = ""
    
    def save_business_details(self):
        # Validate email and phone
        email = self.business_entries['email'].get().strip()
        phone = self.business_entries['phone'].get().strip()
        
        if not self.validate_email(email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return
        
        if not self.validate_phone(phone):
            messagebox.showerror("Error", "Please enter a valid phone number.")
            return
        
        for key, entry in self.business_entries.items():
            self.business_details[key] = entry.get().strip()
        
        with open('business_details.json', 'w') as f:
            json.dump(self.business_details, f)
        
        messagebox.showinfo("Success", "Business details saved successfully!")

    def validate_email(self, email):
        # Simple email validation
        return "@" in email and "." in email

    def validate_phone(self, phone):
        # Simple phone validation (digits only)
        return phone.isdigit() and len(phone) >= 10  # Adjust length as needed
    
    def create_clients_tab(self):
        clients_frame = ttk.Frame(self.notebook)
        self.notebook.add(clients_frame, text='Clients & Prospects')

        # Create notebook for Clients and Prospects
        clients_notebook = ttk.Notebook(clients_frame)
        clients_notebook.pack(expand=True, fill='both', padx=5, pady=5)

        # Clients tab
        clients_tab = ttk.Frame(clients_notebook)
        clients_notebook.add(clients_tab, text='Clients')

        # Clients list
        self.clients_tree = ttk.Treeview(clients_tab, columns=('Name', 'Email', 'Address', 'Phone'), show='headings')
        self.clients_tree.heading('Name', text='Name')
        self.clients_tree.heading('Email', text='Email')
        self.clients_tree.heading('Address', text='Address')
        self.clients_tree.heading('Phone', text='Phone')
        self.clients_tree.pack(pady=5, padx=5, fill='both', expand=True)

        # Prospects tab
        prospects_tab = ttk.Frame(clients_notebook)
        clients_notebook.add(prospects_tab, text='Prospects')

        # Prospects list
        self.prospects_tree = ttk.Treeview(prospects_tab, columns=('Name', 'Email', 'Address', 'Phone'), show='headings')
        self.prospects_tree.heading('Name', text='Name')
        self.prospects_tree.heading('Email', text='Email')
        self.prospects_tree.heading('Address', text='Address')
        self.prospects_tree.heading('Phone', text='Phone')
        self.prospects_tree.pack(pady=5, padx=5, fill='both', expand=True)

        # Add/Edit client/prospect frame
        add_frame = ttk.LabelFrame(clients_frame, text="Add/Edit Client/Prospect")
        add_frame.pack(pady=5, padx=5, fill='x')

        # Entry fields
        ttk.Label(add_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.client_name_entry = ttk.Entry(add_frame, width=30)
        self.client_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Email:").grid(row=0, column=2, padx=5, pady=5)
        self.client_email_entry = ttk.Entry(add_frame, width=30)
        self.client_email_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(add_frame, text="Address:").grid(row=1, column=0, padx=5, pady=5)
        self.client_address_entry = ttk.Entry(add_frame, width=30)
        self.client_address_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Phone:").grid(row=1, column=2, padx=5, pady=5)
        self.client_phone_entry = ttk.Entry(add_frame, width=30)
        self.client_phone_entry.grid(row=1, column=3, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(add_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)

        ttk.Button(button_frame, text="Add as Prospect", command=self.add_prospect).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Add as Client", command=self.add_client).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Convert to Client", command=self.convert_to_client).pack(side='left', padx=5)
        self.edit_button = ttk.Button(button_frame, text="Edit Selected", command=self.edit_selected)
        self.edit_button.pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected).pack(side='left', padx=5)

        # Bind double-click event for editing
        self.clients_tree.bind('<Double-1>', lambda e: self.edit_selected())
        self.prospects_tree.bind('<Double-1>', lambda e: self.edit_selected())

        # Update the lists immediately after creation
        self.update_clients_list()
        self.update_prospects_list()

    def add_client(self):
        name = self.client_name_entry.get().strip()
        email = self.client_email_entry.get().strip()
        address = self.client_address_entry.get().strip()
        phone = self.client_phone_entry.get().strip()

        if not all([name, email, address, phone]):
            messagebox.showerror("Error", "All fields are required!")
            return

        client = {
            'name': name,
            'email': email,
            'address': address,
            'phone': phone
        }

        self.clients.append(client)
        self.update_clients_list()
        self.save_clients_prospects()
        self.clear_client_entries()
        # Update dropdowns immediately
        self.update_client_dropdown()
        self.update_quote_client_dropdown()

    def add_prospect(self):
        name = self.client_name_entry.get().strip()
        email = self.client_email_entry.get().strip()
        address = self.client_address_entry.get().strip()
        phone = self.client_phone_entry.get().strip()

        if not all([name, email, address, phone]):
            messagebox.showerror("Error", "All fields are required!")
            return

        prospect = {
            'name': name,
            'email': email,
            'address': address,
            'phone': phone
        }

        self.prospects.append(prospect)
        self.update_prospects_list()
        self.save_clients_prospects()
        self.clear_client_entries()
        # Update quote dropdown immediately (since it includes prospects)
        self.update_quote_client_dropdown()

    def convert_to_client(self):
        selected = self.prospects_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a prospect to convert!")
            return

        index = self.prospects_tree.index(selected[0])
        prospect = self.prospects.pop(index)
        self.clients.append(prospect)
        
        self.update_prospects_list()
        self.update_clients_list()
        self.save_clients_prospects()
        # Update both dropdowns immediately
        self.update_client_dropdown()
        self.update_quote_client_dropdown()

    def edit_selected(self):
        # Check which tree has selection
        selected = self.clients_tree.selection() or self.prospects_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an item to edit!")
            return

        # Determine which tree was selected
        if self.clients_tree.selection():
            tree = self.clients_tree
            data = self.clients
        else:
            tree = self.prospects_tree
            data = self.prospects

        index = tree.index(selected[0])
        item = data[index]

        # Populate entries
        self.client_name_entry.delete(0, 'end')
        self.client_name_entry.insert(0, item['name'])
        self.client_email_entry.delete(0, 'end')
        self.client_email_entry.insert(0, item['email'])
        self.client_address_entry.delete(0, 'end')
        self.client_address_entry.insert(0, item['address'])
        self.client_phone_entry.delete(0, 'end')
        self.client_phone_entry.insert(0, item['phone'])

        # Change button text to indicate editing mode
        self.edit_button.config(text="Save Changes")
        self.edit_button.config(command=lambda: self.save_edit(item, tree, data, index))

    def save_edit(self, item, tree, data, index):
        name = self.client_name_entry.get().strip()
        email = self.client_email_entry.get().strip()
        address = self.client_address_entry.get().strip()
        phone = self.client_phone_entry.get().strip()

        if not all([name, email, address, phone]):
            messagebox.showerror("Error", "All fields are required!")
            return

        item['name'] = name
        item['email'] = email
        item['address'] = address
        item['phone'] = phone

        self.update_clients_list()
        self.update_prospects_list()
        self.save_clients_prospects()
        self.clear_client_entries()
        # Update both dropdowns immediately
        self.update_client_dropdown()
        self.update_quote_client_dropdown()

        # Reset button to normal state
        self.edit_button.config(text="Edit Selected")
        self.edit_button.config(command=self.edit_selected)

    def delete_selected(self):
        selected = self.clients_tree.selection() or self.prospects_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an item to delete!")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            if self.clients_tree.selection():
                index = self.clients_tree.index(selected[0])
                self.clients.pop(index)
                self.update_clients_list()
                # Update both dropdowns immediately
                self.update_client_dropdown()
                self.update_quote_client_dropdown()
            else:
                index = self.prospects_tree.index(selected[0])
                self.prospects.pop(index)
                self.update_prospects_list()
                # Update quote dropdown immediately
                self.update_quote_client_dropdown()
            
            self.save_clients_prospects()

    def clear_client_entries(self):
        self.client_name_entry.delete(0, 'end')
        self.client_email_entry.delete(0, 'end')
        self.client_address_entry.delete(0, 'end')
        self.client_phone_entry.delete(0, 'end')

    def update_clients_list(self):
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
        
        for client in self.clients:
            self.clients_tree.insert('', 'end', values=(
                client['name'],
                client['email'],
                client['address'],
                client['phone']
            ))

    def update_prospects_list(self):
        for item in self.prospects_tree.get_children():
            self.prospects_tree.delete(item)
        
        for prospect in self.prospects:
            self.prospects_tree.insert('', 'end', values=(
                prospect['name'],
                prospect['email'],
                prospect['address'],
                prospect['phone']
            ))

    def load_clients_prospects(self):
        try:
            with open('clients_prospects.json', 'r') as f:
                data = json.load(f)
                self.clients = data.get('clients', [])
                self.prospects = data.get('prospects', [])
        except FileNotFoundError:
            self.clients = []
            self.prospects = []

    def save_clients_prospects(self):
        with open('clients_prospects.json', 'w') as f:
            json.dump({
                'clients': self.clients,
                'prospects': self.prospects
            }, f, indent=4)

    def create_items_tab(self):
        items_frame = ttk.Frame(self.notebook)
        self.notebook.add(items_frame, text='Items')

        # Items list
        self.items_library_tree = ttk.Treeview(items_frame, 
                                     columns=('ID', 'Name', 'Description', 'Price'),
                                     show='headings')
        self.items_library_tree.heading('ID', text='ID')
        self.items_library_tree.heading('Name', text='Name')
        self.items_library_tree.heading('Description', text='Description')
        self.items_library_tree.heading('Price', text='Price (ex GST)')
        
        self.items_library_tree.column('ID', width=100)
        self.items_library_tree.column('Name', width=150)
        self.items_library_tree.column('Description', width=200)
        self.items_library_tree.column('Price', width=100)
        
        self.items_library_tree.pack(pady=5, padx=5, fill='both', expand=True)

        # Add/Edit item frame
        add_frame = ttk.LabelFrame(items_frame, text="Add/Edit Item")
        add_frame.pack(pady=5, padx=5, fill='x')

        # Entry fields
        ttk.Label(add_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.item_name_entry = ttk.Entry(add_frame, width=30)
        self.item_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Description:").grid(row=0, column=2, padx=5, pady=5)
        self.item_desc_entry = ttk.Entry(add_frame, width=40)
        self.item_desc_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(add_frame, text="Price (ex GST):").grid(row=0, column=4, padx=5, pady=5)
        self.item_price_entry = ttk.Entry(add_frame, width=15)
        self.item_price_entry.grid(row=0, column=5, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(add_frame)
        button_frame.grid(row=1, column=0, columnspan=6, pady=10)

        ttk.Button(button_frame, text="Add Item", command=self.add_item_to_library).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Edit Selected", command=self.edit_library_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_library_item).pack(side='left', padx=5)

        # Bind double-click event for editing
        self.items_library_tree.bind('<Double-1>', lambda e: self.edit_library_item())

        # Update the items list
        self.update_items_list()

    def add_item_to_library(self):
        name = self.item_name_entry.get().strip()
        desc = self.item_desc_entry.get().strip()
        try:
            price = float(self.item_price_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price!")
            return

        if not name or not desc:
            messagebox.showerror("Error", "Name and Description are required!")
            return

        item_id = self.generate_item_id()
        item = {
            'id': item_id,
            'name': name,
            'description': desc,
            'price': price
        }

        self.items.append(item)
        self.save_items()
        self.update_items_list()
        self.clear_item_entries()

    def edit_library_item(self):
        selected = self.items_library_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an item to edit!")
            return

        index = self.items_library_tree.index(selected[0])
        item = self.items[index]

        # Create edit window
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Item")
        edit_window.geometry("400x200")

        ttk.Label(edit_window, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(edit_window, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        name_entry.insert(0, item['name'])

        ttk.Label(edit_window, text="Description:").grid(row=1, column=0, padx=5, pady=5)
        desc_entry = ttk.Entry(edit_window, width=30)
        desc_entry.grid(row=1, column=1, padx=5, pady=5)
        desc_entry.insert(0, item['description'])

        ttk.Label(edit_window, text="Price (ex GST):").grid(row=2, column=0, padx=5, pady=5)
        price_entry = ttk.Entry(edit_window, width=15)
        price_entry.grid(row=2, column=1, padx=5, pady=5)
        price_entry.insert(0, str(item['price']))

        def save_changes():
            name = name_entry.get().strip()
            desc = desc_entry.get().strip()
            try:
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid price!")
                return

            if not name or not desc:
                messagebox.showerror("Error", "Name and Description are required!")
                return

            item['name'] = name
            item['description'] = desc
            item['price'] = price

            self.save_items()
            self.update_items_list()
            edit_window.destroy()

        ttk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=3, column=0, columnspan=2, pady=20)

    def delete_library_item(self):
        selected = self.items_library_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an item to delete!")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            index = self.items_library_tree.index(selected[0])
            self.items.pop(index)
            self.save_items()
            self.update_items_list()

    def clear_item_entries(self):
        self.item_name_entry.delete(0, 'end')
        self.item_desc_entry.delete(0, 'end')
        self.item_price_entry.delete(0, 'end')

    def update_items_list(self):
        for item in self.items_library_tree.get_children():
            self.items_library_tree.delete(item)
        
        for item in self.items:
            self.items_library_tree.insert('', 'end', values=(
                item['id'],
                item['name'],
                item['description'],
                f"${item['price']:.2f}"
            ))

    def load_items(self):
        try:
            with open('items.json', 'r') as f:
                data = json.load(f)
                self.items = data.get('items', [])
                self.item_counter = data.get('counter', 0)
        except FileNotFoundError:
            self.items = []
            self.item_counter = 0

    def save_items(self):
        with open('items.json', 'w') as f:
            json.dump({
                'items': self.items,
                'counter': self.item_counter
            }, f, indent=4)

    def generate_item_id(self):
        self.item_counter += 1
        return f"ITEM{self.item_counter:04d}"

    def create_invoice_tab(self):
        invoice_frame = ttk.Frame(self.notebook)
        self.notebook.add(invoice_frame, text='New Invoice')
        
        # Client Information
        client_frame = ttk.LabelFrame(invoice_frame, text="Client Information")
        client_frame.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky='nsew')
        
        # Client selection dropdown
        ttk.Label(client_frame, text="Select Client:").grid(row=0, column=0, padx=5, pady=5)
        self.client_var = tk.StringVar()
        self.client_dropdown = ttk.Combobox(client_frame, textvariable=self.client_var, width=37)
        self.client_dropdown.grid(row=0, column=1, pady=5)
        self.client_dropdown.bind('<<ComboboxSelected>>', self.on_client_selected)
        
        # Update client dropdown
        self.update_client_dropdown()
        
        ttk.Label(client_frame, text="Client Name:").grid(row=1, column=0, padx=5, pady=5)
        self.client_name = ttk.Entry(client_frame, width=40)
        self.client_name.grid(row=1, column=1, pady=5)
        
        ttk.Label(client_frame, text="Client Email:").grid(row=2, column=0, padx=5, pady=5)
        self.client_email = ttk.Entry(client_frame, width=40)
        self.client_email.grid(row=2, column=1, pady=5)
        
        ttk.Label(client_frame, text="Client Address:").grid(row=3, column=0, padx=5, pady=5)
        self.client_address = ttk.Entry(client_frame, width=40)
        self.client_address.grid(row=3, column=1, pady=5)
        
        # GST Option
        self.gst_var = tk.BooleanVar(value=True)
        self.gst_check = ttk.Checkbutton(client_frame, text="Include GST (10%)", variable=self.gst_var, 
                                        command=self.update_total)
        self.gst_check.grid(row=4, column=1, pady=5)
        
        # Items Frame
        items_frame = ttk.LabelFrame(invoice_frame, text="Items")
        items_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky='nsew')
        
        # Items Table
        self.items_tree = ttk.Treeview(items_frame, 
                                      columns=('Item ID', 'Name', 'Description', 'Quantity', 'Price', 'GST', 'Total'),
                                      show='headings')
        self.items_tree.heading('Item ID', text='Item ID')
        self.items_tree.heading('Name', text='Name')
        self.items_tree.heading('Description', text='Description')
        self.items_tree.heading('Quantity', text='Quantity')
        self.items_tree.heading('Price', text='Price (ex GST)')
        self.items_tree.heading('GST', text='GST')
        self.items_tree.heading('Total', text='Total')
        
        self.items_tree.column('Item ID', width=100)
        self.items_tree.column('Name', width=150)
        self.items_tree.column('Description', width=200)
        self.items_tree.column('Quantity', width=100)
        self.items_tree.column('Price', width=100)
        self.items_tree.column('GST', width=100)
        self.items_tree.column('Total', width=100)
        
        self.items_tree.pack(pady=5)
        
        # Bind double-click event for editing items
        self.items_tree.bind('<Double-1>', self.edit_invoice_item)
        
        # Add Item Frame
        add_item_frame = ttk.Frame(items_frame)
        add_item_frame.pack(pady=5)
        
        # Labels and entries for new items
        ttk.Label(add_item_frame, text="Select Item:").grid(row=0, column=0, padx=5)
        self.item_selection = ttk.Combobox(add_item_frame, width=30)
        self.item_selection.grid(row=0, column=1, padx=5)
        self.update_item_selection()
        
        ttk.Label(add_item_frame, text="Quantity:").grid(row=0, column=2, padx=5)
        self.item_quantity = ttk.Entry(add_item_frame, width=10)
        self.item_quantity.grid(row=0, column=3, padx=5)
        
        ttk.Button(add_item_frame, text="Add Item", command=self.add_item).grid(row=0, column=4, padx=5)
        ttk.Button(add_item_frame, text="New Item", command=self.create_new_item).grid(row=0, column=5, padx=5)
        ttk.Button(add_item_frame, text="Edit Selected", command=self.edit_invoice_item).grid(row=0, column=6, padx=5)
        ttk.Button(add_item_frame, text="Remove Selected", 
                   command=self.remove_selected_item).grid(row=0, column=7, padx=5)
        
        # Totals Frame
        totals_frame = ttk.Frame(invoice_frame)
        totals_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky='e')
        
        self.subtotal_label = ttk.Label(totals_frame, text="Subtotal: $0.00")
        self.subtotal_label.pack(pady=2)
        
        self.gst_label = ttk.Label(totals_frame, text="GST: $0.00")
        self.gst_label.pack(pady=2)
        
        self.total_label = ttk.Label(totals_frame, text="Total: $0.00", font=('Arial', 12, 'bold'))
        self.total_label.pack(pady=2)
        
        # Generate Button
        ttk.Button(invoice_frame, text="Generate Invoice", 
                   command=lambda: self.save_document('invoice')).grid(row=3, column=1, pady=10)
    
    def create_quote_tab(self):
        quote_frame = ttk.Frame(self.notebook)
        self.notebook.add(quote_frame, text='New Quote')
        
        # Client Information
        client_frame = ttk.LabelFrame(quote_frame, text="Client Information")
        client_frame.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky='nsew')
        
        # Client selection dropdown
        ttk.Label(client_frame, text="Select Client/Prospect:").grid(row=0, column=0, padx=5, pady=5)
        self.quote_client_var = tk.StringVar()
        self.quote_client_dropdown = ttk.Combobox(client_frame, textvariable=self.quote_client_var, width=37)
        self.quote_client_dropdown.grid(row=0, column=1, pady=5)
        self.quote_client_dropdown.bind('<<ComboboxSelected>>', self.on_quote_client_selected)
        
        # Update client dropdown
        self.update_quote_client_dropdown()
        
        ttk.Label(client_frame, text="Client Name:").grid(row=1, column=0, padx=5, pady=5)
        self.quote_client_name = ttk.Entry(client_frame, width=40)
        self.quote_client_name.grid(row=1, column=1, pady=5)
        
        ttk.Label(client_frame, text="Client Email:").grid(row=2, column=0, padx=5, pady=5)
        self.quote_client_email = ttk.Entry(client_frame, width=40)
        self.quote_client_email.grid(row=2, column=1, pady=5)
        
        ttk.Label(client_frame, text="Client Address:").grid(row=3, column=0, padx=5, pady=5)
        self.quote_client_address = ttk.Entry(client_frame, width=40)
        self.quote_client_address.grid(row=3, column=1, pady=5)
        
        # Items Frame
        items_frame = ttk.LabelFrame(quote_frame, text="Items")
        items_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky='nsew')
        
        # Items Table
        self.quote_items_tree = ttk.Treeview(items_frame, 
                                           columns=('Item ID', 'Name', 'Description', 'Quantity', 'Price', 'GST', 'Total'),
                                           show='headings')
        self.quote_items_tree.heading('Item ID', text='Item ID')
        self.quote_items_tree.heading('Name', text='Name')
        self.quote_items_tree.heading('Description', text='Description')
        self.quote_items_tree.heading('Quantity', text='Quantity')
        self.quote_items_tree.heading('Price', text='Price (ex GST)')
        self.quote_items_tree.heading('GST', text='GST')
        self.quote_items_tree.heading('Total', text='Total')
        
        self.quote_items_tree.column('Item ID', width=100)
        self.quote_items_tree.column('Name', width=150)
        self.quote_items_tree.column('Description', width=200)
        self.quote_items_tree.column('Quantity', width=100)
        self.quote_items_tree.column('Price', width=100)
        self.quote_items_tree.column('GST', width=100)
        self.quote_items_tree.column('Total', width=100)
        
        self.quote_items_tree.pack(pady=5)
        
        # Bind double-click event for editing items
        self.quote_items_tree.bind('<Double-1>', self.edit_quote_item)
        
        # Add Item Frame
        add_item_frame = ttk.Frame(items_frame)
        add_item_frame.pack(pady=5)
        
        # Labels and entries for new items
        ttk.Label(add_item_frame, text="Select Item:").grid(row=0, column=0, padx=5)
        self.item_selection_quote = ttk.Combobox(add_item_frame, width=30)
        self.item_selection_quote.grid(row=0, column=1, padx=5)
        self.update_item_selection_quote()
        
        ttk.Label(add_item_frame, text="Quantity:").grid(row=0, column=2, padx=5)
        self.item_quantity_quote = ttk.Entry(add_item_frame, width=10)
        self.item_quantity_quote.grid(row=0, column=3, padx=5)
        
        ttk.Button(add_item_frame, text="Add Item", command=self.add_item_quote).grid(row=0, column=4, padx=5)
        ttk.Button(add_item_frame, text="New Item", command=self.create_new_item).grid(row=0, column=5, padx=5)
        ttk.Button(add_item_frame, text="Edit Selected", command=self.edit_quote_item).grid(row=0, column=6, padx=5)
        ttk.Button(add_item_frame, text="Remove Selected", 
                   command=self.remove_selected_item_quote).grid(row=0, column=7, padx=5)
        
        # Totals Frame for Quote
        totals_frame_quote = ttk.Frame(quote_frame)
        totals_frame_quote.grid(row=2, column=0, columnspan=2, pady=10, sticky='e')
        
        # Initialize the subtotal, GST, and total labels for quotes
        self.subtotal_label_quote = ttk.Label(totals_frame_quote, text="Subtotal: $0.00")
        self.subtotal_label_quote.pack(pady=2)
        
        self.gst_label_quote = ttk.Label(totals_frame_quote, text="GST: $0.00")
        self.gst_label_quote.pack(pady=2)
        
        self.total_label_quote = ttk.Label(totals_frame_quote, text="Total: $0.00", font=('Arial', 12, 'bold'))
        self.total_label_quote.pack(pady=2)
        
        # Generate Button
        ttk.Button(quote_frame, text="Generate Quote", 
                   command=lambda: self.save_document('quote')).grid(row=3, column=1, pady=10)
    
    def create_history_tab(self):
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text='History')
        
        self.history_tree = ttk.Treeview(history_frame, 
                                        columns=('Date', 'Type', 'Client', 'Total', 'PDF'),
                                        show='headings')
        self.history_tree.heading('Date', text='Date')
        self.history_tree.heading('Type', text='Type')
        self.history_tree.heading('Client', text='Client')
        self.history_tree.heading('Total', text='Total')
        self.history_tree.heading('PDF', text='PDF Location')
        
        self.history_tree.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Add Open PDF button
        ttk.Button(history_frame, text="Open Selected PDF", 
                   command=self.open_selected_pdf).pack(pady=5)
        
        self.update_history()
    
    def add_item(self):
        try:
            selected = self.item_selection.get()
            if not selected:
                messagebox.showerror("Error", "Please select an item!")
                return

            item_id = selected.split(' - ')[0]
            item = next((i for i in self.items if i['id'] == item_id), None)
            if not item:
                messagebox.showerror("Error", "Selected item not found!")
                return

            qty = float(self.item_quantity.get())
            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0!")
                return

            price = item['price']
            if self.gst_var.get():
                gst = price * qty * 0.1
                total = (price * qty) + gst
            else:
                gst = 0
                total = price * qty
            
            self.items_tree.insert('', 'end', values=(
                item['id'],
                item['name'],
                item['description'],
                qty, 
                f"${price:.2f}", 
                f"${gst:.2f}",
                f"${total:.2f}"
            ))
            self.update_total()
            
            # Clear entries
            self.item_quantity.delete(0, 'end')
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity.")
    
    def remove_selected_item(self):
        selected_item = self.items_tree.selection()
        if selected_item:
            self.items_tree.delete(selected_item)
            self.update_total()
    
    def update_total(self):
        subtotal = 0
        gst_total = 0
        for item in self.items_tree.get_children():
            values = self.items_tree.item(item, 'values')
            subtotal += float(values[4].replace('$', '')) * float(values[3])
            gst_total += float(values[5].replace('$', ''))
        
        total = subtotal + gst_total
        self.subtotal_label.config(text=f"Subtotal: ${subtotal:.2f}")
        self.gst_label.config(text=f"GST: ${gst_total:.2f}")
        self.total_label.config(text=f"Total: ${total:.2f}")
    
    def generate_pdf(self, data, doc_type):
        pdf_file = f"{doc_type.capitalize()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        doc = SimpleDocTemplate(pdf_file, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph(f"{doc_type.capitalize()}", title_style))
        
        # Business Details
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"{self.business_details['name']}", styles['Normal']))
        story.append(Paragraph(f"{self.business_details['address']}", styles['Normal']))
        story.append(Paragraph(f"Phone: {self.business_details['phone']}", styles['Normal']))
        story.append(Paragraph(f"Email: {self.business_details['email']}", styles['Normal']))
        if self.business_details['abn']:
            story.append(Paragraph(f"ABN: {self.business_details['abn']}", styles['Normal']))
        
        # Banking Details (only if available)
        if doc_type == 'invoice':
            story.append(Spacer(1, 12))
            story.append(Paragraph("Banking Details:", styles['Heading3']))
            if self.business_details['bank']:
                story.append(Paragraph(f"Bank: {self.business_details['bank']}", styles['Normal']))
            if self.business_details['bsb']:
                story.append(Paragraph(f"BSB: {self.business_details['bsb']}", styles['Normal']))
            if self.business_details['account']:
                story.append(Paragraph(f"Account: {self.business_details['account']}", styles['Normal']))
        
        # Client Information
        story.append(Spacer(1, 12))
        story.append(Paragraph("Client Information:", styles['Heading3']))
        story.append(Paragraph(f"Client Name: {data['client_name']}", styles['Normal']))
        story.append(Paragraph(f"Client Email: {data['client_email']}", styles['Normal']))
        story.append(Paragraph(f"Client Address: {data['client_address']}", styles['Normal']))
        
        # Items Table
        story.append(Spacer(1, 12))
        story.append(Paragraph("Items:", styles['Heading3']))
        
        # Define column widths (in points) - removed Item ID column
        col_widths = [120, 180, 50, 60, 60, 60]  # Total: 530 points (A4 width is 595 points)
        
        # Create custom styles for table cells
        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        )
        
        table_cell_style = ParagraphStyle(
            'TableCell',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,  # Line spacing
            alignment=0,  # Left alignment
            fontName='Helvetica'
        )
        
        table_cell_style_right = ParagraphStyle(
            'TableCellRight',
            parent=table_cell_style,
            alignment=2  # Right alignment
        )
        
        table_cell_style_center = ParagraphStyle(
            'TableCellCenter',
            parent=table_cell_style,
            alignment=1  # Center alignment
        )
        
        # Create table data with Paragraph objects for text wrapping - removed Item ID column
        item_data = [[
            Paragraph("Name", table_header_style),
            Paragraph("Description", table_header_style),
            Paragraph("Qty", table_header_style),
            Paragraph("Price", table_header_style),
            Paragraph("GST", table_header_style),
            Paragraph("Total", table_header_style)
        ]]
        
        for item in data['items']:
            # Create Paragraph objects for each cell - skip Item ID
            formatted_item = [
                Paragraph(str(item[1]), table_cell_style),         # Name
                Paragraph(str(item[2]), table_cell_style),         # Description
                Paragraph(str(item[3]), table_cell_style_right),   # Quantity
                Paragraph(str(item[4]), table_cell_style_right),   # Price
                Paragraph(str(item[5]), table_cell_style_right),   # GST
                Paragraph(str(item[6]), table_cell_style_right)    # Total
            ]
            item_data.append(formatted_item)
        
        # Create the table
        table = Table(item_data, colWidths=col_widths, repeatRows=1)
        
        # Define table styles
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            
            # Grid lines
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            
            # Row height
            ('MINIMUMHEIGHT', (0, 0), (-1, -1), 30),
        ])
        
        table.setStyle(table_style)
        story.append(table)
        
        # Totals
        story.append(Spacer(1, 20))
        totals_style = ParagraphStyle(
            'Totals',
            parent=styles['Normal'],
            fontSize=12,
            alignment=2  # Right alignment
        )
        story.append(Paragraph(f"Subtotal: ${data['subtotal']}", totals_style))
        story.append(Paragraph(f"GST: ${data['gst']}", totals_style))
        story.append(Paragraph(f"Total: ${data['total']}", totals_style))
        
        # Add terms if available
        if self.business_details['invoice_terms']:
            story.append(Spacer(1, 20))
            story.append(Paragraph("Terms:", styles['Heading3']))
            story.append(Paragraph(self.business_details['invoice_terms'], styles['Normal']))
        
        doc.build(story)
        return pdf_file
    
    def save_document(self, doc_type):
        items = []
        # Get items from appropriate tree
        tree = self.quote_items_tree if doc_type == 'quote' else self.items_tree
        for item in tree.get_children():
            values = tree.item(item, 'values')
            items.append([values[0], values[1], values[2], values[3], values[4], values[5], values[6]])
        
        # Calculate totals directly from items
        subtotal = 0
        gst_total = 0
        for item in items:
            # Extract numeric values from formatted strings
            price = float(item[4].replace('$', ''))  # Price
            qty = float(item[3])  # Quantity
            gst = float(item[5].replace('$', ''))  # GST
            
            subtotal += price * qty
            gst_total += gst
        
        total = subtotal + gst_total
        
        data = {
            'client_name': self.quote_client_name.get(),
            'client_email': self.quote_client_email.get(),
            'client_address': self.quote_client_address.get(),
            'items': items,
            'subtotal': f"{subtotal:.2f}",
            'gst': f"{gst_total:.2f}",
            'total': f"{total:.2f}"
        }
        
        pdf_file = self.generate_pdf(data, doc_type)
        messagebox.showinfo("PDF Generated", f"{doc_type.capitalize()} PDF generated and saved as {pdf_file}.")
        self.update_history()
    
    def update_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Load history data (example static entries)
        history_data = [
            ('2024-11-01', 'Invoice', 'Client A', '$500', 'Invoice_20241101.pdf')
        ]
        
        for entry in history_data:
            self.history_tree.insert('', 'end', values=entry)
    
    def open_selected_pdf(self):
        selected = self.history_tree.selection()
        if selected:
            pdf_file = self.history_tree.item(selected, 'values')[-1]
            os.system(f'open {pdf_file}') # macOS; use 'start' for Windows or 'xdg-open' for Linux
    
    def load_data(self):
        if os.path.exists('data.json'):
            with open('data.json', 'r') as f:
                data = json.load(f)
                self.invoices = data.get('invoices', [])
                self.quotes = data.get('quotes', [])
        else:
            self.invoices = []  # Initialize to empty if file doesn't exist
            self.quotes = []    # Initialize to empty if file doesn't exist
    
    def add_item_quote(self):
        try:
            selected = self.item_selection_quote.get()
            if not selected:
                messagebox.showerror("Error", "Please select an item!")
                return

            item_id = selected.split(' - ')[0]
            item = next((i for i in self.items if i['id'] == item_id), None)
            if not item:
                messagebox.showerror("Error", "Selected item not found!")
                return

            qty = float(self.item_quantity_quote.get())
            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0!")
                return

            price = item['price']
            if self.gst_var.get():
                gst = price * qty * 0.1
                total = (price * qty) + gst
            else:
                gst = 0
                total = price * qty
            
            self.quote_items_tree.insert('', 'end', values=(
                item['id'],
                item['name'],
                item['description'],
                qty, 
                f"${price:.2f}", 
                f"${gst:.2f}",
                f"${total:.2f}"
            ))
            self.update_total_quote()
            
            # Clear entries
            self.item_quantity_quote.delete(0, 'end')
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity.")
    
    def remove_selected_item_quote(self):
        selected_item = self.quote_items_tree.selection()
        if selected_item:
            self.quote_items_tree.delete(selected_item)
            self.update_total_quote()
    
    def update_total_quote(self):
        subtotal = 0
        gst_total = 0
        for item in self.quote_items_tree.get_children():
            values = self.quote_items_tree.item(item, 'values')
            subtotal += float(values[4].replace('$', '')) * float(values[3])
            gst_total += float(values[5].replace('$', ''))
        
        total = subtotal + gst_total
        self.subtotal_label_quote.config(text=f"Subtotal: ${subtotal:.2f}")
        self.gst_label_quote.config(text=f"GST: ${gst_total:.2f}")
        self.total_label_quote.config(text=f"Total: ${total:.2f}")
    
    def load_business_details(self):
        # Load business details from a JSON file
        if os.path.exists('business_details.json'):
            with open('business_details.json', 'r') as f:
                self.business_details = json.load(f)
                # Update the entry fields with loaded data
                for key, entry in self.business_entries.items():
                    entry.delete(0, 'end')  # Clear existing entry
                    entry.insert(0, self.business_details.get(key, ''))  # Insert loaded value
        else:
            self.business_details = {  # Initialize with empty values if file doesn't exist
                'name': '',
                'address': '',
                'phone': '',
                'email': '',
                'abn': '',
                'bank': '',
                'bsb': '',
                'account': '',
                'logo': '',
                'invoice_terms': '',
                'currency_symbol': ''
            }
    
    def update_client_dropdown(self):
        client_names = [client['name'] for client in self.clients]
        self.client_dropdown['values'] = client_names
        # Clear the current selection
        self.client_var.set('')

    def update_quote_client_dropdown(self):
        # Combine clients and prospects for quotes
        all_names = [client['name'] for client in self.clients]
        all_names.extend([prospect['name'] for prospect in self.prospects])
        self.quote_client_dropdown['values'] = all_names
        # Clear the current selection
        self.quote_client_var.set('')

    def on_client_selected(self, event):
        selected_name = self.client_var.get()
        for client in self.clients:
            if client['name'] == selected_name:
                self.client_name.delete(0, 'end')
                self.client_name.insert(0, client['name'])
                self.client_email.delete(0, 'end')
                self.client_email.insert(0, client['email'])
                self.client_address.delete(0, 'end')
                self.client_address.insert(0, client['address'])
                break

    def on_quote_client_selected(self, event):
        selected_name = self.quote_client_var.get()
        # Check clients first
        for client in self.clients:
            if client['name'] == selected_name:
                self.quote_client_name.delete(0, 'end')
                self.quote_client_name.insert(0, client['name'])
                self.quote_client_email.delete(0, 'end')
                self.quote_client_email.insert(0, client['email'])
                self.quote_client_address.delete(0, 'end')
                self.quote_client_address.insert(0, client['address'])
                return
        # Then check prospects
        for prospect in self.prospects:
            if prospect['name'] == selected_name:
                self.quote_client_name.delete(0, 'end')
                self.quote_client_name.insert(0, prospect['name'])
                self.quote_client_email.delete(0, 'end')
                self.quote_client_email.insert(0, prospect['email'])
                self.quote_client_address.delete(0, 'end')
                self.quote_client_address.insert(0, prospect['address'])
                return

    def edit_invoice_item(self, event=None):
        # Get the selected item
        selected = self.items_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an item to edit!")
            return

        # Get the item's values
        item = self.items_tree.item(selected[0])
        values = item['values']
        if not values:
            messagebox.showerror("Error", "Invalid item selection!")
            return

        # Create edit window
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Item")
        edit_window.geometry("400x200")
        edit_window.transient(self.window)
        edit_window.grab_set()

        # Create and populate the quantity entry
        ttk.Label(edit_window, text="Quantity:").grid(row=0, column=0, padx=5, pady=5)
        qty_entry = ttk.Entry(edit_window, width=10)
        qty_entry.grid(row=0, column=1, padx=5, pady=5)
        qty_entry.insert(0, values[3])
        qty_entry.select_range(0, 'end')  # Select all text for easy editing

        def save_changes():
            try:
                quantity = float(qty_entry.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0!")
                    return

                # Get the original item from the library
                item_id = values[0]
                library_item = next((i for i in self.items if i['id'] == item_id), None)
                if not library_item:
                    messagebox.showerror("Error", "Item not found in library!")
                    return

                price = library_item['price']
                gst = price * quantity * 0.1 if self.gst_var.get() else 0
                total = (price * quantity) + gst

                # Update the tree item
                self.items_tree.item(selected[0], values=(
                    item_id,
                    library_item['name'],
                    library_item['description'],
                    f"{quantity:.2f}",
                    f"${price:.2f}",
                    f"${gst:.2f}",
                    f"${total:.2f}"
                ))

                self.update_total()
                edit_window.destroy()

            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity!")

        # Add save button
        ttk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=1, column=0, columnspan=2, pady=20)

        # Center the window
        edit_window.update_idletasks()
        width = edit_window.winfo_width()
        height = edit_window.winfo_height()
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_window.winfo_screenheight() // 2) - (height // 2)
        edit_window.geometry(f'{width}x{height}+{x}+{y}')

        # Set focus to quantity entry
        qty_entry.focus_set()

    def edit_quote_item(self, event=None):
        # Get the selected item
        selected = self.quote_items_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an item to edit!")
            return

        # Get the item's values
        item = self.quote_items_tree.item(selected[0])
        values = item['values']
        if not values:
            messagebox.showerror("Error", "Invalid item selection!")
            return

        # Create edit window
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Item")
        edit_window.geometry("400x200")
        edit_window.transient(self.window)
        edit_window.grab_set()

        # Create and populate the quantity entry
        ttk.Label(edit_window, text="Quantity:").grid(row=0, column=0, padx=5, pady=5)
        qty_entry = ttk.Entry(edit_window, width=10)
        qty_entry.grid(row=0, column=1, padx=5, pady=5)
        qty_entry.insert(0, values[3])
        qty_entry.select_range(0, 'end')  # Select all text for easy editing

        def save_changes():
            try:
                quantity = float(qty_entry.get())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0!")
                    return

                # Get the original item from the library
                item_id = values[0]
                library_item = next((i for i in self.items if i['id'] == item_id), None)
                if not library_item:
                    messagebox.showerror("Error", "Item not found in library!")
                    return

                price = library_item['price']
                gst = price * quantity * 0.1 if self.gst_var.get() else 0
                total = (price * quantity) + gst

                # Update the tree item
                self.quote_items_tree.item(selected[0], values=(
                    item_id,
                    library_item['name'],
                    library_item['description'],
                    f"{quantity:.2f}",
                    f"${price:.2f}",
                    f"${gst:.2f}",
                    f"${total:.2f}"
                ))

                self.update_total_quote()
                edit_window.destroy()

            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity!")

        # Add save button
        ttk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=1, column=0, columnspan=2, pady=20)

        # Center the window
        edit_window.update_idletasks()
        width = edit_window.winfo_width()
        height = edit_window.winfo_height()
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_window.winfo_screenheight() // 2) - (height // 2)
        edit_window.geometry(f'{width}x{height}+{x}+{y}')

        # Set focus to quantity entry
        qty_entry.focus_set()

    def update_item_selection(self):
        items = [(item['id'], item['name']) for item in self.items]
        self.item_selection['values'] = [f"{id} - {name}" for id, name in items]

    def update_item_selection_quote(self):
        items = [(item['id'], item['name']) for item in self.items]
        self.item_selection_quote['values'] = [f"{id} - {name}" for id, name in items]

    def create_new_item(self):
        # Create edit window
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Create New Item")
        edit_window.geometry("400x250")
        edit_window.transient(self.window)  # Make window modal
        edit_window.grab_set()  # Make window modal

        # Create entry fields
        ttk.Label(edit_window, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = ttk.Entry(edit_window, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="Description:").grid(row=1, column=0, padx=5, pady=5)
        desc_entry = ttk.Entry(edit_window, width=30)
        desc_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="Price (ex GST):").grid(row=2, column=0, padx=5, pady=5)
        price_entry = ttk.Entry(edit_window, width=15)
        price_entry.grid(row=2, column=1, padx=5, pady=5)

        def save_item():
            name = name_entry.get().strip()
            desc = desc_entry.get().strip()
            try:
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid price!")
                return

            if not name or not desc:
                messagebox.showerror("Error", "Name and Description are required!")
                return

            if price <= 0:
                messagebox.showerror("Error", "Price must be greater than 0!")
                return

            # Create new item
            item_id = self.generate_item_id()
            item = {
                'id': item_id,
                'name': name,
                'description': desc,
                'price': price
            }

            # Add to items list
            self.items.append(item)
            self.save_items()

            # Update all item-related UI elements
            self.update_items_list()
            self.update_item_selection()
            self.update_item_selection_quote()

            # Select the new item in the dropdown
            self.item_selection.set(f"{item_id} - {name}")
            if hasattr(self, 'item_selection_quote'):
                self.item_selection_quote.set(f"{item_id} - {name}")

            edit_window.destroy()

        # Add buttons
        button_frame = ttk.Frame(edit_window)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Save Item", command=save_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=edit_window.destroy).pack(side='left', padx=5)

        # Center the window
        edit_window.update_idletasks()
        width = edit_window.winfo_width()
        height = edit_window.winfo_height()
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_window.winfo_screenheight() // 2) - (height // 2)
        edit_window.geometry(f'{width}x{height}+{x}+{y}')

        # Set focus to name entry
        name_entry.focus_set()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = InvoiceSystem()
    app.run()
