import calendar
from pathlib import Path
import ast
import matplotlib.pyplot as plt
import pandas as pd
from functools import partial
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext, filedialog
from tkinter import ttk

#------------------------ Options ------------------------#

UI_TEXT_DEFAULT = {
    "ru": {
        "title": "Shift Calendar",
        "label_year": "Введите год:",
        "label_month": "Введите месяц (1-12):",
        "label_data": "Введите данные (день + код смены):",
        "paste_button": "Вставить из буфера",
        "shifts_button": "Смены",
        "create_button": "Создать календарь",
        "language_button": "Сменить язык",
        "ext_lang": "Использовать внешний словарь",
        "exit_button": "Выход",
        "current_shifts": "Текущие смены:",
        "add_shift_title": "Добавить смену",
        "add_shift_message1": "Код смены (1-2 буквы):",
        "add_shift_message2": "Время смены (08:00 - 17:00):",
        "add_shift_success": "Смена '{code}' добавлена: {time}",
        "success_title": "Готово",
        "success_message": "Календарь сохранён как {filename}",
        "error_title": "Ошибка",
        "error_year_month_message": "Год и месяц должны быть числами.",
        "error_month_range_message": "Месяц должен быть 1…12.",
        "error_no_data_message": "Нет данных по сменам.",
        "error_line_format": "Неверный формат: {line}",
        "error_line_value": "Неверный день или смена: {line}",
        "empty_clipboard_error": "Ошибка",
        "empty_clipboard_message": "Буфер обмена пуст.",
        "week_days": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        "months": {
            1: "Январь",
            2: "Февраль",
            3: "Март",
            4: "Апрель",
            5: "Май",
            6: "Июнь",
            7: "Июль",
            8: "Август",
            9: "Сентябрь",
            10: "Октябрь",
            11: "Ноябрь",
            12: "Декабрь",
        },
        "help_button": "Инструкция",
        "help_instructions": (
            "Каждая строка: <день> <код смены>, разделитель — пробел или таб.\n"
            "Важно: после ночной смены S автоматически выделяется следующий день."
        ),
    },
    "en": {
        "title": "Shift Calendar",
        "label_year": "Enter year:",
        "label_month": "Enter month (1-12):",
        "label_data": "Enter data (day + shift code):",
        "paste_button": "Paste from clipboard",
        "shifts_button": "Shifts",
        "create_button": "Create calendar",
        "language_button": "Switch language",
        "ext_lang": "Use external dictionary",
        "exit_button": "Exit",
        "current_shifts": "Current shifts:",
        "add_shift_title": "Add shift",
        "add_shift_message1": "Shift code (1-2 letters):",
        "add_shift_message2": "Shift time (08:00 - 17:00):",
        "add_shift_success": "Shift '{code}' added: {time}",
        "success_title": "Done",
        "success_message": "Calendar saved as {filename}",
        "error_title": "Error",
        "error_year_month_message": "Year and month must be integers.",
        "error_month_range_message": "Month must be 1…12.",
        "error_no_data_message": "No shift data.",
        "error_line_format": "Invalid format: {line}",
        "error_line_value": "Invalid day or shift: {line}",
        "empty_clipboard_error": "Error",
        "empty_clipboard_message": "Clipboard empty.",
        "week_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "months": {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        },
        "help_button": "Help",
        "help_instructions": (
            "Line format: <day> <shift code>, separated by space or tab.\n"
            "IMPORTANT: after night shift S the next day is highlighted automatically."
        ),
    },
}

current_lang = "ru"
current_index = 0
external_loaded = False
ui_text_ext = None

LANG_SEQUENCE = ["ru", "en", "ext"]

SHIFTS = {
    "C": "7:00 - 16:30",
    "D": "9:00 - 17:30",
    "E": "10:30 - 20:00",
    "F": "12:30 - 22:00",
    "S": "15:00 - 10:00",
}

WEEKEND_COLORS = {"H": "red", "h": "red"}

#------------------- Utility Functions -------------------#

def get_current_dict():
    if current_lang in ("ru", "en"):
        return UI_TEXT_DEFAULT[current_lang]
    if (
        current_lang == "ext"
        and external_loaded
        and ui_text_ext
        and "ext" in ui_text_ext
    ):
        return ui_text_ext["ext"]
    return UI_TEXT_DEFAULT["ru"]

def tr(key):
    return get_current_dict()[key]

def load_external_dict():
    global external_loaded, ui_text_ext
    if not use_external_dict_var.get():
        external_loaded = False
        ui_text_ext = None
        return
    path = filedialog.askopenfilename(
        title="Select dictionary file",
        filetypes=[("Python dict", "*.txt *.py"), ("All files", "*.*")],
    )
    if not path:
        use_external_dict_var.set(False)
        return
    try:
        ui_text_ext = ast.literal_eval(Path(path).read_text(encoding="utf-8"))
        external_loaded = True
    except (OSError, ValueError, SyntaxError) as exc:
        messagebox.showerror("Error", f"Error loading dictionary:\n{exc}")
        external_loaded = False
        ui_text_ext = None
        use_external_dict_var.set(False)

def update_widgets():
    for widget, key in WIDGETS_MAP.items():
        widget.config(text=tr(key))
    root.title(tr("title"))
    ext_checkbox.config(text=tr("ext_lang"))

def toggle_language():
    global current_index, current_lang
    steps = 3 if use_external_dict_var.get() else 2
    current_index = (current_index + 1) % steps
    current_lang = LANG_SEQUENCE[current_index]
    if current_lang == "ext" and not external_loaded:
        messagebox.showerror("Error", "External dictionary not loaded.")
        current_lang = "ru"
        current_index = 0
    update_widgets()

def paste_from_clipboard():
    try:
        clip = root.clipboard_get()
        input_text.insert("end", clip)
    except Exception:
        messagebox.showerror(tr("empty_clipboard_error"), tr("empty_clipboard_message"))

def create_calendar():
    try:
        year = int(year_entry.get())
        month = int(month_entry.get())
    except ValueError:
        messagebox.showerror(tr("error_title"), tr("error_year_month_message"))
        return
    if not (1 <= month <= 12):
        messagebox.showerror(tr("error_title"), tr("error_month_range_message"))
        return
    raw = input_text.get("1.0", "end").strip()
    if not raw:
        messagebox.showerror(tr("error_title"), tr("error_no_data_message"))
        return
    workdays, colors, night_days = {}, {}, set()
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            day_s, shift_s = line.split()
            day = int(day_s)
            shift = shift_s.upper()
        except ValueError:
            messagebox.showerror(
                tr("error_title"), tr("error_line_format").format(line=line)
            )
            return
        if shift in SHIFTS:
            workdays[day] = f"{SHIFTS[shift]}\n({shift})"
            colors[day] = "black"
            if shift == "S":
                night_days.add(day)
        elif shift in WEEKEND_COLORS:
            colors[day] = WEEKEND_COLORS[shift]
        else:
            messagebox.showerror(
                tr("error_title"), tr("error_line_value").format(line=line)
            )
            return
    _, max_day = calendar.monthrange(year, month)
    for d in night_days:
        if d < max_day:
            colors[d + 1] = "blue"
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axis("off")
    for col, day_name in enumerate(tr("week_days")):
        ax.text(col, 0, day_name, ha="center", va="center", weight="bold")
    month_rows = calendar.monthcalendar(year, month)
    for row_i, week in enumerate(month_rows, 1):
        for col_i, day in enumerate(week):
            if day == 0:
                continue
            col_color = colors.get(day, "black")
            ax.text(
                col_i,
                row_i,
                str(day),
                ha="center",
                va="center",
                color=col_color,
                fontsize=8,
                weight="bold",
            )
            if day in workdays:
                ax.text(
                    col_i,
                    row_i + 0.25,
                    workdays[day],
                    ha="center",
                    va="top",
                    color=col_color,
                    fontsize=7,
                )
    ax.set_xlim(-0.5, 6.5)
    ax.set_ylim(len(month_rows) + 0.5, -0.5)
    title = tr("months").get(month, str(month)) + f" {year}"
    ax.set_title(title, pad=10)
    out_name = f"calendar_{year}_{month}.png"
    try:
        fig.savefig(out_name, bbox_inches="tight")
        messagebox.showinfo(
            tr("success_title"), tr("success_message").format(filename=out_name)
        )
    except OSError as exc:
        messagebox.showerror(tr("error_title"), str(exc))
    finally:
        plt.close(fig)

#------------------- Shifts -------------------#

def show_shifts_window():
    win = tk.Toplevel(root)
    win.title(tr("shifts_button"))
    ttk.Label(win, text=tr("current_shifts"), font=("Arial", 10, "bold")).grid(
        row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5
    )
    row_index = 1
    for code, time_range in SHIFTS.items():
        ttk.Label(win, text=f"{code}: {time_range}", anchor="w").grid(
            row=row_index, column=0, sticky="w", padx=5, pady=2
        )
        ttk.Button(
            win, text="❌", width=2, command=partial(delete_shift, code, win)
        ).grid(row=row_index, column=1, sticky="e", padx=5, pady=2)
        row_index += 1
    ttk.Button(win, text="+", command=partial(add_new_shift, win)).grid(
        row=row_index, column=0, padx=5, pady=5, sticky="w"
    )

def add_new_shift(parent):
    code = simpledialog.askstring(tr("add_shift_title"), tr("add_shift_message1"))
    if not code:
        return
    time_range = simpledialog.askstring(
        tr("add_shift_title"), tr("add_shift_message2"), initialvalue="00:00 - 00:00"
    )
    if not time_range:
        return
    SHIFTS[code.upper()] = time_range
    messagebox.showinfo(
        tr("success_title"),
        tr("add_shift_success").format(code=code.upper(), time=time_range),
    )
    parent.destroy()
    show_shifts_window()

def delete_shift(code, parent):
    if code in SHIFTS:
        del SHIFTS[code]
        parent.destroy()
        show_shifts_window()

def show_help():
    messagebox.showinfo(tr("help_button"), tr("help_instructions"))


#------------------- GUI -------------------#

def build_gui():
    global root, year_entry, month_entry, input_text, ext_checkbox, use_external_dict_var, WIDGETS_MAP

    root = tk.Tk()
    root.title(tr("title"))

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)

    label_year = ttk.Label(root, text=tr("label_year"))
    label_year.grid(row=0, column=0, sticky="e", padx=5, pady=2)
    year_entry = ttk.Entry(root, width=8)
    year_entry.insert(0, "2025")
    year_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)

    label_month = ttk.Label(root, text=tr("label_month"))
    label_month.grid(row=1, column=0, sticky="e", padx=5, pady=2)
    month_entry = ttk.Entry(root, width=8)
    month_entry.insert(0, "3")
    month_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)

    label_data = ttk.Label(root, text=tr("label_data"))
    label_data.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=(5, 0))

    paste_button = ttk.Button(
        root, text=tr("paste_button"), command=paste_from_clipboard
    )
    paste_button.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=2)

    input_text = scrolledtext.ScrolledText(root, width=30, height=8)
    input_text.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=5, pady=2)

    shifts_button = ttk.Button(
        root, text=tr("shifts_button"), command=show_shifts_window
    )
    shifts_button.grid(row=5, column=0, sticky="ew", padx=5, pady=2)

    create_button = ttk.Button(root, text=tr("create_button"), command=create_calendar)
    create_button.grid(row=5, column=1, sticky="ew", padx=5, pady=2)

    language_button = ttk.Button(
        root, text=tr("language_button"), command=toggle_language
    )
    language_button.grid(row=7, column=0, columnspan=2, sticky="ew", padx=5, pady=2)

    use_external_dict_var = tk.BooleanVar(value=False)
    ext_checkbox = ttk.Checkbutton(
        root,
        text=tr("ext_lang"),
        variable=use_external_dict_var,
        command=load_external_dict,
    )
    ext_checkbox.grid(row=8, column=0, columnspan=2, sticky="w", padx=5, pady=2)

    help_button = ttk.Button(root, text=tr("help_button"), command=show_help)
    help_button.grid(row=9, column=0, columnspan=2, sticky="ew", padx=5, pady=2)

    exit_button = ttk.Button(root, text=tr("exit_button"), command=root.destroy)
    exit_button.grid(row=10, column=0, columnspan=2, sticky="ew", padx=5, pady=(2, 6))

    WIDGETS_MAP = {
        label_year: "label_year",
        label_month: "label_month",
        label_data: "label_data",
        paste_button: "paste_button",
        shifts_button: "shifts_button",
        create_button: "create_button",
        language_button: "language_button",
        ext_checkbox: "ext_lang",
        help_button: "help_button",
        exit_button: "exit_button",
    }

    root.mainloop()


#------------------- Main -------------------#

def main():
    build_gui()

if __name__ == "__main__":
    main()
