import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

class JsonConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Convertisseur JSON")
        self.root.geometry("500x200")

        tk.Label(root, text="Convertisseur JSON", font=("Arial", 16, "bold")).pack(pady=10)

        tk.Button(root, text="Sélectionner un fichier JSON", command=self.select_file, 
                  width=30, height=2, bg="#4CAF50", fg="white", font=("Arial", 10)).pack(pady=10)

        tk.Label(root, text="Simple et rapide", font=("Arial", 9)).pack(pady=5)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionnez le fichier JSON source",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:
            return

        folder_path = simpledialog.askstring(
            "Chemin du dossier",
            "Entrez le chemin du dossier\n(ex: X:\\StableDiffusion\\comfyui_output\\2026-01-06\\):",
            parent=self.root
        )

        if not folder_path:
            return

        try:
            self.convert_json(file_path, folder_path)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la conversion :\n{str(e)}")

    def convert_json(self, source_file, folder_path):
        with open(source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        folder_path = folder_path.replace('/', '\\').replace('\\', '\\\\')
        if not folder_path.endswith('\\\\'):
            folder_path += '\\\\'

        result = {"images": []}
        for item in data:
            new_item = item.copy()
            new_item['absolutePath'] = folder_path + item['fileName']
            result['images'].append(new_item)

        base_name = os.path.splitext(source_file)[0]
        output_file = f"{base_name}_fixed.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        messagebox.showinfo("Succès", f"Fichier créé :\n{output_file}")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = JsonConverterApp(root)
    root.mainloop()
