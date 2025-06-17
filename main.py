import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.dialogs.dialogs import Querybox
from ttkbootstrap.dialogs.colorchooser import ColorChooserDialog
import subprocess
import json
import threading
import keyboard
import os

CONFIG_FILE = 'key_bindings.json'

class KeybindingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("keyHm - Configurador de Atajos v2.3")
        self.root.geometry("800x600")

        self.bindings = self.load_bindings()
        self.selected_item_id = None
        self.selected_color = "#FFFFFF"

        self.setup_ui()
        self.populate_treeview()
        self.start_keyboard_listener()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.Labelframe(main_frame, text="Añadir / Editar Atajo", padding=15)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(input_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(input_frame)
        self.name_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(input_frame, text="Atajo:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.shortcut_button = ttk.Button(input_frame, text="Haz clic para capturar", command=self.capture_shortcut_mode)
        self.shortcut_button.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self.shortcut_var = tk.StringVar()

        ttk.Label(input_frame, text="Comando:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.command_entry = ttk.Entry(input_frame)
        self.command_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(input_frame, text="Color:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        color_widget_frame = ttk.Frame(input_frame)
        color_widget_frame.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)
        self.color_preview = ttk.Frame(color_widget_frame, width=25, height=25, bootstyle="light")
        self.color_preview.pack(side=tk.LEFT)
        self.color_button = ttk.Button(color_widget_frame, text="Elegir Color...", command=self.choose_color)
        self.color_button.pack(side=tk.LEFT, padx=5)

        action_frame = ttk.Frame(input_frame)
        action_frame.grid(row=4, column=0, columnspan=3, pady=(10,0))
        self.save_button = ttk.Button(action_frame, text="Guardar Nuevo", command=self.save_binding, bootstyle="success")
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.clear_button = ttk.Button(action_frame, text="Limpiar", command=self.clear_inputs, bootstyle="secondary")
        self.clear_button.pack(side=tk.LEFT, padx=5)

        list_frame = ttk.Labelframe(main_frame, text="Atajos Configurados", padding=15)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "shortcut", "command")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", bootstyle="primary")
        self.tree.heading("name", text="Nombre"); self.tree.heading("shortcut", text="Atajo"); self.tree.heading("command", text="Comando")
        self.tree.column("name", width=200); self.tree.column("shortcut", width=150)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        list_button_frame = ttk.Frame(list_frame)
        list_button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10,0))
        self.edit_button = ttk.Button(list_button_frame, text="Editar", command=self.edit_binding, bootstyle="info")
        self.edit_button.pack(pady=5, fill=tk.X)
        self.remove_button = ttk.Button(list_button_frame, text="Eliminar", command=self.remove_binding, bootstyle="danger")
        self.remove_button.pack(pady=5, fill=tk.X)

    def choose_color(self):
        dialog = ColorChooserDialog(parent=self.root, title="Selecciona un color")
        dialog.show()
        if dialog.result:
            self.selected_color = dialog.result.hex
            s = ttk.Style()
            s.configure(f"{self.selected_color}.TFrame", background=self.selected_color)
            self.color_preview.configure(style=f"{self.selected_color}.TFrame")

    def capture_shortcut_mode(self):
        self.shortcut_button.config(text="Presiona una combinación de teclas...")
        self.root.bind_all("<KeyPress>", self.on_key_press, add="+")

    def on_key_press(self, event):
        self.root.unbind_all("<KeyPress>")
        self.shortcut_button.config(text="Haz clic para capturar")
        key = event.keysym.lower()
        MODIFIER_KEYS = ['control_l', 'control_r', 'shift_l', 'shift_r', 'alt_l', 'alt_r', 'super_l', 'super_r']
        if key in MODIFIER_KEYS:
            self.shortcut_button.config(text="Solo presionaste un modificador. Intenta de nuevo.")
            return

        parts = []
        if event.state & 0x0004: parts.append('ctrl')
        if event.state & 0x0008 or event.state & 0x0080: parts.append('alt')
        if event.state & 0x0001: parts.append('shift')
        if event.state & 0x0040: parts.append('super')
        
        if 'kp_' in key: key = key.replace('kp_', '')
        key = key.replace('_l', '').replace('_r', '')
        if key not in ('ctrl', 'alt', 'shift', 'super'):
            parts.append(key)
        
        shortcut = "+".join(parts)
        self.shortcut_var.set(shortcut)
        self.shortcut_button.config(text=f"Atajo capturado: {shortcut}")

    def clear_inputs(self, editing=False):
        self.name_entry.delete(0, tk.END)
        self.command_entry.delete(0, tk.END)
        self.shortcut_var.set("")
        self.shortcut_button.config(text="Haz clic para capturar")
        self.selected_color = "#FFFFFF"
        self.color_preview.configure(bootstyle="light")
        self.selected_item_id = None
        if not editing:
            self.save_button.config(text="Guardar Nuevo", command=self.save_binding)

    def populate_treeview(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for i, binding in enumerate(self.bindings):
            tag_name = f'color_tag_{i}'
            color = binding.get("color", "#FFFFFF")
            text_color = "#000" if int(color[1:], 16) > 0x888888 else "#FFF"
            self.tree.tag_configure(tag_name, background=color, foreground=text_color)
            self.tree.insert("", tk.END, iid=i, values=(binding["name"], binding["shortcut"], binding["command"]), tags=(tag_name,))

    def save_binding(self):
        name = self.name_entry.get()
        shortcut = self.shortcut_var.get()
        command = self.command_entry.get()
        if not all([name, shortcut, command]):
            Messagebox.show_warning("Todos los campos (Nombre, Atajo, Comando) son obligatorios.", "Campos incompletos")
            return
        
        new_binding = {"name": name, "shortcut": shortcut, "command": command, "color": self.selected_color}
        if self.selected_item_id is not None:
            self.bindings[self.selected_item_id] = new_binding
        else:
            self.bindings.append(new_binding)
            
        self.save_to_file()
        self.populate_treeview()
        self.reregister_hotkeys()
        self.clear_inputs()

    def edit_binding(self):
        selection = self.tree.selection()
        if not selection:
            Messagebox.show_warning("Por favor, selecciona un atajo de la lista para editar.", "Sin selección")
            return
        
        self.selected_item_id = int(selection[0])
        binding_data = self.bindings[self.selected_item_id]
        self.clear_inputs(editing=True)
        self.name_entry.insert(0, binding_data["name"])
        self.command_entry.insert(0, binding_data["command"])
        self.shortcut_var.set(binding_data["shortcut"])
        self.shortcut_button.config(text=f"Atajo capturado: {binding_data['shortcut']}")
        self.selected_color = binding_data.get("color", "#FFFFFF")
        s = ttk.Style()
        s.configure(f"{self.selected_color}.TFrame", background=self.selected_color)
        self.color_preview.configure(style=f"{self.selected_color}.TFrame")
        self.save_button.config(text="Actualizar Atajo", command=self.save_binding)

    def remove_binding(self):
        selection = self.tree.selection()
        if not selection:
            Messagebox.show_warning("Por favor, selecciona un atajo de la lista para eliminar.", "Sin selección")
            return
        item_id = int(selection[0])
        binding_name = self.bindings[item_id]["name"]
        if Messagebox.yesno(f"¿Eliminar '{binding_name}'?", "Confirmar", parent=self.root) == "Yes":
            self.bindings.pop(item_id)
            self.save_to_file()
            self.populate_treeview()
            self.reregister_hotkeys()

    def load_bindings(self):
        if not os.path.exists(CONFIG_FILE): return []
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return [{"name": f"Atajo {i+1}", "shortcut": sc, "command": cmd, "color": "#375A7F"} for i, (sc, cmd) in enumerate(data.items())]
                return data
        except (json.JSONDecodeError, IOError): return []

    def save_to_file(self):
        with open(CONFIG_FILE, 'w') as f: json.dump(self.bindings, f, indent=4)

    def reregister_hotkeys(self):
        keyboard.remove_all_hotkeys()
        self.start_keyboard_listener()

    def start_keyboard_listener(self):
        for binding in self.bindings:
            # --- MEJORA DE ESTABILIDAD ---
            # Si un atajo es inválido, lo ignoramos en lugar de cerrar la app
            try:
                shortcut = binding.get("shortcut", "")
                if not shortcut: continue # Ignorar si no hay atajo
                
                keyboard.add_hotkey(shortcut, lambda cmd=binding["command"]: self.execute_command(cmd))
            except Exception as e:
                print(f"ADVERTENCIA: No se pudo registrar el atajo '{binding.get('name', 'Desconocido')}' ('{shortcut}'). Razón: {e}")

    def execute_command(self, command):
        threading.Thread(target=lambda: subprocess.run(command, shell=True, check=True), daemon=True).start()

    def on_closing(self):
        keyboard.remove_all_hotkeys()
        self.root.destroy()

if __name__ == "__main__":
    # if os.geteuid() != 0:
    #      Messagebox.show_warning("Esta aplicación necesita ejecutarse con privilegios de superusuario...", "Permisos insuficientes")

    root = ttk.Window(themename="darkly")
    app = KeybindingApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()