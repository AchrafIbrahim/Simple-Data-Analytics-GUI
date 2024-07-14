import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, scrolledtext, Scrollbar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st

file_path = None
df = None

# =========================GUI FRAME=========================
# Base GUI
root = tk.Tk()
root.title("Simple Data Analytics App")
root.geometry("1200x800")

def on_mouse_wheel(event, canvas):
    current_scroll_pos = canvas.yview()[0]
    if current_scroll_pos <= 0 and event.delta > 0:
        return
    canvas.yview_scroll(int(-1*(event.delta/120)),"units")
    
# Main Frame for scrolled content ()
main = tk.Frame(root)
main.pack(fill=tk.BOTH, expand=1)
# Add Canvas on top Main Frame
canvas = tk.Canvas(main)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
# Add Scrollbar on canvas
scrollbar = Scrollbar(main, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
# Scrollbar and Canvas configuration
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
# Scrollable Frame inside canvas
scrollable_frame = tk.Frame(canvas)
canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
# Mouse wheel event for scroll
canvas.bind_all("<MouseWheel>", lambda event: on_mouse_wheel(event, canvas))

# Title Frame
title_topbutton_frame = tk.Frame(scrollable_frame)
title_topbutton_frame.grid(row=0, column=0, sticky="w")
# Table Frame
table_frame = tk.Frame(scrollable_frame)
table_frame.grid(row=1, column=0, sticky="nsew", padx=10)
# Result Frame (After button action)
result_frame = tk.Frame(scrollable_frame)
result_frame.grid(row=2, padx=10, sticky="w")
# Button Frame
process_button_frame = tk.Frame(scrollable_frame)
process_button_frame.grid(row=3, sticky="w")
# Text Area inside Result Frame
text_area = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=75, height=10)
text_area.grid(row=0, column=0, padx=10, pady=10, sticky="w")
# Visualization Frame
visualization_frame = tk.Frame(scrollable_frame)
visualization_frame.grid(row=4, column=0, sticky="w")
#TITLE
title = tk.Label(title_topbutton_frame, text="Simple Data Analytics", font="Helvetica 16 bold")
title.grid(pady=20, padx=20, sticky="w")


# =========================FUNCTION=========================
#DISPLAY DATAFRAME
def display_dataframe():
    for widget in table_frame.winfo_children():
        widget.destroy()
    if df is not None:
        tree = ttk.Treeview(table_frame, columns=list(df.columns), show="headings")
        tree.pack(padx=10, pady=10, fill="both", expand=True)
    #header kolom
        for col in df.columns:
            tree.heading(col, text=col)
        #lebar kolom berdasarkan panjang data
        for col in df.columns:
            max_width = max(df[col].astype(str).map(len).max(), len(col)*10)  # Lebar kolom minimal adalah panjang header
            tree.column(col, width=max_width + 20)  # Tambahkan sedikit ruang ekstra
        #Masukkan data DataFrame ke dalam Treeview
        for index, row in df.iterrows():
            tree.insert("", "end", values=list(row))
        #scrollbar horizontal
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        tree.configure(xscrollcommand=scrollbar_x.set)

#TEXTAREA FUNCTION
def update_text_area(text):
    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, text)
    text_area.config(state=tk.DISABLED)

#BROWSE FILE
def browse_file():
    global file_path, df
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
    )
    if file_path:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        display_dataframe()

#DF SHAPE
def df_shape():
    global df
    if df is not None:
        result_text = f"Shape of DataFrame: \n{df.shape}"
        update_text_area(result_text)
    else:
        current_text = text_area.get("1.0", tk.END)
        if "No data available to perform data shape" not in current_text:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, "No data available to perform data shape\n")

#DF DESCRIBE
def df_describe():
    global df
    if df is not None:
        result_text = f"Shape of DataFrame: \n{df.describe()}"
        update_text_area(result_text)
    else:
        current_text = text_area.get("1.0", tk.END)
        if "No data available to perform data describe" not in current_text:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, "No data available to perform data describe\n")

#DF VALUE COUNTS
def df_value_counts():
    global df, column
    if df is not None:
        categorical = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical) > 0:
            result_text = ""
            for column in categorical:
                result_text += f"\nValue Counts for column '{column}': \n{df[column].value_counts().to_string()}\n"
            update_text_area(result_text)
        else: 
            print("No categorical columns found in Data")
    else:
        current_text = text_area.get("1.0", tk.END)
        if "No data available to perform value counts" not in current_text:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, "No data available to perform value counts\n")

#DF DETECT MISSING VALUES
def df_missingvalues():
    global df 
    if df is not None:
        missing_values = df.isna()
        if missing_values.sum().sum() == 0:
            result_text = "There are no missing values"
        else:
            result_text = "Missing values found in the following locations: \n"
            for column in missing_values.columns:
                missing_indices = missing_values.index[missing_values[column]].tolist()
                if missing_indices:
                    result_text += f"Column '{column}': Rows {missing_indices}\n"
        update_text_area(result_text)
    else:
        current_text = text_area.get("1.0", tk.END)
        if "No data available to perform data describe" not in current_text:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, "No data available to perform data describe\n")

#DF COUNT UNIQUE DATA IN COLUMN
def df_countunique():
    global df
    if df is not None: 
        unique_counts = df.nunique()
        result_text = f"\nNumber of unique values in each column:\n{unique_counts.to_string()}"
        update_text_area(result_text)
    else:
        current_text = text_area.get("1.0", tk.END)
        if "No data available to perform Unique Count" not in current_text:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, "No data available to perform Count Unique\n")

#DF CORRELATION
def df_correlation():
    global df 
    if df is not None:
        method_list = ["pearson", "kendall", "spearman"]
        if len(method_list) > 0:
            result_text = ""
            for methods in method_list:
                correlation_matrix = df.corr(method=methods)
                result_text += f"\nCorrelation using '{methods}' method: \n{correlation_matrix.to_string()}\n"
            update_text_area(result_text)
    else:
        current_text = text_area.get("1.0", tk.END)
        if "No data available to perform Correlation" not in current_text:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, "No data available to perform Correlation\n")

#DF BAR CHART
def df_barchart():
    global df
    if df is not None:
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_columns) > 0:
            column = categorical_columns[0]  # For simplicity, we take the first categorical column
            value_counts = df[column].value_counts()
            
            # Create a bar chart
            fig, ax = plt.subplots()
            value_counts.plot(kind='bar', ax=ax)
            ax.set_title(f"Bar Chart for {column}")
            ax.set_xlabel(column)
            ax.set_ylabel("Count")

            # Display the bar chart in the Tkinter window
            canvas = FigureCanvasTkAgg(fig, master=visualization_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, padx=0, pady=0, sticky="w")
        else:
            update_text_area("No categorical columns available for bar chart.")
    else:
        current_text = text_area.get("1.0", tk.END)
        if "No data available to plot bar chart" not in current_text:
            text_area.delete("1.0", tk.END)
            text_area.insert(tk.END, "No data available to plot bar chart\n")

# =========================BUTTON=========================
button_width = 10

button_browse_file = tk.Button(title_topbutton_frame, text="Browse File", width=button_width, command=browse_file)
button_browse_file.grid(row=1, column=0, padx=20, pady=5, sticky="w")

button_shape = tk.Button(process_button_frame, text="Shape", command=df_shape, width=button_width)
button_shape.grid(row=0, column=0, padx=(20,5), pady=5, sticky="w")

button_describe = tk.Button(process_button_frame, text="Describe", command=df_describe, width=button_width)
button_describe.grid(row=0, column=1, padx=5, pady=5, sticky="w")

button_valuecounts = tk.Button(process_button_frame, text="Value Counts", command=df_value_counts, width=button_width)
button_valuecounts.grid(row=0, column=2, padx=5, pady=5, sticky="w")

button_missingvalues = tk.Button(process_button_frame, text="Missing Values", command=df_missingvalues, width=button_width)
button_missingvalues.grid(row=0, column=3, padx=5, pady=5, sticky="w")

button_countunique = tk.Button(process_button_frame, text="Count Unique", command=df_countunique, width=button_width)
button_countunique.grid(row=0, column=4, padx=5, pady=5, sticky="w")

button_correlation = tk.Button(process_button_frame, text="Correlation", command=df_correlation, width=button_width)
button_correlation.grid(row=0, column=5, padx=5, pady=5, sticky="w")

button_barchart = tk.Button(process_button_frame, text="Bar Chart", command=df_barchart, width=button_width)
button_barchart.grid(row=1, column=0, padx=(20,5), pady=5, sticky="w")

root.mainloop()



