# Invoice & Quote Generator

A desktop application built with Python and Tkinter to help users create and manage professional invoices and quotes, manage clients/prospects, and maintain an item library.

## Features

*   **Business Details Management:**
    *   Store and save essential business information (name, address, contact details, ABN, bank details).
    *   Configure company logo path (for future PDF integration).
    *   Set default invoice terms and currency symbol.
    *   Reset business details to default.
    *   Tooltips for guidance on input fields.
    *   Basic email and phone number validation.
    *   Country-specific tax settings (GST, VAT, Sales Tax) with automatic currency symbol and tax rate updates.
*   **Client & Prospect Management:**
    *   Add, edit, and delete clients and prospects.
    *   Maintain separate lists for active clients and potential prospects.
    *   Convert prospects to clients with a single click.
    *   Quickly populate client details when creating new invoices/quotes.
    *   Advanced searchable combobox for client selection with keyboard navigation.
*   **Item Library Management:**
    *   Create a library of reusable items or services.
    *   Store item ID (auto-generated), name, description, and price (excluding GST).
    *   Add, edit, and delete items from the library.
    *   Quick item search and selection with keyboard navigation.
*   **Invoice Generation:**
    *   Select clients from the managed list.
    *   Add items from the library or create new items on-the-fly for the current invoice.
    *   Specify quantities for each item.
    *   Edit item quantities directly within the invoice item list.
    *   Option to include/exclude GST (10%) on invoices.
    *   Automatic calculation of subtotal, GST, and total amount.
    *   Generate professional PDF invoices.
    *   Country-specific tax calculations and currency formatting.
*   **Quote Generation:**
    *   Select clients or prospects.
    *   Functionality similar to invoice generation for creating quotes.
    *   Add items from the library or create new items on-the-fly.
    *   Generate professional PDF quotes.
    *   Country-specific tax calculations and currency formatting.
*   **History:**
    *   View a list of generated invoices and quotes.
    *   Open generated PDF documents directly from the history (platform-dependent).
    *   Persistent storage of document history.
*   **User Interface:**
    *   Modern look and feel with `ttk` themed widgets.
    *   Tabbed interface for easy navigation between sections.
    *   Responsive window sizing.
    *   Dark and Light theme support with professional color schemes.
    *   Improved keyboard navigation throughout the application.
    *   Searchable dropdowns with filtering capabilities.
*   **Data Persistence:**
    *   Business details are saved in `business_details.json`.
    *   Client and prospect data is saved in `clients_prospects.json`.
    *   Item library is saved in `items.json`.
    *   Invoice/Quote history data is saved in `data.json`.
    *   Application settings are saved in `app_config.json`.
    *   Generated PDFs are saved locally.
*   **Settings:**
    *   Theme selection (Dark/Light mode).
    *   Country-specific tax and currency settings.
    *   Persistent application preferences.

## Prerequisites

*   Python 3.x
*   Tkinter (usually included with Python standard library)
*   ReportLab library

## Installation

1.  **Clone the repository (or download the script):**
    ```bash
    # If you have git installed
    # git clone https://github.com/ExoFi-Labs/Megabooks.git
    # cd Megabooks
    ```
    Otherwise, just save the Python script (`megabooks.py`) to a directory.

2.  **Install required Python packages:**
    Open your terminal or command prompt and run:
    ```bash
    pip install reportlab
    ```

## How to Run

1.  Navigate to the directory where you saved the Python script.
2.  Run the application using Python:
    ```bash
    python megabooks.py
    ```
    
## Usage Guide

1.  **Business Details:**
    *   Go to the "Business Details" tab.
    *   Fill in your company's information.
    *   Click "Save Business Details". This information will be used in your generated PDFs.
2.  **Clients & Prospects:**
    *   Go to the "Clients & Prospects" tab.
    *   Use the form to add new clients or prospects.
    *   Select an entry and click "Edit Selected" to modify details, or "Delete Selected" to remove.
    *   To convert a prospect to a client, select a prospect from the "Prospects" list and click "Convert to Client".
3.  **Items:**
    *   Go to the "Items" tab.
    *   Add your products or services with their name, description, and price (ex-GST).
    *   These items will be available for quick selection when creating invoices or quotes.
4.  **Creating a New Invoice:**
    *   Go to the "New Invoice" tab.
    *   Select a client from the "Select Client" dropdown. Their details will auto-fill.
    *   Choose whether to include GST using the checkbox.
    *   In the "Items" section:
        *   Select an item from the "Select Item" dropdown.
        *   Enter the "Quantity".
        *   Click "Add Item".
        *   To add an item not in your library, click "New Item", fill in the details, save it (this adds it to your main item library), and then add it to the invoice.
        *   To edit the quantity of an item already in the invoice list, double-click it or select it and click "Edit Selected".
        *   To remove an item, select it from the list and click "Remove Selected".
    *   The subtotal, GST (if applicable), and total will update automatically.
    *   Click "Generate Invoice" to create a PDF.
5.  **Creating a New Quote:**
    *   Go to the "New Quote" tab.
    *   The process is similar to creating an invoice. You can select either a client or a prospect.
    *   Click "Generate Quote" to create a PDF.
6.  **History:**
    *   Go to the "History" tab to see a list of previously generated documents.
    *   Select a document and click "Open Selected PDF" to view it (requires a default PDF viewer). *Note: History data is currently basic.*
7.  **Settings:**
    *   The "Settings" tab is currently a placeholder for future UI customization options like theme and font size selection.

## Data Storage

The application saves data locally in JSON files in the same directory as the script:

*   `business_details.json`: Stores your business information.
*   `clients_prospects.json`: Stores client and prospect lists.
*   `items.json`: Stores your item library.
*   `data.json`: (Intended for storing historical invoice/quote records - currently not fully utilized for loading history dynamically).
*   PDFs: Generated invoices and quotes are saved as `.pdf` files in the application's root directory, named with a timestamp (e.g., `Invoice_YYYYMMDDHHMMSS.pdf`).

## Future Enhancements (Ideas)

*   Fully implement the "Settings" tab for theme and font customization.
*   Robust history management with searching, filtering, and persistent storage.
*   Integration of company logo into PDF documents.
*   Option to email generated PDFs directly from the application.
*   More advanced reporting features.
*   Backup and restore functionality for JSON data files.
*   Option for different PDF templates.

---

