##import os

import os
import tkinter as tk
from tkinter import ttk, simpledialog
from tkinter import ttk
import shutil
import tkinter.ttk as ttk

class FileExplorer:
    def __init__(self, root):
        self.root = root

        self.button_style = ttk.Style()
        self.button_style.configure("TButton", padding=(20, 15), font=('Helvetica', 10))
        self.button_style.map("Green.TButton", background=[("active", "#2ecc71"), ("!active", "#2ecc71")])
        self.button_style.map("Red.TButton", background=[("active", "#e74c3c"), ("!active", "#e74c3c")])
        self.button_style.map("Orange.TButton", background=[("active", "#f39c12"), ("!active", "#f39c12")])
        self.button_style.map("Purple.TButton", background=[("active", "#8e44ad"), ("!active", "#8e44ad")])  

        self.tree = ttk.Treeview(self.root)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Double-1>", self.OnDoubleClick)
        self.node_dict = {}
        self.initial_directory = ""

        self.initial_directory = tk.simpledialog.askstring("Directorio Inicial", "Ingrese el directorio inicial:")
        
        if os.path.isdir(self.initial_directory):
            root_id = self.tree.insert("", "end", text=os.path.basename(self.initial_directory))
            self.node_dict[root_id] = self.initial_directory
            self.expand_node(root_id)
        else:
            print("Directorio no válido. Saliendo del programa.")
            root.destroy()

        self.add_button = ttk.Button(self.root, text="Agregar", command=self.add_node, style="Green.TButton")
        self.add_button.pack(side="top", pady=5, padx=10 )

        self.delete_button = ttk.Button(self.root, text="Eliminar", command=self.delete_folder, style="Red.TButton")
        self.delete_button.pack(side="top", pady=5, padx=10)

        self.rename_button = ttk.Button(self.root, text="Renombrar", command=self.rename_node, style="Orange.TButton")
        self.rename_button.pack(side="top", pady=5, padx=10)
           
        self.search_button = ttk.Button(self.root, text="Buscar", command=self.search_node, style="Purple.TButton") 
        self.search_button.pack(side="top", pady=5, padx=10)

        self.copy_button = ttk.Button(self.root, text="Copiar", command=self.copy_node, style="Orange.TButton")
        self.copy_button.pack(side="top", pady=5, padx=10)

        self.cut_button = ttk.Button(self.root, text="Cortar", command=self.cut_node, style="Orange.TButton")
        self.cut_button.pack(side="top", pady=5, padx=10)

        self.paste_button = ttk.Button(self.root, text="Pegar", command=self.paste_node, style="Orange.TButton")
        self.paste_button.pack(side="top", pady=5, padx=10)

        self.copy_data = {"node_id": None, "node_path": None, "cut_mode": False}
        self.cut_item = None
        self.cut_path = None

    def add_node(self):
        parent_item = self.tree.selection()[0]
        parent_path = self.node_dict[parent_item]

        new_node_name = tk.simpledialog.askstring("Agregar Nodo", "Ingrese el nombre del nuevo nodo:")
        new_node_path = os.path.join(parent_path, new_node_name)

        if not new_node_name:
            print("Ingrese un nombre válido para el nuevo nodo.")
            return

        if os.path.exists(new_node_path):
            print(f"Ya existe un nodo con el nombre '{new_node_name}'.")
            return

        if not os.path.exists(new_node_path):
            if new_node_name.lower().endswith(".txt"):
                with open(new_node_path, "w") as new_file:
                    pass
            else:
                os.makedirs(new_node_path)

        new_node_id = self.tree.insert(parent_item, "end", text=new_node_name)
        self.node_dict[new_node_id] = new_node_path

        if os.path.isdir(new_node_path):
            self.expand_node(new_node_id)

    def expand_node(self, node_id):
        children = self.tree.get_children(node_id)
        if children:
            return
        node_path = self.node_dict[node_id]
        for child_path in os.listdir(node_path):
            child_full_path = os.path.join(node_path, child_path)
            if os.path.isdir(child_full_path):
                child_id = self.tree.insert(node_id, "end", text=os.path.basename(child_full_path))
                self.node_dict[child_id] = child_full_path
                self.expand_node(child_id)
            elif child_full_path.lower().endswith(".txt"):
                child_id = self.tree.insert(node_id, "end", text=os.path.basename(child_full_path))
                self.node_dict[child_id] = child_full_path

    def OnDoubleClick(self, event):
        item = self.tree.selection()[0]
        node_path = self.node_dict[item]
        if os.path.isdir(node_path):
            self.expand_node(item)

    #Eliminar
   
    def delete_item(self, node_id):
        node_path = self.node_dict[node_id]

        for child_id in self.tree.get_children(node_id):
            self.delete_item(child_id)

        if self.cut_item is not None and node_id == self.cut_item:
            # El nodo cortado no debe eliminarse aquí, ya que se moverá en la función paste_node
            return

        try:
            if os.path.isdir(node_path):
                shutil.rmtree(node_path)
            else:
                os.remove(node_path)

            del self.node_dict[node_id]
            self.tree.delete(node_id)
            print(f"'{os.path.basename(node_path)}' ha sido eliminado.")
        except FileNotFoundError:
            print(f"Error: No se puede encontrar el archivo '{os.path.basename(node_path)}'.")
        except PermissionError:
            print(f"Error: Permiso denegado para eliminar '{os.path.basename(node_path)}'.")
        except Exception as e:
            print(f"Error al eliminar '{os.path.basename(node_path)}': {e}")


    def delete_folder(self):
        item = self.tree.selection()[0]
        confirmation = tk.simpledialog.askstring("Eliminar Nodo", f"¿Seguro que desea eliminar '{os.path.basename(self.node_dict[item])}' y sus subnodos? (Sí/No): ")
        if confirmation and confirmation.lower() == 'si':
            self.delete_item(item)
        else:
            print("Operación de eliminación cancelada.")

    #Renombrar        

    def rename_node(self):
        item = self.tree.selection()[0]
        old_node_path = self.node_dict[item]
        new_node_name = tk.simpledialog.askstring("Renombrar Nodo", "Ingrese el nuevo nombre para el nodo:")
        new_node_path = os.path.join(os.path.dirname(old_node_path), new_node_name)

        if not new_node_name:
            print("Ingrese un nombre válido para el nuevo nodo.")
            return

        if os.path.exists(new_node_path):
            print(f"Ya existe un nodo con el nombre '{new_node_name}'.")
            return

        os.rename(old_node_path, new_node_path)

        self.node_dict[item] = new_node_path
        self.tree.item(item, text=new_node_name)

## buscar

    def search_node(self):
        search_text = tk.simpledialog.askstring("Buscar Nodo", "Ingrese el nombre del nodo a buscar:")
        if not search_text:
            print("Ingrese un texto válido para la búsqueda.")
            return

        matching_nodes = self.find_matching_nodes(search_text)
        if not matching_nodes:
            print(f"No se encontraron nodos que coincidan con '{search_text}'.")
            return

        self.highlight_matching_nodes(matching_nodes)


    def find_matching_nodes(self, search_text, parent_node="", matching_nodes=None):
        if matching_nodes is None:
            matching_nodes = []

        for node_id, node_path in self.node_dict.items():
            if node_path.startswith(parent_node) and search_text.lower() in os.path.basename(node_path).lower():
                matching_nodes.append(node_id)

        print(f"Search Text: {search_text}, Matching Nodes: {matching_nodes}")
        return matching_nodes

    
   
    def highlight_matching_nodes(self, matching_nodes):
        for node_id in self.tree.get_children(""):  # Limpiar etiquetas anteriores
            self.tree.item(node_id, tags=())

        for node_id in matching_nodes:
            node_path = self.node_dict[node_id]
            self.expand_path_to_node(node_path)

            parent_id = self.tree.parent(node_id)
            while parent_id != '':
                self.tree.item(parent_id, open=True)
                parent_id = self.tree.parent(parent_id)

            self.tree.item(node_id, tags=("highlight",))
    
    def expand_path_to_node(self, node_path):
        current_path = ""
        parent_item = ""
        for part in os.path.normpath(node_path).split(os.path.sep):
            current_path = os.path.join(current_path, part)
            for node_id, path in self.node_dict.items():
                if path == current_path:
                    parent_item = node_id
                    break

            if not parent_item:
                break

        if parent_item:
            self.tree.item(parent_item, open=True)


    def copy_node(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.copy_data["node_id"] = selected_item[0]
            self.copy_data["node_path"] = self.node_dict[selected_item[0]]
            self.copy_data["cut_mode"] = False
            print(f"Node '{os.path.basename(self.copy_data['node_path'])}' copiado.")

    def cut_node(self):
        selected_item = self.tree.selection()
        if selected_item:
            self.copy_data["node_id"] = selected_item[0]
            self.copy_data["node_path"] = self.node_dict[selected_item[0]]
            self.copy_data["cut_mode"] = True
            print(f"Node '{os.path.basename(self.copy_data['node_path'])}' cortado.")

    def paste_node(self):
        if self.copy_data["node_id"] is not None and self.copy_data["node_path"] is not None:
            destination_item = self.tree.selection()
            if destination_item:
                destination_path = self.node_dict[destination_item[0]]
                destination_path = os.path.join(destination_path, os.path.basename(self.copy_data["node_path"]))

                if os.path.exists(destination_path):
                    print(f"Ya existe un nodo con el nombre '{os.path.basename(destination_path)}'.")
                    return

                try:
                    if self.copy_data["cut_mode"]:
                        # En el modo de corte, mover y luego eliminar el nodo original
                        shutil.move(self.copy_data["node_path"], destination_path)
                        self.delete_item(self.copy_data["node_id"])
                    else:
                        # En el modo de copia, copiar el nodo
                        if os.path.isdir(self.copy_data["node_path"]):
                            shutil.copytree(self.copy_data["node_path"], destination_path)
                        else:
                            shutil.copy2(self.copy_data["node_path"], destination_path)

                        destination_node_id = self.tree.insert(destination_item[0], "end", text=os.path.basename(destination_path))
                        self.node_dict[destination_node_id] = destination_path
                        self.expand_node(destination_node_id)

                    print(f"Node '{os.path.basename(destination_path)}' pegado.")
                except Exception as e:
                    print(f"Error al pegar nodo: {e}")
        else:
            print("No hay nodo para pegar o cortar.")


    def OnDoubleClick(self, event):
        item = self.tree.selection()[0]
        node_path = self.node_dict[item]
        if os.path.isdir(node_path):
            self.expand_node(item)


root = tk.Tk()
root.title("Explorador de archivos")
app = FileExplorer(root)
root.mainloop()








