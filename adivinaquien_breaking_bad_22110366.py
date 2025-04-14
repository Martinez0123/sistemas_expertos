import json
import os
import math
from tkinter import *
from tkinter import messagebox, simpledialog, ttk
from typing import Dict, List, Optional, Tuple, Union

class Nodo:
    def __init__(self, atributo: str = None, valor: str = None, personaje: Dict = None):
        self.atributo = atributo
        self.valor = valor
        self.personaje = personaje
        self.si = None
        self.no = None

class AdivinaQuienGoT:
    ATRIBUTOS_DISPONIBLES = [
    "género",         # masculino / femenino
    "ocupación",      # químico, abogado, narcotraficante, etc.
    "vivo",           # True / False
    "alias",          # Heisenberg, etc.
    "afiliación",     # Cártel de Juárez, Pollos Hermanos, DEA, etc.
    "ubicación",      # Albuquerque, México, etc.
    "estatus",        # activo, prófugo, muerto
    "relación"        # pareja de, padre de, socio de, etc.
]

    ESTILOS = {
        'TFrame': {'background': '#0e0e0e'},
        'TLabel': {'background': '#0e0e0e', 'foreground': '#d3a625', 'font': ('Helvetica', 12)},
        'Title.TLabel': {'font': ('Game of Thrones', 24, 'bold'), 'foreground': '#d3a625'},
        'Game.TButton': {
            'font': ('Helvetica', 14, 'bold'),
            'foreground': '#d3a625',
            'background': '#1a1a1a',
            'borderwidth': 3,
            'relief': 'raised'
        },
        'Dialog.TFrame': {'background': '#1a1a1a'},
        'Dialog.TLabel': {'background': '#1a1a1a', 'foreground': '#d3a625'},
        'Dialog.TEntry': {'fieldbackground': '#2a2a2a', 'foreground': 'white'}
    }

    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Adivina Quién - BREAKING BAD")
        self.root.geometry("800x600")
        self.root.configure(bg="#0e0e0e")
        
        self.personajes: List[Dict] = []
        self.archivo_json = "personajes_db.json"
        self.raiz: Optional[Nodo] = None
        
        self._cargar_recursos()
        self._configurar_estilos()
        self._cargar_base_datos()
        self._configurar_interfaz_principal()

    def _cargar_recursos(self):
        """Carga imágenes y recursos visuales"""
        self.bg_image = self._cargar_imagen("got_bg.png")
        self.logo_image = self._cargar_imagen("got_logo.png")
        
    def _cargar_imagen(self, ruta: str) -> Optional[PhotoImage]:
        """Intenta cargar una imagen, devuelve None si falla"""
        try:
            return PhotoImage(file=ruta) if os.path.exists(ruta) else None
        except Exception:
            return None

    def _configurar_estilos(self):
        """Configura los estilos de la interfaz"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        for estilo, config in self.ESTILOS.items():
            self.style.configure(estilo, **config)
        
        self.style.map('Game.TButton',
            foreground=[('active', '#d3a625'), ('pressed', '#d3a625')],
            background=[('active', '#2a2a2a'), ('pressed', '#1a1a1a')]
        )

    def _configurar_interfaz_principal(self):
        """Configura la interfaz principal del juego"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True)
        
        if self.bg_image:
            Label(self.main_frame, image=self.bg_image).place(x=0, y=0, relwidth=1, relheight=1)
        
        center_frame = ttk.Frame(self.main_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        if self.logo_image:
            Label(center_frame, image=self.logo_image, bg='#0e0e0e').pack(pady=(0, 30))
        else:
            ttk.Label(center_frame, text="Adivina Quién", style='Title.TLabel').pack(pady=(0, 30))
            ttk.Label(center_frame, text="BREAKING BAD", style='Title.TLabel').pack(pady=(0, 30))
        
        botones = [
            ("Jugar", self.iniciar_juego),
            ("Añadir Personaje", self.mostrar_agregar_personaje),
            ("Salir", self.root.quit)
        ]
        
        for texto, comando in botones:
            ttk.Button(
                center_frame,
                text=texto,
                style='Game.TButton',
                command=comando
            ).pack(fill=X, pady=10, ipady=10)

    def _cargar_base_datos(self):
        """Carga la base de datos de personajes"""
        if not os.path.exists(self.archivo_json):
            self.personajes = []
            self._guardar_base_datos()
        else:
            try:
                with open(self.archivo_json, 'r', encoding='utf-8') as f:
                    self.personajes = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la base de datos: {str(e)}")
                self.personajes = []

    def _guardar_base_datos(self):
        """Guarda la base de datos de personajes"""
        with open(self.archivo_json, 'w', encoding='utf-8') as f:
            json.dump(self.personajes, f, ensure_ascii=False, indent=2)

    def iniciar_juego(self):
        """Inicia el juego principal"""
        if not self.personajes:
            self._mostrar_dialogo("No hay personajes", "Primero añade algunos personajes para jugar.")
            return
        
        self._construir_arbol_decision()
        self._jugar(self.raiz)

    def _construir_arbol_decision(self):
        """Construye el árbol de decisión"""
        self.raiz = self._construir_nodo(self.personajes.copy())

    def _construir_nodo(self, personajes: List[Dict], profundidad: int = 0) -> Nodo:
        """Construye recursivamente los nodos del árbol de decisión"""
        if len(personajes) == 1:
            return Nodo(personaje=personajes[0])
        
        atributo, valor, ganancia = self._mejor_atributo(personajes)
        
        if atributo is None or ganancia < 0.1:
            return Nodo(personaje=self._personaje_mas_comun(personajes))
        
        nodo = Nodo(atributo=atributo, valor=valor)
        si_personajes = [p for p in personajes if str(p["atributos"].get(atributo, "")).lower() == str(valor).lower()]
        no_personajes = [p for p in personajes if str(p["atributos"].get(atributo, "")).lower() != str(valor).lower()]
        
        if not si_personajes or not no_personajes:
            return Nodo(personaje=self._personaje_mas_comun(personajes))
        
        nodo.si = self._construir_nodo(si_personajes, profundidad + 1)
        nodo.no = self._construir_nodo(no_personajes, profundidad + 1)
        
        return nodo

    def _mejor_atributo(self, personajes: List[Dict]) -> Tuple[Optional[str], Optional[str], float]:
        """Encuentra el mejor atributo para dividir los personajes"""
        mejor_atributo, mejor_valor, mejor_ganancia = None, None, -1
        
        for atributo in self.ATRIBUTOS_DISPONIBLES:
            valores = {str(p["atributos"].get(atributo, "")) for p in personajes if p["atributos"].get(atributo)}
            
            if len(valores) < 2:
                continue
                
            for valor in valores:
                ganancia = self._calcular_ganancia(personajes, atributo, valor)
                if ganancia > mejor_ganancia:
                    mejor_atributo, mejor_valor, mejor_ganancia = atributo, valor, ganancia
        
        return mejor_atributo, mejor_valor, mejor_ganancia

    def _calcular_ganancia(self, personajes: List[Dict], atributo: str, valor: str) -> float:
        """Calcula la ganancia de información para un atributo y valor"""
        si_personajes = [p for p in personajes if str(p["atributos"].get(atributo, "")).lower() == str(valor).lower()]
        no_personajes = [p for p in personajes if str(p["atributos"].get(atributo, "")).lower() != str(valor).lower()]
        
        entropia_inicial = self._calcular_entropia(personajes)
        peso_si, peso_no = len(si_personajes)/len(personajes), len(no_personajes)/len(personajes)
        entropia_posterior = (peso_si * self._calcular_entropia(si_personajes)) + (peso_no * self._calcular_entropia(no_personajes))
        
        return entropia_inicial - entropia_posterior

    def _calcular_entropia(self, personajes: List[Dict]) -> float:
        """Calcula la entropía de un conjunto de personajes"""
        if not personajes:
            return 0.0
            
        conteo = {}
        for p in personajes:
            conteo[p["nombre"]] = conteo.get(p["nombre"], 0) + 1
        
        total = len(personajes)
        return -sum((count/total) * math.log2(count/total) for count in conteo.values())

    def _personaje_mas_comun(self, personajes: List[Dict]) -> str:
        """Devuelve el nombre del personaje más común en la lista"""
        conteo = {}
        for p in personajes:
            conteo[p["nombre"]] = conteo.get(p["nombre"], 0) + 1
        return max(conteo.items(), key=lambda x: x[1])[0]

    def _formatear_pregunta(self, atributo: str, valor: str) -> str:
        """Formatea una pregunta legible para el usuario"""
        formatos = {
    "vivo": "sigue con vida",
    "género": f"es de género {valor}",
    "ocupación": f"trabaja como {valor}",
    "afiliación": f"está relacionado con {valor}",
    "alias": f"es conocido como '{valor}'",
    "ubicación": f"suele estar en {valor}",
    "estatus": f"actualmente está {valor}",
    "apariencia": f"tiene una apariencia de {valor}",
    "relación": f"tiene una relación con {valor}"
}

        return formatos.get(atributo, f"tiene {atributo} = {valor}")

    def _jugar(self, nodo: Nodo):
        """Maneja la lógica principal del juego"""
        if nodo.personaje:
            respuesta = self._mostrar_pregunta(
                "¿Es este tu personaje?", 
                f"¿Tu personaje es {nodo.personaje['nombre']}?",
                ("Sí", "No")
            )
            
            if respuesta == "Sí":
                self._mostrar_info_personaje(nodo.personaje)
            else:
                self._agregar_nuevo_personaje(nodo)
        else:
            pregunta = (
                "¿Tu personaje está vivo?" if nodo.atributo == "vivo" else
                f"¿Tu personaje {self._formatear_pregunta(nodo.atributo, nodo.valor)}?"
            )
            
            respuesta = self._mostrar_pregunta("Adivina Quién - BREAKING BAD", pregunta, ("Sí", "No"))
            
            siguiente_nodo = nodo.si if (respuesta == "Sí" and (nodo.atributo != "vivo" or nodo.valor == "si")) else nodo.no
            self._jugar(siguiente_nodo)

    # Métodos de interfaz gráfica (optimizados para reutilización)
    def _crear_ventana_modal(self, titulo: str, tamaño: str = "400x200") -> Toplevel:
        """Crea una ventana modal con estilo consistente"""
        ventana = Toplevel(self.root)
        ventana.title(titulo)
        ventana.geometry(tamaño)
        ventana.configure(bg="#1a1a1a")
        ventana.grab_set()
        return ventana

    def _mostrar_pregunta(self, titulo: str, mensaje: str, opciones: Tuple[str]) -> str:
        """Muestra una pregunta con opciones y devuelve la respuesta"""
        ventana = self._crear_ventana_modal(titulo)
        resultado = [None]
        
        frame = ttk.Frame(ventana, style='Dialog.TFrame')
        frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text=mensaje, style='Dialog.TLabel', wraplength=350).pack(pady=20)
        
        btn_frame = ttk.Frame(frame, style='Dialog.TFrame')
        btn_frame.pack(fill=X, pady=10)
        
        for opcion in opciones:
            ttk.Button(
                btn_frame, 
                text=opcion, 
                style='Game.TButton',
                command=lambda r=opcion: self._cerrar_dialogo(ventana, resultado, r)
            ).pack(side=LEFT, expand=True, padx=5)
        
        self.root.wait_window(ventana)
        return resultado[0]

    def _cerrar_dialogo(self, ventana: Toplevel, resultado: list, valor: str):
        """Cierra un diálogo y guarda el resultado"""
        resultado[0] = valor
        ventana.destroy()

    def _mostrar_dialogo(self, titulo: str, mensaje: str):
        """Muestra un diálogo simple con un mensaje"""
        ventana = self._crear_ventana_modal(titulo)
        
        frame = ttk.Frame(ventana, style='Dialog.TFrame')
        frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text=mensaje, style='Dialog.TLabel', wraplength=350).pack(expand=True)
        ttk.Button(frame, text="Aceptar", style='Game.TButton', command=ventana.destroy).pack(pady=20)

    def _mostrar_info_personaje(self, personaje: Dict):
        """Muestra la información de un personaje"""
        ventana = self._crear_ventana_modal(f"Personaje: {personaje['nombre']}", "500x400")
        
        frame = ttk.Frame(ventana, style='Dialog.TFrame')
        frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text=personaje['nombre'], style='Title.TLabel').pack(pady=10)
        
        for atributo, valor in personaje['atributos'].items():
            row = ttk.Frame(frame, style='Dialog.TFrame')
            row.pack(fill=X, pady=5)
            ttk.Label(row, text=f"{atributo.capitalize()}:", style='Dialog.TLabel', width=15).pack(side=LEFT)
            ttk.Label(row, text=valor, style='Dialog.TLabel').pack(side=LEFT, padx=10)
        
        ttk.Button(frame, text="Cerrar", style='Game.TButton', command=ventana.destroy).pack(pady=20)

    def mostrar_agregar_personaje(self):
        """Muestra el formulario para agregar un nuevo personaje"""
        self._mostrar_formulario_personaje(
            "Añadir Nuevo Personaje",
            lambda n, a: self._guardar_personaje(n, a)
        )

    def _agregar_nuevo_personaje(self, nodo: Nodo):
        """Muestra el formulario para agregar un personaje no reconocido"""
        def guardar_y_actualizar(nombre: str, atributos: Dict):
            pregunta = simpledialog.askstring(
                "Nueva Pregunta",
                f"¿Qué pregunta distinguiría a {nombre} de {nodo.personaje['nombre']}?",
                parent=self.root
            )
            
            if not pregunta:
                self._mostrar_dialogo("Error", "Debes proporcionar una pregunta diferenciadora.")
                return False
            
            respuesta = self._mostrar_pregunta(
                "Respuesta",
                f"Para {nombre}, la respuesta sería ¿Sí?",
                ("Sí", "No")
            )
            
            personaje_antiguo = nodo.personaje
            nodo.personaje = None
            nodo.atributo = "pregunta"
            nodo.valor = pregunta
            
            if respuesta == "Sí":
                nodo.si = Nodo(personaje={"nombre": nombre, "atributos": atributos})
                nodo.no = Nodo(personaje=personaje_antiguo)
            else:
                nodo.si = Nodo(personaje=personaje_antiguo)
                nodo.no = Nodo(personaje={"nombre": nombre, "atributos": atributos})
            
            return True
        
        self._mostrar_formulario_personaje(
            "Nuevo Personaje",
            lambda n, a: guardar_y_actualizar(n, a) and self._guardar_personaje(n, a, "Aprendido", f"¡He aprendido sobre {n}! ¡Gracias!")
        )

    def _mostrar_formulario_personaje(self, titulo: str, comando_guardar):
        """Muestra un formulario genérico para agregar/editar personajes"""
        ventana = self._crear_ventana_modal(titulo, "500x500")
        
        nombre_var = StringVar()
        atributos_vars = {a: StringVar() for a in self.ATRIBUTOS_DISPONIBLES}
        
        frame = ttk.Frame(ventana, style='Dialog.TFrame')
        frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text=titulo, style='Title.TLabel').pack(pady=10)
        ttk.Label(frame, text="Nombre:", style='Dialog.TLabel').pack(anchor=W, pady=5)
        ttk.Entry(frame, textvariable=nombre_var, style='Dialog.TEntry').pack(fill=X, pady=5)
        
        ttk.Label(frame, text="Atributos:", style='Dialog.TLabel').pack(anchor=W, pady=10)
        
        for atributo in self.ATRIBUTOS_DISPONIBLES:
            row = ttk.Frame(frame, style='Dialog.TFrame')
            row.pack(fill=X, pady=5)
            ttk.Label(row, text=f"{atributo.capitalize()}:", style='Dialog.TLabel', width=15).pack(side=LEFT)
            ttk.Entry(row, textvariable=atributos_vars[atributo], style='Dialog.TEntry').pack(side=LEFT, expand=True, fill=X)
        
        btn_frame = ttk.Frame(frame, style='Dialog.TFrame')
        btn_frame.pack(fill=X, pady=20)
        
        ttk.Button(btn_frame, text="Cancelar", style='Game.TButton', command=ventana.destroy).pack(side=LEFT, expand=True, padx=5)
        ttk.Button(btn_frame, text="Guardar", style='Game.TButton', command=lambda: self._procesar_formulario(
            nombre_var, atributos_vars, ventana, comando_guardar
        )).pack(side=LEFT, expand=True, padx=5)

    def _procesar_formulario(self, nombre_var: StringVar, atributos_vars: Dict[str, StringVar], ventana: Toplevel, comando_guardar):
        """Procesa el formulario de personaje"""
        nombre = nombre_var.get().strip()
        if not nombre:
            self._mostrar_dialogo("Error", "El nombre no puede estar vacío.")
            return
        
        atributos = {
            a: v.get().strip() 
            for a, v in atributos_vars.items() 
            if v.get().strip()
        }
        
        if comando_guardar(nombre, atributos):
            ventana.destroy()

    def _guardar_personaje(self, nombre: str, atributos: Dict, titulo: str = "Éxito", mensaje: str = None):
        """Guarda un nuevo personaje en la base de datos"""
        self.personajes.append({
            "nombre": nombre,
            "atributos": atributos
        })
        self._guardar_base_datos()
        self._mostrar_dialogo(titulo, mensaje or f"Personaje '{nombre}' añadido correctamente.")
        return True

if __name__ == "__main__":
    root = Tk()
    app = AdivinaQuienGoT(root)
    
    if os.path.exists("got_icon.ico"):
        root.iconbitmap("got_icon.ico")
    
    root.mainloop()