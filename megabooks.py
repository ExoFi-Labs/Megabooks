import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os
import sys # For platform check in open_selected_pdf
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer #, Image (Import Image if you use it)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

# --- Constants ---
APP_CONFIG_FILE = 'app_config.json'
BUSINESS_DETAILS_FILE = 'business_details.json'
CLIENTS_PROSPECTS_FILE = 'clients_prospects.json'
ITEMS_FILE = 'items.json'
HISTORY_DATA_FILE = 'data.json' # For storing invoice/quote history metadata

DEFAULT_COUNTRY_DATA = {
    "Australia": {"tax_name": "GST", "tax_rate": 10.0, "currency_symbol": "$", "tax_id_label": "ABN"},
    "United States": {"tax_name": "Sales Tax", "tax_rate": 0.0, "currency_symbol": "$", "tax_id_label": "EIN/SSN"},
    "United Kingdom": {"tax_name": "VAT", "tax_rate": 20.0, "currency_symbol": "£", "tax_id_label": "VAT Reg No."},
    "Canada": {"tax_name": "GST/HST", "tax_rate": 5.0, "currency_symbol": "$", "tax_id_label": "Business Number"},
    "New Zealand": {"tax_name": "GST", "tax_rate": 15.0, "currency_symbol": "$", "tax_id_label": "IRD Number"},
    "Custom": {"tax_name": "Tax", "tax_rate": 0.0, "currency_symbol": "$", "tax_id_label": "Tax ID"}
}

# --- Theme Colors ---
# Professional Dark Theme (Solarized-inspired or similar)
DARK_THEME = {
    "bg": "#002b36",  # Base background (very dark blue/cyan)
    "fg": "#93a1a1",  # Main text (light grayish cyan)
    "entry_bg": "#073642",  # Slightly lighter background for inputs
    "entry_fg": "#eee8d5",  # Lighter text for inputs (off-white)
    "button_bg": "#268bd2",  # Blue for buttons
    "button_fg": "#ffffff",  # White text on buttons
    "button_active_bg": "#1a6a9e", # Darker blue on active
    "tree_bg": "#073642",
    "tree_fg": "#93a1a1",
    "tree_selected_bg": "#268bd2", # Blue for selection
    "tree_selected_fg": "#ffffff",
    "tab_bg": "#002b36",
    "tab_fg": "#657b83",  # Muted text for inactive tabs
    "tab_selected_bg": "#073642", # Active tab slightly lighter
    "tab_selected_fg": "#eee8d5", # Active tab text lighter
    "labelframe_fg": "#2aa198",  # Cyan for labelframe titles
    "heading_fg": "#cb4b16", # Orange/Red for main headings
    "tooltip_bg": "#073642",
    "tooltip_fg": "#eee8d5",
    "search_bg": "#073642",  # Search box background
    "search_fg": "#eee8d5",  # Search box text
    "search_highlight_bg": "#268bd2",  # Search highlight background
    "search_highlight_fg": "#ffffff",  # Search highlight text
    "button_hover_bg": "#2aa198",  # Button hover color
    "button_pressed_bg": "#1a6a9e",  # Button pressed color
    "border_color": "#2aa198",  # Border color for frames
    "separator_color": "#073642",  # Separator line color
    "success_color": "#859900",  # Success message color
    "error_color": "#dc322f",  # Error message color
    "warning_color": "#b58900"  # Warning message color
}

LIGHT_THEME = {
    "bg": "#fdf6e3",  # Base background (light cream)
    "fg": "#586e75",  # Main text (dark grayish blue)
    "entry_bg": "#eee8d5",  # Slightly darker cream for inputs
    "entry_fg": "#002b36",  # Very dark text for inputs
    "button_bg": "#268bd2",
    "button_fg": "#ffffff",
    "button_active_bg": "#1a6a9e",
    "tree_bg": "#fdf6e3", # Can be #ffffff for starker contrast if preferred
    "tree_fg": "#586e75",
    "tree_selected_bg": "#268bd2",
    "tree_selected_fg": "#ffffff",
    "tab_bg": "#eee8d5", # Slightly darker for tab bar
    "tab_fg": "#657b83",
    "tab_selected_bg": "#fdf6e3", # Active tab matches main bg
    "tab_selected_fg": "#002b36",
    "labelframe_fg": "#268bd2",
    "heading_fg": "#d33682", # Magenta for main headings
    "tooltip_bg": "#eee8d5",
    "tooltip_fg": "#002b36",
    "search_bg": "#ffffff",  # Search box background
    "search_fg": "#002b36",  # Search box text
    "search_highlight_bg": "#268bd2",  # Search highlight background
    "search_highlight_fg": "#ffffff",  # Search highlight text
    "button_hover_bg": "#2aa198",  # Button hover color
    "button_pressed_bg": "#1a6a9e",  # Button pressed color
    "border_color": "#268bd2",  # Border color for frames
    "separator_color": "#eee8d5",  # Separator line color
    "success_color": "#859900",  # Success message color
    "error_color": "#dc322f",  # Error message color
    "warning_color": "#b58900"  # Warning message color
}

class SearchableCombobox(ttk.Frame):
    def __init__(self, parent, width=30, **kwargs):
        super().__init__(parent)
        self.width = width
        self._create_widgets()
        self._setup_bindings()
        self._items = []
        self._filtered_items = []
        self._selected_item = None
        self.dropdown_window = None
        
    def _create_widgets(self):
        # Create a frame for the search entry and dropdown
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self, textvariable=self.search_var, width=self.width)
        self.search_entry.pack(side='left', fill='x', expand=True)
        
        # Create a button to show/hide the dropdown
        self.dropdown_button = ttk.Button(self, text="▼", width=3, command=self.toggle_dropdown)
        self.dropdown_button.pack(side='right')
        
    def _setup_bindings(self):
        self.search_var.trace('w', self._on_search_change)
        self.search_entry.bind('<FocusIn>', self._on_focus_in)
        self.search_entry.bind('<FocusOut>', self._on_focus_out)
        self.search_entry.bind('<Return>', self._on_return)
        self.search_entry.bind('<Escape>', self._on_escape)
        self.search_entry.bind('<Down>', self._on_down)
        self.search_entry.bind('<Up>', self._on_up)
        
    def _on_search_change(self, *args):
        search_text = self.search_var.get().lower()
        self._filtered_items = [item for item in self._items if search_text in item.lower()]
        self._update_listbox()
        
    def _update_listbox(self):
        if hasattr(self, 'listbox') and self.listbox:
            self.listbox.delete(0, tk.END)
            for item in self._filtered_items:
                self.listbox.insert(tk.END, item)
            
    def _on_select(self, event):
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            self._selected_item = self._filtered_items[index]
            self.search_var.set(self._selected_item)
            self.hide_dropdown()
            self.event_generate('<<ComboboxSelected>>')
            
    def _on_focus_in(self, event):
        self.show_dropdown()
        
    def _on_focus_out(self, event):
        # Add a small delay to allow for selection
        self.after(200, self.hide_dropdown)
        
    def _on_return(self, event):
        if self.listbox.curselection():
            self._on_select(None)
        return "break"
        
    def _on_escape(self, event):
        self.hide_dropdown()
        return "break"
        
    def _on_down(self, event):
        if not self.dropdown_window.winfo_ismapped():
            self.show_dropdown()
        else:
            current = self.listbox.curselection()
            if current:
                next_idx = min(current[0] + 1, self.listbox.size() - 1)
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(next_idx)
                self.listbox.see(next_idx)
        return "break"
        
    def _on_up(self, event):
        if self.dropdown_window.winfo_ismapped():
            current = self.listbox.curselection()
            if current:
                next_idx = max(current[0] - 1, 0)
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(next_idx)
                self.listbox.see(next_idx)
        return "break"
        
    def show_dropdown(self):
        if not self.dropdown_window:
            # Create a new toplevel window for the dropdown
            self.dropdown_window = tk.Toplevel(self)
            self.dropdown_window.overrideredirect(True)  # Remove window decorations
            self.dropdown_window.attributes('-topmost', True)  # Keep on top
            
            # Create a frame in the toplevel window
            dropdown_frame = ttk.Frame(self.dropdown_window)
            dropdown_frame.pack(fill='both', expand=True)
            
            # Create new listbox and scrollbar in the dropdown frame
            self.listbox = tk.Listbox(dropdown_frame, width=self.width, height=6, 
                                    selectmode='single', exportselection=False)
            self.listbox.pack(side='left', fill='both', expand=True)
            
            self.scrollbar = ttk.Scrollbar(dropdown_frame, orient='vertical', 
                                         command=self.listbox.yview)
            self.scrollbar.pack(side='right', fill='y')
            self.listbox.configure(yscrollcommand=self.scrollbar.set)
            
            # Position the dropdown window
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
            self.dropdown_window.geometry(f"+{x}+{y}")
            
            # Set up listbox-specific bindings
            self.listbox.bind('<<ListboxSelect>>', self._on_select)
            
            # Update the listbox contents
            self._update_listbox()
            
            # Bind events to handle window focus
            self.dropdown_window.bind('<FocusOut>', self._on_dropdown_focus_out)
            self.dropdown_window.bind('<Escape>', lambda e: self.hide_dropdown())
            
    def hide_dropdown(self):
        if self.dropdown_window:
            self.dropdown_window.destroy()
            self.dropdown_window = None
            self.listbox = None
            self.scrollbar = None
            
    def _on_dropdown_focus_out(self, event):
        # Check if the focus is moving to our main widget
        if event.widget == self.dropdown_window:
            return
        # Add a small delay to allow for selection
        self.after(200, self.hide_dropdown)
        
    def toggle_dropdown(self):
        if self.dropdown_window:
            self.hide_dropdown()
        else:
            self.show_dropdown()
            
    def get(self):
        return self._selected_item
        
    def set(self, value):
        self.search_var.set(value)
        self._selected_item = value
        
    def configure(self, **kwargs):
        if 'values' in kwargs:
            self._items = kwargs['values']
            self._filtered_items = self._items.copy()
            self._update_listbox()
        if 'width' in kwargs:
            self.width = kwargs['width']
            self.search_entry.configure(width=self.width)
            self.listbox.configure(width=self.width)
            
    def config(self, **kwargs):
        self.configure(**kwargs)

class InvoiceSystem:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Megabooks")
        self.window.geometry("1200x800")  # Increased from 900x750
        self.window.pack_propagate(False)
        # Initial bg, will be overridden by theme
        self.window.configure(bg=LIGHT_THEME["bg"])

        self.style = ttk.Style()

        self.app_settings = {
            'selected_country': 'Australia', 'tax_name': 'GST', 'tax_rate': 10.0,
            'apply_tax_default': True, 'theme': 'Light', 'font_size': '12'
        }
        self.load_app_settings()

        self.business_details = {
            'name': '', 'address': '', 'phone': '', 'email': '',
            'tax_identifier_value': '', 'bank': '', 'bsb': '', 'account': '',
            'logo': '', 'invoice_terms': '',
            'currency_symbol': DEFAULT_COUNTRY_DATA[self.app_settings['selected_country']]['currency_symbol']
        }
        self.business_entries = {}
        self.load_business_details()

        self.clients = []
        self.prospects = []
        self.load_clients_prospects()

        self.items = []
        self.item_counter = 0
        self.load_items()

        self.history_records = []
        self.load_history_data()

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=(5,10)) # Added bottom pady

        # Tab Frames (ensure they are ttk.Frame for styling)
        self.general_settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.general_settings_frame, text='App Settings')
        self.business_details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.business_details_frame, text='Business Details')
        self.clients_frame = ttk.Frame(self.notebook) # Will contain another notebook
        self.notebook.add(self.clients_frame, text='Clients & Prospects')
        self.items_tab_frame = ttk.Frame(self.notebook) # For item library
        self.notebook.add(self.items_tab_frame, text='Items')
        self.invoice_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.invoice_frame, text='New Invoice')
        self.quote_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.quote_frame, text='New Quote')
        self.history_frame_tab = ttk.Frame(self.notebook) # For history tab
        self.notebook.add(self.history_frame_tab, text='History')
        self.help_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.help_frame, text='Help')

        self.create_general_settings_tab()
        self.create_business_details_tab()
        self.create_clients_tab()
        self.create_items_tab()
        self.create_invoice_tab()
        self.create_quote_tab()
        self.create_history_tab()
        self.create_help_tab()

        self.update_ui_for_app_settings() # Apply theme, font, and other UI updates

        # Load and update lists
        self.update_clients_list()
        self.update_prospects_list()
        self.update_items_list() # Updates item library tree
        self.update_client_dropdown()
        self.update_quote_client_dropdown()
        self.update_item_selection()       # Updates invoice item combobox
        self.update_item_selection_quote() # Updates quote item combobox
        self.update_history_display()

    def load_app_settings(self):
        try:
            if os.path.exists(APP_CONFIG_FILE):
                with open(APP_CONFIG_FILE, 'r') as f:
                    loaded_settings = json.load(f)
                    for key, default_value in self.app_settings.items():
                        self.app_settings[key] = loaded_settings.get(key, default_value)
        except Exception as e:
            print(f"Error loading app settings: {e}. Using defaults.")
            self.app_settings = {
                'selected_country': 'Australia', 'tax_name': 'GST', 'tax_rate': 10.0,
                'apply_tax_default': True, 'theme': 'Light', 'font_size': '12'
            }

    def save_app_settings(self):
        try:
            if hasattr(self, 'country_var'): self.app_settings['selected_country'] = self.country_var.get()
            if hasattr(self, 'tax_name_var'): self.app_settings['tax_name'] = self.tax_name_var.get()
            if hasattr(self, 'tax_rate_var'):
                try: self.app_settings['tax_rate'] = float(self.tax_rate_var.get())
                except ValueError: messagebox.showerror("Error", "Invalid tax rate."); return False
            if hasattr(self, 'apply_tax_default_var'): self.app_settings['apply_tax_default'] = self.apply_tax_default_var.get()
            if hasattr(self, 'theme_var_app'): self.app_settings['theme'] = self.theme_var_app.get()
            if hasattr(self, 'font_size_var_app'): self.app_settings['font_size'] = self.font_size_var_app.get()

            with open(APP_CONFIG_FILE, 'w') as f:
                json.dump(self.app_settings, f, indent=4)
            messagebox.showinfo("Success", "App settings saved successfully!") # Removed restart message for now
            self.update_ui_for_app_settings()
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save app settings: {e}")
            return False

    def create_general_settings_tab(self):
        frame = self.general_settings_frame
        self.main_heading_gs = ttk.Label(frame, text="Application Settings") # Style applied in update_ui
        self.main_heading_gs.grid(row=0, column=0, columnspan=2, pady=(10,15), padx=5)

        row_idx = 1
        self.loc_frame_gs = ttk.LabelFrame(frame, text="Localization & Tax")
        self.loc_frame_gs.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        row_idx +=1

        ttk.Label(self.loc_frame_gs, text="Country:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.country_var = tk.StringVar(value=self.app_settings.get('selected_country', 'Australia'))
        self.country_combo = ttk.Combobox(self.loc_frame_gs, textvariable=self.country_var, values=list(DEFAULT_COUNTRY_DATA.keys()), width=30, state="readonly")
        self.country_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.country_combo.bind("<<ComboboxSelected>>", self.on_country_selected)

        ttk.Label(self.loc_frame_gs, text="Tax Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.tax_name_var = tk.StringVar(value=self.app_settings.get('tax_name', 'Tax'))
        self.tax_name_entry = ttk.Entry(self.loc_frame_gs, textvariable=self.tax_name_var, width=33)
        self.tax_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.loc_frame_gs, text="Tax Rate (%):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.tax_rate_var = tk.StringVar(value=str(self.app_settings.get('tax_rate', 0.0)))
        self.tax_rate_entry = ttk.Entry(self.loc_frame_gs, textvariable=self.tax_rate_var, width=10)
        self.tax_rate_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w") # align left

        self.apply_tax_default_var = tk.BooleanVar(value=self.app_settings.get('apply_tax_default', True))
        self.apply_tax_checkbutton = ttk.Checkbutton(self.loc_frame_gs, text="Apply tax by default on new Invoices/Quotes", variable=self.apply_tax_default_var)
        self.apply_tax_checkbutton.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.loc_frame_gs.columnconfigure(1, weight=1)


        self.ui_frame_gs = ttk.LabelFrame(frame, text="User Interface")
        self.ui_frame_gs.grid(row=row_idx, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        row_idx +=1

        ttk.Label(self.ui_frame_gs, text="Select Theme:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.theme_var_app = tk.StringVar(value=self.app_settings.get('theme', "Light"))
        self.theme_combo = ttk.Combobox(self.ui_frame_gs, textvariable=self.theme_var_app, values=["Light", "Dark"], width=30, state="readonly")
        self.theme_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.ui_frame_gs, text="Font Size:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.font_size_var_app = tk.StringVar(value=str(self.app_settings.get('font_size', "12"))) # Ensure string
        self.font_size_combo = ttk.Combobox(self.ui_frame_gs, textvariable=self.font_size_var_app, values=["10", "12", "14", "16"], width=30, state="readonly")
        self.font_size_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.ui_frame_gs.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Save App Settings", command=self.save_app_settings).grid(row=row_idx, column=0, columnspan=2, pady=20)
        frame.columnconfigure(0, weight=1)

    def on_country_selected(self, event=None):
        # ... (same as before)
        selected_country_name = self.country_var.get()
        country_data = DEFAULT_COUNTRY_DATA.get(selected_country_name)
        if country_data:
            self.tax_name_var.set(country_data['tax_name'])
            self.tax_rate_var.set(str(country_data['tax_rate']))
            if hasattr(self, 'business_entries') and 'currency_symbol' in self.business_entries and self.business_entries['currency_symbol']:
                self.business_entries['currency_symbol'].delete(0, tk.END)
                self.business_entries['currency_symbol'].insert(0, country_data['currency_symbol'])
            else: self.business_details['currency_symbol'] = country_data['currency_symbol'] # Fallback
            if hasattr(self, 'tax_id_label_widget') and self.tax_id_label_widget:
                self.tax_id_label_widget.config(text=country_data['tax_id_label'] + ":")

    def update_ui_for_app_settings(self):
        current_theme_name = self.app_settings.get('theme', 'Light')
        theme_colors = DARK_THEME if current_theme_name == 'Dark' else LIGHT_THEME
        font_size = int(self.app_settings.get('font_size', 12))
        heading_font_size = font_size + 4 # Larger for main headings
        tree_heading_font_size = font_size # Same as base or slightly smaller
        tree_row_font_size = font_size -1 if font_size > 10 else font_size

        self.window.configure(bg=theme_colors["bg"])
        self.style.theme_use('default') # IMPORTANT: Reset to apply custom styles cleanly

        # General widget styles
        self.style.configure(".", font=('Helvetica', font_size)) # Default font for all ttk widgets
        self.style.configure("TFrame", background=theme_colors["bg"])
        self.style.configure("TLabel", background=theme_colors["bg"], foreground=theme_colors["fg"])
        self.style.configure("TButton", padding=6,
                             background=theme_colors["button_bg"], foreground=theme_colors["button_fg"],
                             bordercolor=theme_colors["button_bg"]) # Ensure border matches
        self.style.map("TButton",
                       background=[('active', theme_colors["button_active_bg"]), ('pressed', theme_colors["button_active_bg"])],
                       foreground=[('active', theme_colors["button_fg"]), ('pressed', theme_colors["button_fg"])])
        
        self.style.configure("TEntry", fieldbackground=theme_colors["entry_bg"], foreground=theme_colors["entry_fg"],
                             insertcolor=theme_colors["entry_fg"]) # Cursor color
        
        # Combobox styling needs careful mapping for all states
        self.style.map('TCombobox',
            fieldbackground=[('readonly', theme_colors["entry_bg"])],
            foreground=[('readonly', theme_colors["entry_fg"])],
            selectbackground=[('readonly', theme_colors["entry_bg"])], # Dropdown list bg
            selectforeground=[('readonly', theme_colors["entry_fg"])], # Dropdown list fg
            background= [('readonly', theme_colors["entry_bg"])] # Arrow button bg
        )
        self.style.configure("TCombobox", lightcolor=[('readonly', theme_colors["entry_bg"])], # border
                                         darkcolor=[('readonly', theme_colors["entry_bg"])]) # border


        self.style.configure("Treeview", background=theme_colors["tree_bg"], foreground=theme_colors["tree_fg"],
                             fieldbackground=theme_colors["tree_bg"], font=('Helvetica', tree_row_font_size),
                             rowheight=int(font_size * 1.8)) # Adjust row height based on font
        self.style.configure("Treeview.Heading", background=theme_colors["button_bg"], foreground=theme_colors["button_fg"],
                             font=('Helvetica', tree_heading_font_size, 'bold'), relief="flat", padding=(3,3))
        self.style.map("Treeview.Heading", relief=[('active','groove'),('pressed','sunken')])
        self.style.map("Treeview",
                       background=[('selected', theme_colors["tree_selected_bg"])],
                       foreground=[('selected', theme_colors["tree_selected_fg"])])

        self.style.configure("TNotebook", background=theme_colors["bg"])
        self.style.configure("TNotebook.Tab", background=theme_colors["tab_bg"], foreground=theme_colors["tab_fg"],
                             padding=[font_size, font_size//2], font=('Helvetica', font_size)) # Generous padding
        self.style.map("TNotebook.Tab",
                       background=[('selected', theme_colors["tab_selected_bg"])],
                       foreground=[('selected', theme_colors["tab_selected_fg"])],
                       font=[('selected', ('Helvetica', font_size, 'bold'))]) # Bold active tab

        self.style.configure("TCheckbutton", background=theme_colors["bg"], foreground=theme_colors["fg"],
                             indicatorforeground=theme_colors["fg"], indicatorbackground=theme_colors["entry_bg"])
        self.style.map("TCheckbutton", background=[('active', theme_colors["bg"])])
        
        self.style.configure("TLabelframe", background=theme_colors["bg"], bordercolor=theme_colors.get("labelframe_fg", theme_colors["fg"]))
        self.style.configure("TLabelframe.Label", background=theme_colors["bg"], foreground=theme_colors["labelframe_fg"],
                             font=('Helvetica', font_size, 'bold'))
        
        # Apply to specific important labels
        if hasattr(self, 'main_heading_gs'):
            self.main_heading_gs.configure(font=('Arial', heading_font_size, 'bold'), foreground=theme_colors["heading_fg"])
        if hasattr(self, 'main_heading_bd'):
            self.main_heading_bd.configure(font=('Arial', heading_font_size, 'bold'), foreground=theme_colors["heading_fg"])
        if hasattr(self, 'main_heading_help'):
            self.main_heading_help.configure(font=('Arial', heading_font_size, 'bold'), foreground=theme_colors["heading_fg"])

        # --- Update dynamic text based on tax/currency ---
        tax_name = self.app_settings.get('tax_name', 'Tax')
        tax_rate = self.app_settings.get('tax_rate', 0.0)
        tax_checkbox_label = f"Include {tax_name} ({tax_rate:.1f}%)"
        price_ex_tax_header = f"Price (ex {tax_name})"

        if hasattr(self, 'gst_check_invoice'): self.gst_check_invoice.config(text=tax_checkbox_label)
        if hasattr(self, 'gst_check_quote'): self.gst_check_quote.config(text=tax_checkbox_label)
        if hasattr(self, 'items_tree'):
            self.items_tree.heading('GST', text=tax_name); self.items_tree.heading('Price', text=price_ex_tax_header)
        if hasattr(self, 'quote_items_tree'):
            self.quote_items_tree.heading('GST', text=tax_name); self.quote_items_tree.heading('Price', text=price_ex_tax_header)
        if hasattr(self, 'items_library_tree'):
            self.items_library_tree.heading('Price', text=price_ex_tax_header)
        if hasattr(self, 'item_price_ex_tax_label_widget'):
            self.item_price_ex_tax_label_widget.config(text=f"Price (ex {tax_name}):")

        if hasattr(self, 'subtotal_label'): self.update_total()
        if hasattr(self, 'subtotal_label_quote'): self.update_total_quote()
        
        self.update_items_list() # Item library tree content
        if hasattr(self, 'items_tree') and self.items_tree.get_children():
            self.repopulate_treeview_with_current_settings(self.items_tree, 'invoice')
        if hasattr(self, 'quote_items_tree') and self.quote_items_tree.get_children():
            self.repopulate_treeview_with_current_settings(self.quote_items_tree, 'quote')
        
        self.window.update_idletasks() # Ensure all style changes are rendered

    def repopulate_treeview_with_current_settings(self, tree, doc_type):
        # ... (same as before, ensure it uses _get_currency_symbol() and _get_current_tax_rate_decimal())
        current_items_data = []
        for item_id_in_tree in tree.get_children():
            values = tree.item(item_id_in_tree, 'values')
            original_item_id, qty_str = values[0], values[3]
            try: qty = float(qty_str)
            except ValueError: qty = 0
            original_item_info = next((i for i in self.items if i['id'] == original_item_id), None)
            if original_item_info:
                 current_items_data.append({'id': original_item_id, 'qty': qty, 'name': original_item_info['name'], 'description': original_item_info['description'], 'price': original_item_info['price']})

        tree.delete(*tree.get_children())
        tax_rate_decimal = self._get_current_tax_rate_decimal()
        currency_symbol = self._get_currency_symbol()
        apply_tax_for_this_doc = (self.gst_var.get() if doc_type == 'invoice' and hasattr(self, 'gst_var') else
                                  self.gst_var_quote.get() if doc_type == 'quote' and hasattr(self, 'gst_var_quote') else False)

        for item_data in current_items_data:
            price_ex_tax, qty = item_data['price'], item_data['qty']
            tax_amount = price_ex_tax * qty * tax_rate_decimal if apply_tax_for_this_doc else 0
            total_inc_tax = (price_ex_tax * qty) + tax_amount
            tree.insert('', 'end', values=(
                item_data['id'], item_data['name'], item_data['description'], f"{qty:.2f}",
                f"{currency_symbol}{price_ex_tax:.2f}", f"{currency_symbol}{tax_amount:.2f}", f"{currency_symbol}{total_inc_tax:.2f}"
            ))
        if doc_type == 'invoice': self.update_total()
        elif doc_type == 'quote': self.update_total_quote()

    def create_business_details_tab(self):
        # ... (Ensure main_heading_bd is created and stored)
        frame = self.business_details_frame
        self.main_heading_bd = ttk.Label(frame, text="Business Details") # Style applied in update_ui
        self.main_heading_bd.grid(row=0, column=0, columnspan=2, pady=(10,15))

        default_bd_keys = ['name', 'address', 'phone', 'email', 'tax_identifier_value',
                           'bank', 'bsb', 'account', 'logo', 'invoice_terms', 'currency_symbol']
        for key in default_bd_keys:
            if key not in self.business_details: self.business_details[key] = ""
        initial_tax_id_label = DEFAULT_COUNTRY_DATA.get(self.app_settings['selected_country'], {}).get('tax_id_label', 'Tax ID')
        fields = [
            ('Business Name:', 'name'), ('Address:', 'address'), ('Phone:', 'phone'), ('Email:', 'email'),
            (initial_tax_id_label + ':', 'tax_identifier_value'), ('Bank:', 'bank'), ('BSB:', 'bsb'),
            ('Account:', 'account'), ('Company Logo Path:', 'logo'), ('Invoice Terms:', 'invoice_terms'),
            ('Currency Symbol:', 'currency_symbol')
        ]
        self.business_entries = {}
        for row, (label_text, key) in enumerate(fields, start=1):
            field_frame = ttk.Frame(frame)
            field_frame.grid(row=row, column=0, columnspan=2, pady=3, padx=10, sticky='ew') # Reduced pady
            current_label = ttk.Label(field_frame, text=label_text, width=20, anchor="w")
            current_label.pack(side='left', padx=(0,5))
            if key == 'tax_identifier_value': self.tax_id_label_widget = current_label
            entry = ttk.Entry(field_frame)
            entry.pack(side='left', expand=True, fill='x')
            entry.insert(0, self.business_details.get(key, ""))
            self.business_entries[key] = entry
            entry.bind("<Enter>", lambda e, text=label_text.split(':')[0]: self.show_tooltip(e, text))
            entry.bind("<Leave>", self.hide_tooltip)
        
        button_frame_bd = ttk.Frame(frame)
        button_frame_bd.grid(row=len(fields) + 1, column=0, columnspan=2, pady=(15,10))
        ttk.Button(button_frame_bd, text="Save Business Details", command=self.save_business_details).pack(side="left", padx=10)
        ttk.Button(button_frame_bd, text="Reset Business Details", command=self.reset_business_details).pack(side="left", padx=10)
        frame.columnconfigure(0, weight=1)

    def show_tooltip(self, event, text):
        # ... (Ensure it uses theme colors)
        if hasattr(self, 'tooltip_window') and self.tooltip_window.winfo_exists():
            self.tooltip_window.destroy()
        self.tooltip_window = tk.Toplevel(self.window)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{event.x_root + 15}+{event.y_root + 10}")
        theme_colors = DARK_THEME if self.app_settings.get('theme') == 'Dark' else LIGHT_THEME
        label = ttk.Label(self.tooltip_window, text=text, justify='left',
                          background=theme_colors.get("tooltip_bg", "#FFFFE0"), 
                          foreground=theme_colors.get("tooltip_fg", "#000000"),
                          relief='solid', borderwidth=1, padding=(3,2),
                          font=('Helvetica', int(self.app_settings.get('font_size', 12))-2)) # Slightly smaller font
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if hasattr(self, 'tooltip_window') and self.tooltip_window.winfo_exists():
            self.tooltip_window.destroy()
            # delattr(self, 'tooltip_window') # Safer to not delete if rapidly re-triggered

    def reset_business_details(self):
        # ... (same as before)
        for key, entry in self.business_entries.items():
            entry.delete(0, 'end'); self.business_details[key] = ""
        country_data = DEFAULT_COUNTRY_DATA.get(self.app_settings.get('selected_country'))
        if country_data and 'currency_symbol' in self.business_entries and self.business_entries['currency_symbol']: # Check entry exists
            self.business_entries['currency_symbol'].insert(0, country_data['currency_symbol'])
            self.business_details['currency_symbol'] = country_data['currency_symbol']

    def save_business_details(self):
        # ... (same as before)
        email = self.business_entries['email'].get().strip()
        phone = self.business_entries['phone'].get().strip()
        if email and not self.validate_email(email): messagebox.showerror("Error", "Valid email required."); return
        if phone and not self.validate_phone(phone): messagebox.showerror("Error", "Valid phone (>=10 digits)."); return
        for key, entry in self.business_entries.items(): self.business_details[key] = entry.get().strip()
        try:
            with open(BUSINESS_DETAILS_FILE, 'w') as f: json.dump(self.business_details, f, indent=4)
            messagebox.showinfo("Success", "Business details saved!")
            self.update_ui_for_app_settings() # Crucial to reflect currency symbol change
        except Exception as e: messagebox.showerror("Error", f"Failed to save business details: {e}")


    def load_business_details(self):
        # ... (same as before)
        try:
            if os.path.exists(BUSINESS_DETAILS_FILE):
                with open(BUSINESS_DETAILS_FILE, 'r') as f: loaded_details = json.load(f)
                for key, default_value in self.business_details.items():
                    self.business_details[key] = loaded_details.get(key, default_value)
                if hasattr(self, 'business_entries') and self.business_entries: # If UI exists
                    for key, entry_widget in self.business_entries.items():
                        entry_widget.delete(0, tk.END)
                        entry_widget.insert(0, self.business_details.get(key, ''))
            else: self.business_details['currency_symbol'] = DEFAULT_COUNTRY_DATA[self.app_settings['selected_country']]['currency_symbol']
        except Exception as e:
            print(f"Error loading business details: {e}.")
            self.business_details = { # Reset to defaults
                'name': '', 'address': '', 'phone': '', 'email': '', 'tax_identifier_value': '',
                'bank': '', 'bsb': '', 'account': '', 'logo': '', 'invoice_terms': '',
                'currency_symbol': DEFAULT_COUNTRY_DATA[self.app_settings.get('selected_country', 'Australia')]['currency_symbol']
            }


    def validate_email(self, email): return "@" in email and "." in email if email else True
    def validate_phone(self, phone): return phone.isdigit() and len(phone) >= 10 if phone else True

    def create_clients_tab(self):
        # clients_outer_frame = ttk.Frame(self.notebook) # Already created and stored as self.clients_frame
        # self.notebook.add(clients_outer_frame, text='Clients & Prospects')
        clients_outer_frame = self.clients_frame


        clients_notebook = ttk.Notebook(clients_outer_frame)
        clients_notebook.pack(expand=True, fill='both', padx=5, pady=5)

        clients_tab_content = ttk.Frame(clients_notebook)
        clients_notebook.add(clients_tab_content, text='Clients')
        self.clients_tree = ttk.Treeview(clients_tab_content, columns=('Name', 'Email', 'Address', 'Phone'), show='headings')
        for col_name in ('Name', 'Email', 'Address', 'Phone'):
            self.clients_tree.heading(col_name, text=col_name)
            self.clients_tree.column(col_name, width=150, minwidth=100, stretch=tk.YES)
        self.clients_tree.pack(pady=5, padx=5, fill='both', expand=True)


        prospects_tab_content = ttk.Frame(clients_notebook)
        clients_notebook.add(prospects_tab_content, text='Prospects')
        self.prospects_tree = ttk.Treeview(prospects_tab_content, columns=('Name', 'Email', 'Address', 'Phone'), show='headings')
        for col_name in ('Name', 'Email', 'Address', 'Phone'):
            self.prospects_tree.heading(col_name, text=col_name)
            self.prospects_tree.column(col_name, width=150, minwidth=100, stretch=tk.YES)
        self.prospects_tree.pack(pady=5, padx=5, fill='both', expand=True)


        add_edit_frame_clients = ttk.LabelFrame(clients_outer_frame, text="Add/Edit Client or Prospect")
        add_edit_frame_clients.pack(pady=10, padx=5, fill='x')
        
        self.client_prospect_entries = {}
        fields = {"Name:": "name", "Email:": "email", "Address:": "address", "Phone:": "phone"}
        current_row = 0
        for i, (label_text, key) in enumerate(fields.items()):
            ttk.Label(add_edit_frame_clients, text=label_text).grid(row=current_row, column=(i%2)*2, padx=5, pady=3, sticky="w")
            entry = ttk.Entry(add_edit_frame_clients, width=35)
            entry.grid(row=current_row, column=(i%2)*2 + 1, padx=5, pady=3, sticky="ew")
            self.client_prospect_entries[key] = entry
            if i%2 != 0: current_row +=1 # New row after two fields
        
        add_edit_frame_clients.columnconfigure(1, weight=1)
        add_edit_frame_clients.columnconfigure(3, weight=1)

        client_buttons_frame = ttk.Frame(add_edit_frame_clients)
        client_buttons_frame.grid(row=current_row, column=0, columnspan=4, pady=(10,5)) # Adjusted pady
        ttk.Button(client_buttons_frame, text="Add Prospect", command=self.add_prospect).pack(side='left', padx=3)
        ttk.Button(client_buttons_frame, text="Add Client", command=self.add_client).pack(side='left', padx=3)
        ttk.Button(client_buttons_frame, text="Convert", command=self.convert_to_client).pack(side='left', padx=3)
        self.edit_client_button = ttk.Button(client_buttons_frame, text="Edit", command=self.edit_selected_client_prospect)
        self.edit_client_button.pack(side='left', padx=3)
        ttk.Button(client_buttons_frame, text="Delete", command=self.delete_selected_client_prospect).pack(side='left', padx=3)

        self.clients_tree.bind('<Double-1>', lambda e: self.edit_selected_client_prospect())
        self.prospects_tree.bind('<Double-1>', lambda e: self.edit_selected_client_prospect())


    def _get_client_prospect_entry_values(self):
        return {key: entry.get().strip() for key, entry in self.client_prospect_entries.items()}

    def _set_client_prospect_entry_values(self, data_dict):
        for key, value in data_dict.items():
            if key in self.client_prospect_entries:
                self.client_prospect_entries[key].delete(0, tk.END)
                self.client_prospect_entries[key].insert(0, value)

    def _clear_client_prospect_entries(self):
        for entry in self.client_prospect_entries.values(): entry.delete(0, tk.END)

    def add_client(self):
        data = self._get_client_prospect_entry_values()
        if not all(data.values()): messagebox.showerror("Error", "All fields are required!"); return
        self.clients.append(data)
        self.update_clients_list(); self.save_clients_prospects(); self._clear_client_prospect_entries()
        self.update_client_dropdown(); self.update_quote_client_dropdown()

    def add_prospect(self):
        data = self._get_client_prospect_entry_values()
        if not all(data.values()): messagebox.showerror("Error", "All fields are required!"); return
        self.prospects.append(data)
        self.update_prospects_list(); self.save_clients_prospects(); self._clear_client_prospect_entries()
        self.update_quote_client_dropdown()

    def convert_to_client(self):
        selected = self.prospects_tree.selection()
        if not selected: messagebox.showerror("Error", "Select prospect to convert."); return
        index = self.prospects_tree.index(selected[0])
        prospect = self.prospects.pop(index)
        self.clients.append(prospect)
        self.update_prospects_list(); self.update_clients_list(); self.save_clients_prospects()
        self.update_client_dropdown(); self.update_quote_client_dropdown()

    def edit_selected_client_prospect(self):
        selected_id = self.clients_tree.selection() or self.prospects_tree.selection()
        if not selected_id: messagebox.showerror("Error", "Select item to edit."); return
        tree = self.clients_tree if self.clients_tree.selection() else self.prospects_tree
        data_list = self.clients if self.clients_tree.selection() else self.prospects
        index = tree.index(selected_id[0])
        item_data = data_list[index] # This is a dictionary
        self._set_client_prospect_entry_values(item_data)
        self.edit_client_button.config(text="Save", command=lambda current_item=item_data: self.save_client_prospect_edit(current_item))


    def save_client_prospect_edit(self, item_to_update): # item_to_update is a dict from self.clients/self.prospects
        new_data = self._get_client_prospect_entry_values()
        if not all(new_data.values()): messagebox.showerror("Error", "All fields required."); return
        item_to_update.update(new_data) # Update the original dictionary in the list
        self.update_clients_list(); self.update_prospects_list(); self.save_clients_prospects()
        self._clear_client_prospect_entries()
        self.update_client_dropdown(); self.update_quote_client_dropdown()
        self.edit_client_button.config(text="Edit", command=self.edit_selected_client_prospect)


    def delete_selected_client_prospect(self):
        # ... (same as before)
        selected_id = self.clients_tree.selection() or self.prospects_tree.selection()
        if not selected_id: messagebox.showerror("Error", "Select item to delete."); return
        if messagebox.askyesno("Confirm Delete", "Delete selected item?"):
            if self.clients_tree.selection():
                self.clients.pop(self.clients_tree.index(selected_id[0]))
                self.update_clients_list(); self.update_client_dropdown(); self.update_quote_client_dropdown()
            else:
                self.prospects.pop(self.prospects_tree.index(selected_id[0]))
                self.update_prospects_list(); self.update_quote_client_dropdown()
            self.save_clients_prospects()

    def update_clients_list(self):
        self.clients_tree.delete(*self.clients_tree.get_children())
        for client in self.clients: self.clients_tree.insert('', 'end', values=(client['name'], client['email'], client['address'], client['phone']))

    def update_prospects_list(self):
        self.prospects_tree.delete(*self.prospects_tree.get_children())
        for prospect in self.prospects: self.prospects_tree.insert('', 'end', values=(prospect['name'], prospect['email'], prospect['address'], prospect['phone']))

    def load_clients_prospects(self):
        # ... (same as before)
        try:
            if os.path.exists(CLIENTS_PROSPECTS_FILE):
                with open(CLIENTS_PROSPECTS_FILE, 'r') as f: data = json.load(f)
                self.clients = data.get('clients', [])
                self.prospects = data.get('prospects', [])
        except FileNotFoundError: self.clients, self.prospects = [], []
        except json.JSONDecodeError: print(f"Error decoding {CLIENTS_PROSPECTS_FILE}"); self.clients, self.prospects = [], []


    def save_clients_prospects(self):
        with open(CLIENTS_PROSPECTS_FILE, 'w') as f: json.dump({'clients': self.clients, 'prospects': self.prospects}, f, indent=4)

    def create_items_tab(self):
        # items_tab_frame = ttk.Frame(self.notebook) # Already self.items_tab_frame
        # self.notebook.add(items_tab_frame, text='Items')
        items_tab_frame = self.items_tab_frame


        price_ex_tax_header = f"Price (ex {self.app_settings.get('tax_name', 'Tax')})"
        self.items_library_tree = ttk.Treeview(items_tab_frame, columns=('ID', 'Name', 'Description', 'Price'), show='headings')
        self.items_library_tree.heading('ID', text='ID'); self.items_library_tree.heading('Name', text='Name')
        self.items_library_tree.heading('Description', text='Description'); self.items_library_tree.heading('Price', text=price_ex_tax_header)
        for col, wid, stretch_val in [('ID', 70, tk.NO), ('Name', 200, tk.YES), ('Description', 300, tk.YES), ('Price', 100, tk.NO)]: 
            self.items_library_tree.column(col, width=wid, minwidth=50, stretch=stretch_val)
        self.items_library_tree.pack(pady=5, padx=5, fill='both', expand=True)

        add_item_lib_frame = ttk.LabelFrame(items_tab_frame, text="Add/Edit Library Item")
        add_item_lib_frame.pack(pady=10, padx=5, fill='x')
        
        # Fields for adding/editing item
        ttk.Label(add_item_lib_frame, text="Name:").grid(row=0, column=0, padx=5, pady=3, sticky="w")
        self.item_name_entry = ttk.Entry(add_item_lib_frame)
        self.item_name_entry.grid(row=0, column=1, padx=5, pady=3, sticky="ew")
        
        self.item_price_ex_tax_label_widget = ttk.Label(add_item_lib_frame, text=price_ex_tax_header + ":")
        self.item_price_ex_tax_label_widget.grid(row=0, column=2, padx=5, pady=3, sticky="w")
        self.item_price_entry = ttk.Entry(add_item_lib_frame, width=15)
        self.item_price_entry.grid(row=0, column=3, padx=5, pady=3, sticky="w")

        ttk.Label(add_item_lib_frame, text="Description:").grid(row=1, column=0, padx=5, pady=3, sticky="w")
        self.item_desc_entry = ttk.Entry(add_item_lib_frame)
        self.item_desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=3, sticky="ew") # Span description
        
        add_item_lib_frame.columnconfigure(1, weight=1) # Name entry takes available space
        add_item_lib_frame.columnconfigure(3, weight=0) # Price entry fixed width

        item_lib_buttons_frame = ttk.Frame(add_item_lib_frame)
        item_lib_buttons_frame.grid(row=2, column=0, columnspan=4, pady=(10,5))
        ttk.Button(item_lib_buttons_frame, text="Add Item", command=self.add_item_to_library).pack(side='left', padx=5)
        ttk.Button(item_lib_buttons_frame, text="Edit Selected", command=self.edit_library_item).pack(side='left', padx=5)
        ttk.Button(item_lib_buttons_frame, text="Delete Selected", command=self.delete_library_item).pack(side='left', padx=5)
        self.items_library_tree.bind('<Double-1>', lambda e: self.edit_library_item())

    def add_item_to_library(self):
        # ... (same as before, but ensure item selections are updated)
        name, desc = self.item_name_entry.get().strip(), self.item_desc_entry.get().strip()
        try: price = float(self.item_price_entry.get())
        except ValueError: messagebox.showerror("Error", "Valid price required."); return
        if not name or not desc: messagebox.showerror("Error", "Name/Desc required."); return
        if price < 0: messagebox.showerror("Error", "Price cannot be negative."); return
        item_id = self.generate_item_id()
        self.items.append({'id': item_id, 'name': name, 'description': desc, 'price': price})
        self.save_items(); self.update_items_list(); self.clear_item_entries()
        self.update_item_selection(); self.update_item_selection_quote()

    def edit_library_item(self):
        # ... (same as before, but ensure item selections are updated)
        selected = self.items_library_tree.selection()
        if not selected: messagebox.showerror("Error", "Select item to edit."); return
        item_id_from_tree = self.items_library_tree.item(selected[0], 'values')[0]
        item_to_edit = next((item for item in self.items if item['id'] == item_id_from_tree), None)
        if not item_to_edit: messagebox.showerror("Error", "Item not found."); return
        
        edit_win = tk.Toplevel(self.window); edit_win.title("Edit Library Item"); edit_win.geometry("450x200"); edit_win.transient(self.window); edit_win.grab_set()
        price_label_text = f"Price (ex {self.app_settings.get('tax_name', 'Tax')}):"
        
        # Apply theme to Toplevel
        theme_colors = DARK_THEME if self.app_settings.get('theme') == 'Dark' else LIGHT_THEME
        edit_win.configure(bg=theme_colors["bg"])

        entries = {}
        # Explicitly create ttk.Labels and ttk.Entry for theming
        l_name = ttk.Label(edit_win, text="Name:"); l_name.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        e_name = ttk.Entry(edit_win, width=40); e_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew"); e_name.insert(0, item_to_edit['name']); entries['name'] = e_name
        
        l_desc = ttk.Label(edit_win, text="Description:"); l_desc.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        e_desc = ttk.Entry(edit_win, width=40); e_desc.grid(row=1, column=1, padx=5, pady=5, sticky="ew"); e_desc.insert(0, item_to_edit['description']); entries['description'] = e_desc
        
        l_price = ttk.Label(edit_win, text=price_label_text); l_price.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        e_price = ttk.Entry(edit_win, width=15); e_price.grid(row=2, column=1, padx=5, pady=5, sticky="w"); e_price.insert(0, str(item_to_edit['price'])); entries['price'] = e_price # Key 'price'

        edit_win.columnconfigure(1, weight=1)
        
        def _save():
            name, desc = entries['name'].get().strip(), entries['description'].get().strip()
            try: price = float(entries['price'].get())
            except ValueError: messagebox.showerror("Error", "Valid price.", parent=edit_win); return
            if not name or not desc: messagebox.showerror("Error", "Name/Desc required.", parent=edit_win); return
            if price < 0: messagebox.showerror("Error", "Price >= 0.", parent=edit_win); return
            item_to_edit.update({'name': name, 'description': desc, 'price': price})
            self.save_items(); self.update_items_list()
            self.update_item_selection(); self.update_item_selection_quote()
            edit_win.destroy()
        
        save_button = ttk.Button(edit_win, text="Save Changes", command=_save)
        save_button.grid(row=3, column=0, columnspan=2, pady=10)


    def delete_library_item(self):
        # ... (same as before, but ensure item selections are updated)
        selected = self.items_library_tree.selection()
        if not selected: messagebox.showerror("Error", "Please select an item to delete!"); return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            item_id_from_tree = self.items_library_tree.item(selected[0], 'values')[0]
            self.items = [item for item in self.items if item['id'] != item_id_from_tree]
            self.save_items(); self.update_items_list()
            self.update_item_selection(); self.update_item_selection_quote()


    def clear_item_entries(self):
        self.item_name_entry.delete(0, tk.END); self.item_desc_entry.delete(0, tk.END); self.item_price_entry.delete(0, tk.END)

    def update_items_list(self): # Item library tree
        if not hasattr(self, 'items_library_tree'): return # UI not ready
        self.items_library_tree.delete(*self.items_library_tree.get_children())
        currency_symbol = self._get_currency_symbol()
        for item in self.items:
            self.items_library_tree.insert('', 'end', values=(
                item['id'], item['name'], item['description'], f"{currency_symbol}{item['price']:.2f}"
            ))

    def load_items(self):
        try:
            if os.path.exists(ITEMS_FILE):
                with open(ITEMS_FILE, 'r') as f: data = json.load(f)
                self.items = data.get('items', [])
                self.item_counter = data.get('counter', 0)
        except FileNotFoundError: self.items, self.item_counter = [], 0
        except json.JSONDecodeError: print(f"Error decoding {ITEMS_FILE}"); self.items, self.item_counter = [], 0


    def save_items(self):
        with open(ITEMS_FILE, 'w') as f: json.dump({'items': self.items, 'counter': self.item_counter}, f, indent=4)

    def generate_item_id(self):
        self.item_counter += 1; return f"ITEM{self.item_counter:04d}"


    def create_invoice_tab(self):
        # invoice_frame = ttk.Frame(self.notebook) # Already self.invoice_frame
        # self.notebook.add(invoice_frame, text='New Invoice')
        invoice_frame = self.invoice_frame
        
        client_frame_inv = ttk.LabelFrame(invoice_frame, text="Client Information")
        client_frame_inv.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky='nsew')
        ttk.Label(client_frame_inv, text="Select Client:").grid(row=0, column=0, padx=5, pady=3, sticky="w")
        self.client_var = tk.StringVar()
        self.client_dropdown = ttk.Combobox(client_frame_inv, textvariable=self.client_var, width=37, state="readonly")
        self.client_dropdown.grid(row=0, column=1, pady=3, sticky="ew")
        self.client_dropdown.bind('<<ComboboxSelected>>', self.on_client_selected)
        # self.update_client_dropdown() # Called in __init__
        
        ttk.Label(client_frame_inv, text="Client Name:").grid(row=1, column=0, padx=5, pady=3, sticky="w")
        self.client_name = ttk.Entry(client_frame_inv, width=40); self.client_name.grid(row=1, column=1, pady=3, sticky="ew")
        ttk.Label(client_frame_inv, text="Client Email:").grid(row=2, column=0, padx=5, pady=3, sticky="w")
        self.client_email = ttk.Entry(client_frame_inv, width=40); self.client_email.grid(row=2, column=1, pady=3, sticky="ew")
        ttk.Label(client_frame_inv, text="Client Address:").grid(row=3, column=0, padx=5, pady=3, sticky="w")
        self.client_address = ttk.Entry(client_frame_inv, width=40); self.client_address.grid(row=3, column=1, pady=3, sticky="ew")
        client_frame_inv.columnconfigure(1, weight=1)
        
        self.gst_var = tk.BooleanVar(value=self.app_settings.get('apply_tax_default', True))
        tax_label_text_inv = f"Include {self.app_settings.get('tax_name', 'Tax')} ({self.app_settings.get('tax_rate', 0.0):.1f}%)"
        self.gst_check_invoice = ttk.Checkbutton(client_frame_inv, text=tax_label_text_inv, variable=self.gst_var, command=self.update_total)
        self.gst_check_invoice.grid(row=4, column=0, columnspan=2, pady=3, sticky="w")
        
        items_section_inv = ttk.LabelFrame(invoice_frame, text="Items")
        items_section_inv.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky='nsew')
        
        tax_name_col_inv = self.app_settings.get('tax_name', 'Tax')
        price_ex_tax_col_inv = f"Price (ex {tax_name_col_inv})"
        self.items_tree = ttk.Treeview(items_section_inv, columns=('Item ID', 'Name', 'Description', 'Quantity', 'Price', 'GST', 'Total'), show='headings')
        col_data_inv = [('Item ID', 70, tk.NO), ('Name', 150, tk.YES), ('Description', 200, tk.YES), 
                        ('Quantity', 60, tk.NO), ('Price', 100, tk.NO), ('GST', 80, tk.NO), ('Total', 100, tk.NO)]
        col_map_inv = {'Price': price_ex_tax_col_inv, 'GST': tax_name_col_inv}
        for text, wid, stretch in col_data_inv: self.items_tree.heading(text, text=col_map_inv.get(text, text)); self.items_tree.column(text, width=wid, minwidth=50, stretch=stretch, anchor="w")
        self.items_tree.pack(pady=5, fill='both', expand=True)
        self.items_tree.bind('<Double-1>', self.edit_invoice_item)
        
        add_item_controls_inv = ttk.Frame(items_section_inv)
        add_item_controls_inv.pack(pady=5, fill='x')
        
        # Create a frame for the item selection
        item_selection_frame = ttk.LabelFrame(add_item_controls_inv, text="Add Item")
        item_selection_frame.pack(fill='x', padx=5, pady=5)
        
        # Add search label and entry
        ttk.Label(item_selection_frame, text="Search:").grid(row=0, column=0, padx=(5,0), pady=3, sticky="w")
        self.item_selection = SearchableCombobox(item_selection_frame, width=40)
        self.item_selection.grid(row=0, column=1, padx=5, pady=3, sticky="ew")
        
        # Add quantity controls
        quantity_frame = ttk.Frame(item_selection_frame)
        quantity_frame.grid(row=0, column=2, padx=(10,0), pady=3, sticky="e")
        ttk.Label(quantity_frame, text="Qty:").pack(side='left', padx=(0,5))
        self.item_quantity = ttk.Entry(quantity_frame, width=8)
        self.item_quantity.pack(side='left')
        self.item_quantity.insert(0, "1")
        
        # Add buttons in a separate frame
        item_buttons_inv = ttk.Frame(item_selection_frame)
        item_buttons_inv.grid(row=0, column=3, padx=(10,5), pady=3, sticky="e")
        
        # Style the buttons
        button_style = {'width': 8, 'padding': 5}
        ttk.Button(item_buttons_inv, text="Add", command=self.add_item, **button_style).pack(side='left', padx=2)
        ttk.Button(item_buttons_inv, text="New", command=self.create_new_item, **button_style).pack(side='left', padx=2)
        ttk.Button(item_buttons_inv, text="Edit", command=self.edit_invoice_item, **button_style).pack(side='left', padx=2)
        ttk.Button(item_buttons_inv, text="Del", command=self.remove_selected_item, **button_style).pack(side='left', padx=2)
        
        # Configure grid weights
        item_selection_frame.columnconfigure(1, weight=1)
        item_selection_frame.columnconfigure(3, weight=0)

        totals_display_inv = ttk.Frame(invoice_frame)
        totals_display_inv.grid(row=2, column=1, pady=10, padx=10, sticky='e')
        self.subtotal_label = ttk.Label(totals_display_inv, text=f"Subtotal: {self._get_currency_symbol()}0.00")
        self.subtotal_label.pack(pady=1, anchor="e")
        self.gst_label = ttk.Label(totals_display_inv, text=f"{self._get_tax_name()}: {self._get_currency_symbol()}0.00")
        self.gst_label.pack(pady=1, anchor="e")
        self.total_label = ttk.Label(totals_display_inv, text=f"Total: {self._get_currency_symbol()}0.00") # Font set in update_ui
        self.total_label.pack(pady=1, anchor="e")
        
        ttk.Button(invoice_frame, text="Generate Invoice", command=lambda: self.save_document('invoice')).grid(row=3, column=1, pady=(5,10), padx=10, sticky="e")
        invoice_frame.columnconfigure(0, weight=1); invoice_frame.columnconfigure(1, weight=1) # Allow client and totals to share space
        invoice_frame.rowconfigure(1, weight=1) # Allow items section to expand vertically


    def create_quote_tab(self):
        # quote_frame = ttk.Frame(self.notebook) # Already self.quote_frame
        # self.notebook.add(quote_frame, text='New Quote')
        quote_frame = self.quote_frame

        client_frame_quo = ttk.LabelFrame(quote_frame, text="Client/Prospect Information")
        client_frame_quo.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky='nsew')
        ttk.Label(client_frame_quo, text="Select:").grid(row=0, column=0, padx=5, pady=3, sticky="w")
        self.quote_client_var = tk.StringVar()
        self.quote_client_dropdown = ttk.Combobox(client_frame_quo, textvariable=self.quote_client_var, width=37, state="readonly")
        self.quote_client_dropdown.grid(row=0, column=1, pady=3, sticky="ew")
        self.quote_client_dropdown.bind('<<ComboboxSelected>>', self.on_quote_client_selected)
        # self.update_quote_client_dropdown() # Called in __init__
        
        ttk.Label(client_frame_quo, text="Name:").grid(row=1, column=0, padx=5, pady=3, sticky="w")
        self.quote_client_name = ttk.Entry(client_frame_quo, width=40); self.quote_client_name.grid(row=1, column=1, pady=3, sticky="ew")
        ttk.Label(client_frame_quo, text="Email:").grid(row=2, column=0, padx=5, pady=3, sticky="w")
        self.quote_client_email = ttk.Entry(client_frame_quo, width=40); self.quote_client_email.grid(row=2, column=1, pady=3, sticky="ew")
        ttk.Label(client_frame_quo, text="Address:").grid(row=3, column=0, padx=5, pady=3, sticky="w")
        self.quote_client_address = ttk.Entry(client_frame_quo, width=40); self.quote_client_address.grid(row=3, column=1, pady=3, sticky="ew")
        client_frame_quo.columnconfigure(1, weight=1)

        self.gst_var_quote = tk.BooleanVar(value=self.app_settings.get('apply_tax_default', True))
        tax_label_text_quo = f"Include {self.app_settings.get('tax_name', 'Tax')} ({self.app_settings.get('tax_rate', 0.0):.1f}%)"
        self.gst_check_quote = ttk.Checkbutton(client_frame_quo, text=tax_label_text_quo, variable=self.gst_var_quote, command=self.update_total_quote)
        self.gst_check_quote.grid(row=4, column=0, columnspan=2, pady=3, sticky="w")

        items_section_quo = ttk.LabelFrame(quote_frame, text="Items")
        items_section_quo.grid(row=1, column=0, columnspan=2, pady=10, padx=10, sticky='nsew')
        
        tax_name_col_quo = self.app_settings.get('tax_name', 'Tax')
        price_ex_tax_col_quo = f"Price (ex {tax_name_col_quo})"
        self.quote_items_tree = ttk.Treeview(items_section_quo, columns=('Item ID', 'Name', 'Description', 'Quantity', 'Price', 'GST', 'Total'), show='headings')
        col_data_quo = [('Item ID', 70, tk.NO), ('Name', 150, tk.YES), ('Description', 200, tk.YES), 
                        ('Quantity', 60, tk.NO), ('Price', 100, tk.NO), ('GST', 80, tk.NO), ('Total', 100, tk.NO)]
        col_map_quo = {'Price': price_ex_tax_col_quo, 'GST': tax_name_col_quo}
        for text, wid, stretch in col_data_quo: self.quote_items_tree.heading(text, text=col_map_quo.get(text, text)); self.quote_items_tree.column(text, width=wid, minwidth=50, stretch=stretch, anchor="w")
        self.quote_items_tree.pack(pady=5, fill='both', expand=True)
        self.quote_items_tree.bind('<Double-1>', self.edit_quote_item)
        
        add_item_controls_quo = ttk.Frame(items_section_quo)
        add_item_controls_quo.pack(pady=5, fill='x')
        
        # Create a frame for the item selection
        item_selection_frame = ttk.LabelFrame(add_item_controls_quo, text="Add Item")
        item_selection_frame.pack(fill='x', padx=5, pady=5)
        
        # Add search label and entry
        ttk.Label(item_selection_frame, text="Search:").grid(row=0, column=0, padx=(5,0), pady=3, sticky="w")
        self.item_selection_quote = SearchableCombobox(item_selection_frame, width=40)
        self.item_selection_quote.grid(row=0, column=1, padx=5, pady=3, sticky="ew")
        
        # Add quantity controls
        quantity_frame = ttk.Frame(item_selection_frame)
        quantity_frame.grid(row=0, column=2, padx=(10,0), pady=3, sticky="e")
        ttk.Label(quantity_frame, text="Qty:").pack(side='left', padx=(0,5))
        self.item_quantity_quote = ttk.Entry(quantity_frame, width=8)
        self.item_quantity_quote.pack(side='left')
        self.item_quantity_quote.insert(0, "1")
        
        # Add buttons in a separate frame
        item_buttons_quo = ttk.Frame(item_selection_frame)
        item_buttons_quo.grid(row=0, column=3, padx=(10,5), pady=3, sticky="e")
        
        # Style the buttons
        button_style = {'width': 8, 'padding': 5}
        ttk.Button(item_buttons_quo, text="Add", command=self.add_item_quote, **button_style).pack(side='left', padx=2)
        ttk.Button(item_buttons_quo, text="New", command=self.create_new_item, **button_style).pack(side='left', padx=2)
        ttk.Button(item_buttons_quo, text="Edit", command=self.edit_quote_item, **button_style).pack(side='left', padx=2)
        ttk.Button(item_buttons_quo, text="Del", command=self.remove_selected_item_quote, **button_style).pack(side='left', padx=2)
        
        # Configure grid weights
        item_selection_frame.columnconfigure(1, weight=1)
        item_selection_frame.columnconfigure(3, weight=0)

        totals_display_quo = ttk.Frame(quote_frame)
        totals_display_quo.grid(row=2, column=1, pady=10, padx=10, sticky='e')
        self.subtotal_label_quote = ttk.Label(totals_display_quo, text=f"Subtotal: {self._get_currency_symbol()}0.00")
        self.subtotal_label_quote.pack(pady=1, anchor="e")
        self.gst_label_quote = ttk.Label(totals_display_quo, text=f"{self._get_tax_name()}: {self._get_currency_symbol()}0.00")
        self.gst_label_quote.pack(pady=1, anchor="e")
        self.total_label_quote = ttk.Label(totals_display_quo, text=f"Total: {self._get_currency_symbol()}0.00") # Font set in update_ui
        self.total_label_quote.pack(pady=1, anchor="e")
        
        ttk.Button(quote_frame, text="Generate Quote", command=lambda: self.save_document('quote')).grid(row=3, column=1, pady=(5,10), padx=10, sticky="e")
        quote_frame.columnconfigure(0, weight=1); quote_frame.columnconfigure(1, weight=1)
        quote_frame.rowconfigure(1, weight=1)


    def create_history_tab(self):
        # history_frame_tab = ttk.Frame(self.notebook) # Already self.history_frame_tab
        # self.notebook.add(history_frame_tab, text='History')
        history_frame_tab = self.history_frame_tab

        self.history_tree = ttk.Treeview(history_frame_tab, columns=('Date', 'Type', 'Client', 'Total', 'PDF Path'), show='headings')
        for col_name in ('Date', 'Type', 'Client', 'Total', 'PDF Path'):
            self.history_tree.heading(col_name, text=col_name)
            sw = self.window.winfo_screenwidth()
            col_width = int(sw * 0.15) if col_name != 'PDF Path' else int(sw * 0.30) # PDF Path wider
            self.history_tree.column(col_name, width=col_width, minwidth=80, stretch=tk.YES)
        self.history_tree.pack(expand=True, fill='both', padx=10, pady=(10,5))
        ttk.Button(history_frame_tab, text="Open Selected PDF", command=self.open_selected_pdf).pack(pady=(5,10))
        # self.update_history_display() # Called in __init__


    def _get_current_tax_rate_decimal(self):
        return self.app_settings.get('tax_rate', 0.0) / 100.0

    def _get_currency_symbol(self):
        return self.business_details.get('currency_symbol', '$')

    def _get_tax_name(self):
        return self.app_settings.get('tax_name', 'Tax')

    def add_item_logic(self, item_selection_widget, item_quantity_widget, treeview_widget, apply_tax_var, update_total_func):
        # ... (same as before)
        try:
            selected_item_str = item_selection_widget.get()
            if not selected_item_str: messagebox.showerror("Error", "Please select an item!"); return
            item_id = selected_item_str.split(' - ')[0]
            item_info = next((i for i in self.items if i['id'] == item_id), None)
            if not item_info: messagebox.showerror("Error", "Selected item not found!"); return
            qty_str = item_quantity_widget.get()
            if not qty_str: messagebox.showerror("Error", "Please enter quantity!"); return
            qty = float(qty_str)
            if qty <= 0: messagebox.showerror("Error", "Quantity must be > 0!"); return

            price_ex_tax = item_info['price']
            tax_amount = price_ex_tax * qty * self._get_current_tax_rate_decimal() if apply_tax_var.get() else 0
            total_inc_tax = (price_ex_tax * qty) + tax_amount
            currency_sym = self._get_currency_symbol()
            treeview_widget.insert('', 'end', values=(
                item_info['id'], item_info['name'], item_info['description'], f"{qty:.2f}",
                f"{currency_sym}{price_ex_tax:.2f}", f"{currency_sym}{tax_amount:.2f}", f"{currency_sym}{total_inc_tax:.2f}"
            ))
            update_total_func()
            item_quantity_widget.delete(0, tk.END); item_quantity_widget.insert(0,"1")
            item_selection_widget.set('')
        except ValueError: messagebox.showerror("Error", "Valid quantity required.")
        except Exception as e: messagebox.showerror("Error", f"Unexpected error: {e}")


    def add_item(self): self.add_item_logic(self.item_selection, self.item_quantity, self.items_tree, self.gst_var, self.update_total)
    def add_item_quote(self): self.add_item_logic(self.item_selection_quote, self.item_quantity_quote, self.quote_items_tree, self.gst_var_quote, self.update_total_quote)

    def remove_selected_item(self):
        if self.items_tree.selection(): self.items_tree.delete(self.items_tree.selection()[0]); self.update_total()
    def remove_selected_item_quote(self):
        if self.quote_items_tree.selection(): self.quote_items_tree.delete(self.quote_items_tree.selection()[0]); self.update_total_quote()
    
    def update_total_generic(self, treeview, subtotal_label_widget, tax_label_widget, total_label_widget, tax_var_for_doc):
        # ... (ensure font is applied to total_label_widget if needed, or handle in update_ui_for_app_settings)
        subtotal, tax_total_for_doc = 0, 0
        currency_sym = self._get_currency_symbol()
        current_tax_rate_decimal = self._get_current_tax_rate_decimal()
        for item_row_id in treeview.get_children():
            values = treeview.item(item_row_id, 'values')
            try:
                price_str = values[4].replace(currency_sym, '')
                item_price_ex_tax = float(price_str)
                item_qty = float(values[3])
            except (IndexError, ValueError) as e:
                print(f"Error parsing tree values: {values} - {e}"); continue 
            line_subtotal = item_price_ex_tax * item_qty
            subtotal += line_subtotal
            if tax_var_for_doc.get(): tax_total_for_doc += line_subtotal * current_tax_rate_decimal
        total_amount = subtotal + tax_total_for_doc
        subtotal_label_widget.config(text=f"Subtotal: {currency_sym}{subtotal:.2f}")
        tax_label_widget.config(text=f"{self._get_tax_name()}: {currency_sym}{tax_total_for_doc:.2f}")
        
        font_size = int(self.app_settings.get('font_size', 12))
        total_label_widget.config(text=f"Total: {currency_sym}{total_amount:.2f}", font=('Helvetica', font_size + 2, 'bold')) # Apply bold here too


    def update_total(self): self.update_total_generic(self.items_tree, self.subtotal_label, self.gst_label, self.total_label, self.gst_var)
    def update_total_quote(self): self.update_total_generic(self.quote_items_tree, self.subtotal_label_quote, self.gst_label_quote, self.total_label_quote, self.gst_var_quote)

    def generate_pdf(self, data, doc_type):
        # ... (same as before, but ensure it uses _get_tax_name() and _get_currency_symbol() for PDF content)
        pdf_file = f"{doc_type.capitalize()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf" # underscore in time
        doc = SimpleDocTemplate(pdf_file, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm, leftMargin=1.5*cm, rightMargin=1.5*cm)
        story = []
        styles = getSampleStyleSheet()
        font_size_pdf = 10 # Base font size for PDF
        
        # PDF Styles
        title_style = ParagraphStyle('PdfTitle', parent=styles['h1'], fontSize=18, spaceAfter=0.8*cm, alignment=1, textColor=colors.HexColor("#002b36"))
        heading_style = ParagraphStyle('PdfHeading', parent=styles['h2'], fontSize=font_size_pdf + 2, spaceBefore=0.4*cm, spaceAfter=0.15*cm, textColor=colors.HexColor("#268bd2"))
        normal_style = ParagraphStyle('PdfNormal', parent=styles['Normal'], fontSize=font_size_pdf, leading=font_size_pdf+2)
        normal_bold_style = ParagraphStyle('PdfNormalBold', parent=normal_style, fontName='Helvetica-Bold')
        table_header_style = ParagraphStyle('PdfTableHeader', parent=normal_bold_style, alignment=1, textColor=colors.whitesmoke)
        table_cell_style = ParagraphStyle('PdfTableCell', parent=normal_style, alignment=0) # Left default
        table_cell_right_style = ParagraphStyle('PdfTableCellRight', parent=table_cell_style, alignment=2) # Right

        # --- Header ---
        story.append(Paragraph(f"{self.business_details.get('name', 'Your Business Name')}", title_style)) # Use title style for business name
        story.append(Paragraph(f"{self.business_details.get('address', 'Your Address')}", normal_style))
        if self.business_details.get('phone'): story.append(Paragraph(f"Phone: {self.business_details['phone']}", normal_style))
        if self.business_details.get('email'): story.append(Paragraph(f"Email: {self.business_details['email']}", normal_style))
        tax_id_label_pdf = DEFAULT_COUNTRY_DATA.get(self.app_settings.get('selected_country'), {}).get('tax_id_label', 'Tax ID')
        tax_id_value_pdf = self.business_details.get('tax_identifier_value', '')
        if tax_id_value_pdf: story.append(Paragraph(f"{tax_id_label_pdf}: {tax_id_value_pdf}", normal_style))
        story.append(Spacer(1, 0.8*cm))

        story.append(Paragraph(f"<b>{doc_type.capitalize()}</b>", ParagraphStyle('DocTypeTitle', fontSize=16, alignment=0, spaceAfter=0.2*cm)))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%d %B %Y')}", normal_style))
        story.append(Spacer(1, 0.5*cm))

        story.append(Paragraph("Bill To:", heading_style))
        story.append(Paragraph(f"{data['client_name']}", normal_bold_style))
        story.append(Paragraph(f"{data['client_address']}", normal_style))
        story.append(Paragraph(f"{data['client_email']}", normal_style))
        story.append(Spacer(1, 0.8*cm))

        currency_sym_pdf = self._get_currency_symbol()
        tax_name_pdf = self._get_tax_name()
        item_data_for_pdf = [[
            Paragraph("Description", table_header_style), Paragraph("Qty", table_header_style),
            Paragraph(f"Unit Price ({currency_sym_pdf})", table_header_style),
            Paragraph(f"{tax_name_pdf} ({currency_sym_pdf})", table_header_style),
            Paragraph(f"Total ({currency_sym_pdf})", table_header_style)
        ]]
        for item_values in data['items']: # item_id, name, description, qty, price_str, tax_str, total_str
            desc_text = f"<b>{item_values[1]}</b><br/><font size='{font_size_pdf-1}'>{item_values[2]}</font>"
            item_data_for_pdf.append([
                Paragraph(desc_text, table_cell_style), Paragraph(str(item_values[3]), table_cell_right_style),
                Paragraph(item_values[4].replace(currency_sym_pdf, ''), table_cell_right_style),
                Paragraph(item_values[5].replace(currency_sym_pdf, ''), table_cell_right_style),
                Paragraph(item_values[6].replace(currency_sym_pdf, ''), table_cell_right_style)
            ])

        page_width = A4[0] - 3*cm # margins
        col_widths = [page_width*0.40, page_width*0.10, page_width*0.18, page_width*0.12, page_width*0.20]
        
        table = Table(item_data_for_pdf, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#268bd2")), # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'), # Header text center
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),   # Description left
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'), # Other columns right
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.5*cm))

        totals_style_right = ParagraphStyle('TotalsRight', parent=normal_style, alignment=2)
        totals_bold_style_right = ParagraphStyle('TotalsBoldRight', parent=normal_bold_style, alignment=2)
        story.append(Paragraph(f"Subtotal: {currency_sym_pdf}{data['subtotal']}", totals_style_right))
        story.append(Paragraph(f"{tax_name_pdf}: {currency_sym_pdf}{data['tax']}", totals_style_right))
        story.append(Paragraph(f"<b>Total: {currency_sym_pdf}{data['total']}</b>", ParagraphStyle('TotalAmountPdf', parent=totals_bold_style_right, fontSize=font_size_pdf+2)))
        story.append(Spacer(1, 0.8*cm))

        if doc_type == 'invoice':
            story.append(Paragraph("Payment Details:", heading_style))
            if self.business_details.get('bank'): story.append(Paragraph(f"Bank: {self.business_details['bank']}", normal_style))
            if self.business_details.get('bsb'): story.append(Paragraph(f"BSB: {self.business_details['bsb']}", normal_style))
            if self.business_details.get('account'): story.append(Paragraph(f"Account No: {self.business_details['account']}", normal_style))
            story.append(Spacer(1, 0.5*cm))
        if self.business_details.get('invoice_terms'):
            story.append(Paragraph("Terms & Conditions:", heading_style))
            story.append(Paragraph(self.business_details['invoice_terms'].replace('\n', '<br/>\n'), normal_style))
        try: doc.build(story); return pdf_file
        except Exception as e: messagebox.showerror("PDF Error", f"Failed: {e}"); return None


    def save_document(self, doc_type):
        # ... (same as before)
        items_list_for_pdf = []
        tree = self.items_tree if doc_type == 'invoice' else self.quote_items_tree
        client_name_widget = self.client_name if doc_type == 'invoice' else self.quote_client_name
        client_email_widget = self.client_email if doc_type == 'invoice' else self.quote_client_email
        client_address_widget = self.client_address if doc_type == 'invoice' else self.quote_client_address
        tax_var_for_doc = self.gst_var if doc_type == 'invoice' else self.gst_var_quote

        if not client_name_widget.get(): messagebox.showerror("Error", "Client Name is required."); return

        subtotal_val, tax_val = 0, 0
        currency_sym = self._get_currency_symbol()
        current_tax_rate_decimal = self._get_current_tax_rate_decimal()

        for item_row_id in tree.get_children():
            values = list(tree.item(item_row_id, 'values')) # Make a mutable copy
            items_list_for_pdf.append(values)
            try:
                price_ex_tax_numeric = float(values[4].replace(currency_sym, ''))
                qty_numeric = float(values[3])
            except (IndexError, ValueError) as e:
                print(f"Error parsing values for PDF total: {values} - {e}"); continue
            line_subtotal = price_ex_tax_numeric * qty_numeric
            subtotal_val += line_subtotal
            if tax_var_for_doc.get(): tax_val += line_subtotal * current_tax_rate_decimal
        total_val = subtotal_val + tax_val

        data_for_pdf = {
            'client_name': client_name_widget.get(), 'client_email': client_email_widget.get(),
            'client_address': client_address_widget.get(), 'items': items_list_for_pdf,
            'subtotal': f"{subtotal_val:.2f}", 'tax': f"{tax_val:.2f}", 'total': f"{total_val:.2f}"
        }
        pdf_file = self.generate_pdf(data_for_pdf, doc_type)
        if pdf_file:
            messagebox.showinfo("PDF Generated", f"{doc_type.capitalize()} PDF: {pdf_file}.")
            history_entry = {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M'), 'type': doc_type.capitalize(),
                'client': client_name_widget.get(), 'total': f"{currency_sym}{total_val:.2f}",
                'pdf_path': os.path.abspath(pdf_file)
            }
            self.add_to_history(history_entry) # This calls save_history_data
            self.update_history_display()


    def add_to_history(self, entry):
        self.history_records.append(entry)
        self.save_history_data()

    def load_history_data(self):
        try:
            if os.path.exists(HISTORY_DATA_FILE):
                with open(HISTORY_DATA_FILE, 'r') as f: self.history_records = json.load(f)
            else: self.history_records = []
        except Exception as e: print(f"Error loading history: {e}"); self.history_records = []

    def save_history_data(self):
        try:
            with open(HISTORY_DATA_FILE, 'w') as f: json.dump(self.history_records, f, indent=4)
        except Exception as e: print(f"Error saving history: {e}")

    def update_history_display(self):
        if not hasattr(self, 'history_tree'): return
        self.history_tree.delete(*self.history_tree.get_children())
        for entry in reversed(self.history_records): # Newest first
            self.history_tree.insert('', 'end', values=(
                entry['date'], entry['type'], entry['client'], entry['total'], entry['pdf_path']
            ))

    def open_selected_pdf(self):
        # ... (same as before)
        selected = self.history_tree.selection()
        if selected:
            pdf_file_path = self.history_tree.item(selected[0], 'values')[4]
            if os.path.exists(pdf_file_path):
                try:
                    if sys.platform == "win32": os.startfile(pdf_file_path)
                    elif sys.platform == "darwin": os.system(f'open "{pdf_file_path}"')
                    else: os.system(f'xdg-open "{pdf_file_path}"')
                except Exception as e: messagebox.showerror("Error", f"Could not open: {e}\n{pdf_file_path}")
            else: messagebox.showerror("Error", f"Not found: {pdf_file_path}")

    def update_client_dropdown(self):
        if hasattr(self, 'client_dropdown'):
            self.client_dropdown['values'] = sorted([c['name'] for c in self.clients])
            self.client_var.set('')

    def update_quote_client_dropdown(self):
        if hasattr(self, 'quote_client_dropdown'):
            all_contacts = [c['name'] for c in self.clients] + [p['name'] for p in self.prospects]
            self.quote_client_dropdown['values'] = sorted(list(set(all_contacts)))
            self.quote_client_var.set('')

    def on_client_selected(self, event):
        # ... (same as before)
        name = self.client_var.get()
        client = next((c for c in self.clients if c['name'] == name), None)
        if client:
            self.client_name.delete(0, tk.END); self.client_name.insert(0, client['name'])
            self.client_email.delete(0, tk.END); self.client_email.insert(0, client['email'])
            self.client_address.delete(0, tk.END); self.client_address.insert(0, client['address'])


    def on_quote_client_selected(self, event):
        # ... (same as before)
        name = self.quote_client_var.get()
        contact = next((c for c in self.clients if c['name'] == name), None) or \
                  next((p for p in self.prospects if p['name'] == name), None)
        if contact:
            self.quote_client_name.delete(0, tk.END); self.quote_client_name.insert(0, contact['name'])
            self.quote_client_email.delete(0, tk.END); self.quote_client_email.insert(0, contact['email'])
            self.quote_client_address.delete(0, tk.END); self.quote_client_address.insert(0, contact['address'])


    def edit_item_in_doc_tree(self, tree, apply_tax_var, update_total_func):
        # ... (same as before)
        selected = tree.selection()
        if not selected: messagebox.showerror("Error", "Select item to edit quantity."); return
        values = tree.item(selected[0], 'values')
        item_id, item_name, item_desc, current_qty_str = values[0], values[1], values[2], values[3]
        edit_win = tk.Toplevel(self.window); edit_win.title("Edit Item Quantity"); edit_win.geometry("350x150"); edit_win.transient(self.window); edit_win.grab_set()
        
        theme_colors = DARK_THEME if self.app_settings.get('theme') == 'Dark' else LIGHT_THEME
        edit_win.configure(bg=theme_colors["bg"])

        ttk.Label(edit_win, text=f"Item: {item_name[:30]}...").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        ttk.Label(edit_win, text="New Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        qty_entry = ttk.Entry(edit_win, width=10); qty_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w"); qty_entry.insert(0, current_qty_str); qty_entry.select_range(0, tk.END); qty_entry.focus_set()
        def _save():
            try:
                new_qty = float(qty_entry.get())
                if new_qty <= 0: messagebox.showerror("Error", "Quantity must be > 0!", parent=edit_win); return
                original_item_info = next((i for i in self.items if i['id'] == item_id), None)
                if not original_item_info: messagebox.showerror("Error", "Base item not in library!", parent=edit_win); return
                price_ex_tax = original_item_info['price']
                tax_amount = price_ex_tax * new_qty * self._get_current_tax_rate_decimal() if apply_tax_var.get() else 0
                total_inc_tax = (price_ex_tax * new_qty) + tax_amount
                currency_sym = self._get_currency_symbol()
                tree.item(selected[0], values=(
                    item_id, item_name, item_desc, f"{new_qty:.2f}", f"{currency_sym}{price_ex_tax:.2f}",
                    f"{currency_sym}{tax_amount:.2f}", f"{currency_sym}{total_inc_tax:.2f}"
                ))
                update_total_func(); edit_win.destroy()
            except ValueError: messagebox.showerror("Error", "Valid quantity required!", parent=edit_win)
        ttk.Button(edit_win, text="Save Changes", command=_save).grid(row=2, column=0, columnspan=2, pady=10)


    def edit_invoice_item(self, event=None): self.edit_item_in_doc_tree(self.items_tree, self.gst_var, self.update_total)
    def edit_quote_item(self, event=None): self.edit_item_in_doc_tree(self.quote_items_tree, self.gst_var_quote, self.update_total_quote)

    def update_item_selection(self):
        if hasattr(self, 'item_selection'):
            items = sorted([f"{i['id']} - {i['name']}" for i in self.items])
            self.item_selection.configure(values=items)
            self.item_selection.set('')

    def update_item_selection_quote(self):
        if hasattr(self, 'item_selection_quote'):
            items = sorted([f"{i['id']} - {i['name']}" for i in self.items])
            self.item_selection_quote.configure(values=items)
            self.item_selection_quote.set('')

    def create_new_item(self): # Modal for creating a library item
        # ... (Ensure theme is applied to this Toplevel and its widgets)
        edit_win = tk.Toplevel(self.window); edit_win.title("Create New Library Item"); edit_win.geometry("450x230"); edit_win.transient(self.window); edit_win.grab_set()
        
        theme_colors = DARK_THEME if self.app_settings.get('theme') == 'Dark' else LIGHT_THEME
        edit_win.configure(bg=theme_colors["bg"])

        ttk.Label(edit_win, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = ttk.Entry(edit_win, width=40); name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(edit_win, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        desc_entry = ttk.Entry(edit_win, width=40); desc_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        price_label_text = f"Price (ex {self.app_settings.get('tax_name', 'Tax')}):"
        ttk.Label(edit_win, text=price_label_text).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        price_entry = ttk.Entry(edit_win, width=15); price_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w") # Align left
        name_entry.focus_set()
        edit_win.columnconfigure(1, weight=1)

        def _save_new_lib_item():
            name, desc = name_entry.get().strip(), desc_entry.get().strip()
            try: price = float(price_entry.get())
            except ValueError: messagebox.showerror("Error", "Valid price required!", parent=edit_win); return
            if not name or not desc: messagebox.showerror("Error", "Name/Desc required!", parent=edit_win); return
            if price < 0: messagebox.showerror("Error", "Price >= 0!", parent=edit_win); return
            item_id = self.generate_item_id()
            self.items.append({'id': item_id, 'name': name, 'description': desc, 'price': price})
            self.save_items(); self.update_items_list()
            self.update_item_selection(); self.update_item_selection_quote()
            edit_win.destroy()
        
        btn_frame_new_item = ttk.Frame(edit_win)
        btn_frame_new_item.grid(row=3, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame_new_item, text="Save Item", command=_save_new_lib_item).pack(side='left', padx=5)
        ttk.Button(btn_frame_new_item, text="Cancel", command=edit_win.destroy).pack(side='left', padx=5)

    def create_help_tab(self):
        frame = self.help_frame
        self.main_heading_help = ttk.Label(frame, text="Megabooks Help Guide")
        self.main_heading_help.grid(row=0, column=0, columnspan=2, pady=(10,15), padx=5)

        # Create a text widget with scrollbar for help content
        help_text_frame = ttk.Frame(frame)
        help_text_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky='nsew')
        
        scrollbar = ttk.Scrollbar(help_text_frame)
        scrollbar.pack(side='right', fill='y')
        
        help_text = tk.Text(help_text_frame, wrap='word', yscrollcommand=scrollbar.set, 
                           padx=10, pady=10, font=('Helvetica', 11))
        help_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=help_text.yview)
        
        # Help content
        help_content = """
Getting Started with Megabooks

1. App Settings (First Tab)
   - Set your country and tax preferences
   - Choose between Light and Dark theme
   - Adjust font size for better readability
   - Save your preferences

2. Business Details
   - Enter your business information
   - Add payment details
   - Set invoice terms
   - Save your business details

3. Clients & Prospects
   - Add new clients and prospects
   - Convert prospects to clients
   - Edit or delete existing contacts
   - Double-click to edit entries

4. Items Library
   - Create a catalog of your products/services
   - Add descriptions and prices
   - Edit or delete items
   - Double-click to edit entries

5. Creating Invoices
   - Select a client from your list
   - Add items from your library
   - Adjust quantities as needed
   - Generate PDF invoice

6. Creating Quotes
   - Select a client or prospect
   - Add items from your library
   - Adjust quantities as needed
   - Generate PDF quote

7. History
   - View all generated documents
   - Open PDFs directly
   - Track your invoicing history

Tips:
- Use the search feature in item selection to quickly find items
- Double-click items in lists to edit them
- Save your settings after making changes
- Check the tax settings before creating new documents
- Use the "New" button to create items on the fly while creating invoices/quotes

For any issues or questions, please create a ticket on GitHub.
"""
        help_text.insert('1.0', help_content)
        help_text.config(state='disabled')  # Make read-only
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = InvoiceSystem()
    app.run()