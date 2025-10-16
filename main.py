import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
from bank import BankAccount
import database as db

# ==================== MODERN STYLING ====================
COLORS = {
    'primary': '#2C3E50',  # Dark blue-gray
    'secondary': '#3498DB',  # Bright blue
    'success': '#27AE60',  # Green
    'danger': '#E74C3C',  # Red
    'warning': '#F39C12',  # Orange
    'light': '#ECF0F1',  # Light gray
    'white': '#FFFFFF',
    'dark': '#1A252F',
    'accent': '#9B59B6',  # Purple
    'bg': '#F5F7FA',  # Light background
    'card': '#FFFFFF',
    'border': '#BDC3C7',
    'text': '#2C3E50',
    'text_light': '#7F8C8D'
}

FONTS = {
    'title': ('Segoe UI', 24, 'bold'),
    'heading': ('Segoe UI', 16, 'bold'),
    'subheading': ('Segoe UI', 12, 'bold'),
    'body': ('Segoe UI', 10),
    'small': ('Segoe UI', 9),
    'button': ('Segoe UI', 10, 'bold')
}

# ==================== MAIN WINDOW ====================
root = tk.Tk()
root.title("🏦 SBI BANK")
root.geometry("1100x750")
root.configure(bg=COLORS['bg'])

# Custom Style
style = ttk.Style()
style.theme_use('clam')

# Configure Notebook (Tabs)
style.configure('TNotebook', background=COLORS['bg'], borderwidth=0)
style.configure('TNotebook.Tab',
                background=COLORS['light'],
                foreground=COLORS['text'],
                padding=[20, 10],
                font=FONTS['subheading'])
style.map('TNotebook.Tab',
          background=[('selected', COLORS['secondary'])],
          foreground=[('selected', COLORS['white'])],
          expand=[('selected', [1, 1, 1, 1])])

# Configure Treeview
style.configure('Treeview',
                background=COLORS['white'],
                foreground=COLORS['text'],
                rowheight=30,
                fieldbackground=COLORS['white'],
                borderwidth=0,
                font=FONTS['body'])
style.configure('Treeview.Heading',
                background=COLORS['primary'],
                foreground=COLORS['white'],
                relief='flat',
                font=FONTS['subheading'])
style.map('Treeview.Heading',
          background=[('active', COLORS['secondary'])])
style.map('Treeview',
          background=[('selected', COLORS['secondary'])],
          foreground=[('selected', COLORS['white'])])


# ==================== CUSTOM WIDGETS ====================
class ModernButton(tk.Button):
    def __init__(self, parent, text, command=None, style='primary', **kwargs):
        color = COLORS.get(style, COLORS['primary'])
        super().__init__(parent,
                         text=text,
                         command=command,
                         bg=color,
                         fg=COLORS['white'],
                         font=FONTS['button'],
                         relief='flat',
                         cursor='hand2',
                         padx=20,
                         pady=10,
                         borderwidth=0,
                         **kwargs)
        self.default_bg = color
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def on_enter(self, e):
        self['bg'] = self.adjust_color(self.default_bg)

    def on_leave(self, e):
        self['bg'] = self.default_bg

    def adjust_color(self, color):
        # Darken color slightly on hover
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, c - 20) for c in rgb)
        return '#%02x%02x%02x' % rgb


class ModernEntry(tk.Entry):
    def __init__(self, parent, placeholder='', **kwargs):
        super().__init__(parent,
                         font=FONTS['body'],
                         relief='solid',
                         borderwidth=1,
                         highlightthickness=2,
                         highlightbackground=COLORS['border'],
                         highlightcolor=COLORS['secondary'],
                         **kwargs)
        self.placeholder = placeholder
        self.placeholder_active = False

        if placeholder:
            self.insert(0, placeholder)
            self.config(fg=COLORS['text_light'])
            self.placeholder_active = True

        self.bind('<FocusIn>', self.on_focus_in)
        self.bind('<FocusOut>', self.on_focus_out)

    def on_focus_in(self, e):
        if self.placeholder_active:
            self.delete(0, tk.END)
            self.config(fg=COLORS['text'])
            self.placeholder_active = False

    def on_focus_out(self, e):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=COLORS['text_light'])
            self.placeholder_active = True

    def get_value(self):
        return '' if self.placeholder_active else self.get()


class CardFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent,
                         bg=COLORS['card'],
                         relief='flat',
                         borderwidth=1,
                         highlightbackground=COLORS['border'],
                         highlightthickness=1,
                         **kwargs)


# ==================== NOTEBOOK SETUP ====================
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both', padx=10, pady=10)

# Create Frames
home_frame = tk.Frame(notebook, bg=COLORS['bg'])
cust_frame = tk.Frame(notebook, bg=COLORS['bg'])
txn_frame = tk.Frame(notebook, bg=COLORS['bg'])
transfer_frame = tk.Frame(notebook, bg=COLORS['bg'])
history_frame = tk.Frame(notebook, bg=COLORS['bg'])

notebook.add(home_frame, text='  📊 Dashboard  ')
notebook.add(cust_frame, text='  👤 Add Customer  ')
notebook.add(txn_frame, text='  💰 Transactions  ')
notebook.add(transfer_frame, text='  🔄 Transfer  ')
notebook.add(history_frame, text='  📜 History  ')


# ==================== DASHBOARD ====================
def create_dashboard():
    # Title
    title_frame = tk.Frame(home_frame, bg=COLORS['bg'])
    title_frame.pack(fill='x', padx=20, pady=(20, 10))

    tk.Label(title_frame,
             text='💼 Account Dashboard',
             font=FONTS['title'],
             bg=COLORS['bg'],
             fg=COLORS['primary']).pack(side='left')

    ModernButton(title_frame,
                 text='🔄 Refresh',
                 command=refresh_accounts,
                 style='success').pack(side='right')

    # Accounts Table
    card = CardFrame(home_frame)
    card.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    cols = ('ID', 'Account No', 'Customer', 'Type', 'Balance')
    global tree
    tree = ttk.Treeview(card, columns=cols, show='headings', height=15)

    # Column widths
    tree.column('ID', width=50, anchor='center')
    tree.column('Account No', width=150, anchor='center')
    tree.column('Customer', width=250)
    tree.column('Type', width=120, anchor='center')
    tree.column('Balance', width=150, anchor='e')

    for col in cols:
        tree.heading(col, text=col)

    # Scrollbar
    scrollbar = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.pack(side='left', fill='both', expand=True, padx=2, pady=2)
    scrollbar.pack(side='right', fill='y')


def refresh_accounts():
    for row in tree.get_children():
        tree.delete(row)
    try:
        data = db.get_accounts()
        for acc in data:
            tree.insert('', 'end', values=(
                acc['account_id'],
                acc['account_number'],
                f"{acc['first_name']} {acc['last_name']}",
                acc['account_type'].upper(),
                f"₹{acc['balance']:,.2f}"
            ))
    except Exception as e:
        messagebox.showerror('Error', f'Failed to load accounts:\n{str(e)}')


create_dashboard()


# ==================== ADD CUSTOMER ====================
def create_customer_form():
    # Title
    tk.Label(cust_frame,
             text='👤 Create New Customer',
             font=FONTS['title'],
             bg=COLORS['bg'],
             fg=COLORS['primary']).pack(pady=(30, 20))

    # Form Card
    card = CardFrame(cust_frame)
    card.pack(padx=100, pady=20, fill='both')

    # Center the form
    form_frame = tk.Frame(card, bg=COLORS['card'])
    form_frame.pack(expand=True, pady=40)

    # Form fields
    fields = [
        ('First Name', 'fname'),
        ('Last Name', 'lname'),
        ('Email Address', 'email'),
        ('Phone Number', 'phone')
    ]

    entries = {}

    for idx, (label, key) in enumerate(fields):
        tk.Label(form_frame,
                 text=label,
                 font=FONTS['subheading'],
                 bg=COLORS['card'],
                 fg=COLORS['text']).grid(row=idx, column=0, sticky='w', padx=20, pady=15)

        entry = ModernEntry(form_frame, placeholder=f'Enter {label.lower()}', width=35)
        entry.grid(row=idx, column=1, padx=20, pady=15)
        entries[key] = entry

    # Account Type
    tk.Label(form_frame,
             text='Account Type',
             font=FONTS['subheading'],
             bg=COLORS['card'],
             fg=COLORS['text']).grid(row=4, column=0, sticky='w', padx=20, pady=15)

    acc_type = ttk.Combobox(form_frame,
                            values=['Savings', 'Current'],
                            font=FONTS['body'],
                            state='readonly',
                            width=33)
    acc_type.set('Savings')
    acc_type.grid(row=4, column=1, padx=20, pady=15)

    # Submit Button
    def submit():
        try:
            fname = entries['fname'].get_value()
            lname = entries['lname'].get_value()
            email = entries['email'].get_value()
            phone = entries['phone'].get_value()
            acc_t = acc_type.get().lower()

            if not all([fname, lname, email, phone]):
                messagebox.showwarning('Validation Error', 'Please fill all fields!')
                return

            db.create_customer(fname, lname, email, phone, acc_t)
            messagebox.showinfo('✅ Success',
                                f'Customer {fname} {lname} created successfully!')

            # Clear fields
            for entry in entries.values():
                entry.delete(0, tk.END)
                entry.placeholder_active = False
                entry.on_focus_out(None)

        except Exception as e:
            messagebox.showerror('❌ Error', f'Failed to create customer:\n{str(e)}')

    ModernButton(form_frame,
                 text='✅ Create Account',
                 command=submit,
                 style='success').grid(row=5, column=1, pady=30, sticky='e', padx=20)


create_customer_form()


# ==================== TRANSACTIONS ====================
def create_transaction_form():
    # Title
    tk.Label(txn_frame,
             text='💰 Deposit & Withdrawal',
             font=FONTS['title'],
             bg=COLORS['bg'],
             fg=COLORS['primary']).pack(pady=(30, 20))

    # Form Card
    card = CardFrame(txn_frame)
    card.pack(padx=100, pady=20, fill='both')

    form_frame = tk.Frame(card, bg=COLORS['card'])
    form_frame.pack(expand=True, pady=50)

    # Account ID
    tk.Label(form_frame,
             text='Account ID',
             font=FONTS['subheading'],
             bg=COLORS['card'],
             fg=COLORS['text']).grid(row=0, column=0, sticky='w', padx=20, pady=15)

    acc_id_entry = ModernEntry(form_frame, placeholder='Enter account ID', width=35)
    acc_id_entry.grid(row=0, column=1, padx=20, pady=15)

    # Amount
    tk.Label(form_frame,
             text='Amount (₹)',
             font=FONTS['subheading'],
             bg=COLORS['card'],
             fg=COLORS['text']).grid(row=1, column=0, sticky='w', padx=20, pady=15)

    amount_entry = ModernEntry(form_frame, placeholder='Enter amount', width=35)
    amount_entry.grid(row=1, column=1, padx=20, pady=15)

    # Action
    tk.Label(form_frame,
             text='Action',
             font=FONTS['subheading'],
             bg=COLORS['card'],
             fg=COLORS['text']).grid(row=2, column=0, sticky='w', padx=20, pady=15)

    action_var = ttk.Combobox(form_frame,
                              values=['💵 Deposit', '💸 Withdraw'],
                              font=FONTS['body'],
                              state='readonly',
                              width=33)
    action_var.set('💵 Deposit')
    action_var.grid(row=2, column=1, padx=20, pady=15)

    # Button Frame
    btn_frame = tk.Frame(form_frame, bg=COLORS['card'])
    btn_frame.grid(row=3, column=1, pady=30, sticky='e', padx=20)

    def perform_transaction():
        try:
            aid = acc_id_entry.get_value()
            amt = amount_entry.get_value()

            if not aid or not amt:
                messagebox.showwarning('Validation Error', 'Please fill all fields!')
                return

            aid = int(aid)
            amt = Decimal(amt)

            if amt <= 0:
                messagebox.showwarning('Invalid Amount', 'Amount must be greater than 0!')
                return

            balance = db.get_balance(aid)
            account = BankAccount(aid, balance)

            action = action_var.get()

            if '💵 Deposit' in action:
                account.deposit(amt)
                db.update_balance(aid, account.balance)
                db.record_transaction(aid, 'deposit', amt)
                messagebox.showinfo('✅ Success',
                                    f'Deposited ₹{amt:,.2f}\nNew Balance: ₹{account.balance:,.2f}')
            else:
                if account.withdraw(amt):
                    db.update_balance(aid, account.balance)
                    db.record_transaction(aid, 'withdraw', amt)
                    messagebox.showinfo('✅ Success',
                                        f'Withdrew ₹{amt:,.2f}\nNew Balance: ₹{account.balance:,.2f}')
                else:
                    messagebox.showerror('❌ Error', 'Insufficient funds!')

            acc_id_entry.delete(0, tk.END)
            amount_entry.delete(0, tk.END)
            acc_id_entry.on_focus_out(None)
            amount_entry.on_focus_out(None)

        except ValueError:
            messagebox.showerror('❌ Error', 'Invalid input! Please enter valid numbers.')
        except Exception as e:
            messagebox.showerror('❌ Error', f'Transaction failed:\n{str(e)}')

    ModernButton(btn_frame,
                 text='✅ Submit',
                 command=perform_transaction,
                 style='success').pack()


create_transaction_form()


# ==================== TRANSFER ====================
def create_transfer_form():
    # Title
    tk.Label(transfer_frame,
             text='🔄 Transfer Money',
             font=FONTS['title'],
             bg=COLORS['bg'],
             fg=COLORS['primary']).pack(pady=(30, 20))

    # Form Card
    card = CardFrame(transfer_frame)
    card.pack(padx=100, pady=20, fill='both')

    form_frame = tk.Frame(card, bg=COLORS['card'])
    form_frame.pack(expand=True, pady=50)

    # From Account
    tk.Label(form_frame,
             text='From Account ID',
             font=FONTS['subheading'],
             bg=COLORS['card'],
             fg=COLORS['text']).grid(row=0, column=0, sticky='w', padx=20, pady=15)

    from_entry = ModernEntry(form_frame, placeholder='Source account ID', width=35)
    from_entry.grid(row=0, column=1, padx=20, pady=15)

    # To Account
    tk.Label(form_frame,
             text='To Account ID',
             font=FONTS['subheading'],
             bg=COLORS['card'],
             fg=COLORS['text']).grid(row=1, column=0, sticky='w', padx=20, pady=15)

    to_entry = ModernEntry(form_frame, placeholder='Destination account ID', width=35)
    to_entry.grid(row=1, column=1, padx=20, pady=15)

    # Amount
    tk.Label(form_frame,
             text='Amount (₹)',
             font=FONTS['subheading'],
             bg=COLORS['card'],
             fg=COLORS['text']).grid(row=2, column=0, sticky='w', padx=20, pady=15)

    amount_entry = ModernEntry(form_frame, placeholder='Transfer amount', width=35)
    amount_entry.grid(row=2, column=1, padx=20, pady=15)

    def perform_transfer():
        try:
            aid_from = from_entry.get_value()
            aid_to = to_entry.get_value()
            amt = amount_entry.get_value()

            if not all([aid_from, aid_to, amt]):
                messagebox.showwarning('Validation Error', 'Please fill all fields!')
                return

            aid_from = int(aid_from)
            aid_to = int(aid_to)
            amt = Decimal(amt)

            if aid_from == aid_to:
                messagebox.showwarning('Invalid Transfer',
                                       'Source and destination accounts cannot be the same!')
                return

            if amt <= 0:
                messagebox.showwarning('Invalid Amount', 'Amount must be greater than 0!')
                return

            balance_from = db.get_balance(aid_from)
            balance_to = db.get_balance(aid_to)

            from_account = BankAccount(aid_from, balance_from)
            to_account = BankAccount(aid_to, balance_to)

            if from_account.withdraw(amt):
                to_account.deposit(amt)

                db.update_balance(aid_from, from_account.balance)
                db.update_balance(aid_to, to_account.balance)

                db.record_transaction(aid_from, 'transfer_out', amt)
                db.record_transaction(aid_to, 'transfer_in', amt)

                messagebox.showinfo('✅ Success',
                                    f'Transferred ₹{amt:,.2f}\n'
                                    f'From Account: {aid_from}\n'
                                    f'To Account: {aid_to}')

                from_entry.delete(0, tk.END)
                to_entry.delete(0, tk.END)
                amount_entry.delete(0, tk.END)
                from_entry.on_focus_out(None)
                to_entry.on_focus_out(None)
                amount_entry.on_focus_out(None)
            else:
                messagebox.showerror('❌ Error', 'Insufficient funds for transfer!')

        except ValueError:
            messagebox.showerror('❌ Error', 'Invalid input! Please enter valid numbers.')
        except Exception as e:
            messagebox.showerror('❌ Error', f'Transfer failed:\n{str(e)}')

    ModernButton(form_frame,
                 text='🔄 Transfer Now',
                 command=perform_transfer,
                 style='secondary').grid(row=3, column=1, pady=30, sticky='e', padx=20)


create_transfer_form()


# ==================== TRANSACTION HISTORY ====================
def create_history_view():
    # Title
    title_frame = tk.Frame(history_frame, bg=COLORS['bg'])
    title_frame.pack(fill='x', padx=20, pady=(20, 10))

    tk.Label(title_frame,
             text='📜 Transaction History',
             font=FONTS['title'],
             bg=COLORS['bg'],
             fg=COLORS['primary']).pack(side='left')

    # Search Frame
    search_frame = CardFrame(history_frame)
    search_frame.pack(fill='x', padx=20, pady=(0, 10))

    search_inner = tk.Frame(search_frame, bg=COLORS['card'])
    search_inner.pack(pady=15, padx=20)

    tk.Label(search_inner,
             text='Account ID:',
             font=FONTS['subheading'],
             bg=COLORS['card'],
             fg=COLORS['text']).pack(side='left', padx=(0, 10))

    history_acc = ModernEntry(search_inner, placeholder='Enter account ID', width=25)
    history_acc.pack(side='left', padx=10)

    # History Table
    card = CardFrame(history_frame)
    card.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    cols = ('ID', 'Type', 'Amount', 'Timestamp')
    global history_tree
    history_tree = ttk.Treeview(card, columns=cols, show='headings', height=12)

    history_tree.column('ID', width=80, anchor='center')
    history_tree.column('Type', width=150, anchor='center')
    history_tree.column('Amount', width=150, anchor='e')
    history_tree.column('Timestamp', width=200, anchor='center')

    for col in cols:
        history_tree.heading(col, text=col)

    scrollbar = ttk.Scrollbar(card, orient='vertical', command=history_tree.yview)
    history_tree.configure(yscrollcommand=scrollbar.set)

    history_tree.pack(side='left', fill='both', expand=True, padx=2, pady=2)
    scrollbar.pack(side='right', fill='y')

    def view_history():
        for row in history_tree.get_children():
            history_tree.delete(row)
        try:
            aid = history_acc.get_value()
            if not aid:
                messagebox.showwarning('Validation Error', 'Please enter an account ID!')
                return

            aid = int(aid)
            conn = db.get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT transaction_id, type, amount, timestamp FROM transactions WHERE account_id=%s ORDER BY timestamp DESC",
                (aid,))
            data = cur.fetchall()

            if not data:
                messagebox.showinfo('No Records', 'No transactions found for this account.')
            else:
                for tx in data:
                    tx_type = tx['type'].replace('_', ' ').title()

                    # Add emoji based on type
                    if 'deposit' in tx['type']:
                        tx_type = '💵 ' + tx_type
                    elif 'withdraw' in tx['type']:
                        tx_type = '💸 ' + tx_type
                    elif 'transfer_in' in tx['type']:
                        tx_type = '⬇️ ' + tx_type
                    elif 'transfer_out' in tx['type']:
                        tx_type = '⬆️ ' + tx_type

                    history_tree.insert('', 'end', values=(
                        tx['transaction_id'],
                        tx_type,
                        f"₹{Decimal(tx['amount']):,.2f}",
                        tx['timestamp']
                    ))

            cur.close()
            conn.close()
        except ValueError:
            messagebox.showerror('❌ Error', 'Invalid account ID!')
        except Exception as e:
            messagebox.showerror('❌ Error', f'Failed to load history:\n{str(e)}')

    ModernButton(search_inner,
                 text='🔍 View History',
                 command=view_history,
                 style='secondary').pack(side='left', padx=10)


create_history_view()

# ==================== INITIALIZE ====================
refresh_accounts()

# Run the application
root.mainloop()