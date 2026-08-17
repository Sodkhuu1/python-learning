import tkinter as tk

def calculate(op):
    try:
        a = float(entry_a.get())
        b = float(entry_b.get())
    except ValueError:
        result_label.config(text="Aldaa: too oruulna uu!")
        return

    if op == "+":
        result = a + b
    elif op == "-":
        result = a - b
    elif op == "*":
        result = a * b
    elif op == "/":
        if b == 0:
            result_label.config(text="Aldaa: 0-d huwaaj bolohgui!")
            return
        result = a / b
    else:
        result_label.config(text="Buruu uildel!")
        return

    result_label.config(text=f"Ur dun: {result}")

# Tsonh uusgeh
root = tk.Tk()
root.title("Toonii mashin")

# Widget-uud
tk.Label(root, text="Ehnnii too:").grid(row=0, column=0, padx=5, pady=5)
entry_a = tk.Entry(root)
entry_a.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="2 dahi too:").grid(row=1, column=0, padx=5, pady=5)
entry_b = tk.Entry(root)
entry_b.grid(row=1, column=1, padx=5, pady=5)

# Uildel tovchuud
tk.Button(root, text="+", width=5, command=lambda: calculate("+")).grid(row=2, column=0, padx=5, pady=5)
tk.Button(root, text="-", width=5, command=lambda: calculate("-")).grid(row=2, column=1, padx=5, pady=5)
tk.Button(root, text="*", width=5, command=lambda: calculate("*")).grid(row=3, column=0, padx=5, pady=5)
tk.Button(root, text="/", width=5, command=lambda: calculate("/")).grid(row=3, column=1, padx=5, pady=5)

# Ur dun haruulah label
result_label = tk.Label(root, text="Ur dun: ")
result_label.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

root.mainloop()
