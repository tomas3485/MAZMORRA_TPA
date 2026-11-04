# interfaz grafica (tkinter). Solo habla con Juego, no conoce el generador ni los ficheros..
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from .juego import Juego
from .modelo import ErrorMazmorra

# colores
FONDO = "#1b1830"
PANEL = "#26223f"
PANEL2 = "#322d52"
TEXTO = "#ece8f8"
APAGADO = "#8f89b0"
ORO = "#e3a82f"
ROJO = "#e05a55"
VERDE = "#5fbf7a"


class App:
    def __init__(self, ventana: tk.Tk, juego: Juego):
        self.ventana = ventana
        self.juego = juego
        ventana.title("Mazmorras olvidadas")
        ventana.geometry("1020x680")
        ventana.minsize(900, 600)
        ventana.configure(bg=FONDO)

        # variables de control del panel del personaje
        self.nombre_var = tk.StringVar()
        self.nivel_var = tk.StringVar()
        self.vida_var = tk.StringVar()
        self.barra_var = tk.DoubleVar()
        self.ataque_var = tk.StringVar()
        self.defensa_var = tk.StringVar()
        self.arma_var = tk.StringVar()
        self.oro_var = tk.StringVar()
        self.completadas_var = tk.StringVar()

        self._estilos()
        self._crear_widgets()
        self.juego.suscribir(self.escribir_log)

        # eventos
        self.lista_mazmorras.bind("<<ListboxSelect>>", lambda e: self._mostrar_salas())
        self.lista_mazmorras.bind("<Double-Button-1>", lambda e: self.entrar())
        ventana.bind("<Return>", lambda e: self.entrar())
        ventana.protocol("WM_DELETE_WINDOW", self.cerrar)  # guardar al cerrar

        # se arranca ya dentro del mainloop para poder cerrar la ventana si se cancela el nombre
        ventana.after(100, self._arrancar)

    # ------------------------------------------------------------ aspecto
    def _estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "TButton", background=PANEL2, foreground=TEXTO, padding=(12, 8), borderwidth=0, focusthickness=0
        )
        estilo.map("TButton", background=[("active", "#443d70")])
        estilo.configure(
            "Accion.TButton", background=ORO, foreground="#1b1830", font=("Segoe UI", 10, "bold")
        )
        estilo.map("Accion.TButton", background=[("active", "#f2bd52")])
        for nombre, color in (("Vida", VERDE), ("VidaBaja", ROJO)):
            estilo.configure(
                f"{nombre}.Horizontal.TProgressbar",
                troughcolor=PANEL2,
                background=color,
                bordercolor=PANEL,
                lightcolor=color,
                darkcolor=color,
            )

    def _panel(self, titulo: str) -> tk.Frame:
        marco = tk.Frame(self.ventana, bg=PANEL, padx=14, pady=10)
        tk.Label(marco, text=titulo.upper(), bg=PANEL, fg=ORO, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Frame(marco, bg=ORO, height=1).pack(fill="x", pady=(3, 8))
        return marco

    def _lista(self, padre) -> tk.Listbox:
        return tk.Listbox(
            padre,
            bg=PANEL2,
            fg=TEXTO,
            selectbackground=ORO,
            selectforeground="#1b1830",
            highlightthickness=0,
            borderwidth=0,
            activestyle="none",
            exportselection=False,
            font=("Segoe UI", 10),
        )

    def _crear_widgets(self):
        v = self.ventana
        v.columnconfigure(0, weight=0)
        v.columnconfigure(1, weight=1)
        v.columnconfigure(2, weight=2)
        v.rowconfigure(1, weight=3)
        v.rowconfigure(2, weight=2)

        tk.Label(v, text="MAZMORRAS OLVIDADAS", bg=FONDO, fg=ORO, font=("Georgia", 22, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(12, 6)
        )

        # panel del personaje: siempre visible a la izquierda
        pj = self._panel("Personaje")
        pj.grid(row=1, column=0, rowspan=2, sticky="ns", padx=(14, 7), pady=7)
        tk.Label(pj, textvariable=self.nombre_var, bg=PANEL, fg=TEXTO, font=("Georgia", 16, "bold")).pack(anchor="w")
        tk.Label(pj, textvariable=self.nivel_var, bg=PANEL, fg=APAGADO).pack(anchor="w", pady=(0, 10))
        tk.Label(pj, textvariable=self.vida_var, bg=PANEL, fg=TEXTO, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.barra = ttk.Progressbar(
            pj, variable=self.barra_var, maximum=100, style="Vida.Horizontal.TProgressbar", length=210
        )
        self.barra.pack(anchor="w", pady=(2, 10))
        for variable in (self.ataque_var, self.defensa_var, self.arma_var, self.oro_var, self.completadas_var):
            tk.Label(
                pj, textvariable=variable, bg=PANEL, fg=TEXTO, font=("Segoe UI", 11), wraplength=210, justify="left"
            ).pack(anchor="w", pady=3)

        # mazmorras pendientes
        izq = self._panel("Mazmorras pendientes")
        izq.grid(row=1, column=1, sticky="nsew", padx=7, pady=7)
        self.lista_mazmorras = self._lista(izq)
        self.lista_mazmorras.pack(fill="both", expand=True)

        # salas de la mazmorra seleccionada
        der = self._panel("Salas")
        der.grid(row=1, column=2, sticky="nsew", padx=(7, 14), pady=7)
        self.lista_salas = self._lista(der)
        self.lista_salas.pack(fill="both", expand=True)

        # registro de lo que pasa
        reg = self._panel("Registro")
        reg.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=(7, 14), pady=7)
        self.log = tk.Text(
            reg, height=7, bg=PANEL2, fg=TEXTO, relief="flat", wrap="word", state="disabled", font=("Consolas", 10)
        )
        self.log.pack(fill="both", expand=True)
        self.log.tag_configure("malo", foreground=ROJO)
        self.log.tag_configure("bueno", foreground=ORO)

        # botones
        barra = tk.Frame(v, bg=FONDO)
        barra.grid(row=3, column=0, columnspan=3, sticky="ew", padx=14, pady=(4, 12))
        ttk.Button(barra, text="Entrar en la siguiente sala", style="Accion.TButton", command=self.entrar).pack(
            side="left"
        )
        ttk.Button(barra, text="Generar mazmorra", command=self.generar).pack(side="left", padx=8)
        ttk.Button(barra, text="Nueva partida", command=self.nueva_partida).pack(side="left")
        ttk.Button(barra, text="Exportar", command=self.exportar).pack(side="right")
        ttk.Button(barra, text="Guardar", command=self.guardar).pack(side="right", padx=8)

    # ------------------------------------------------------------ arranque
    def _arrancar(self):
        if os.path.exists(self.juego.ruta) and messagebox.askyesno(
            "Partida guardada", "Hay una partida guardada. ¿Quieres continuarla?", parent=self.ventana
        ):
            try:
                if self.juego.cargar():
                    self.refrescar()
                    return
            except ErrorMazmorra as error:
                messagebox.showerror(
                    "Error al cargar", f"{error}\n\nSe empezará una partida nueva.", parent=self.ventana
                )
        if not self._empezar():
            self.ventana.destroy()

    def _pedir_nombre(self):
        # al empezar se pregunta el nombre del personaje (no puede estar vacio)
        while True:
            nombre = simpledialog.askstring("Tu personaje", "¿Cómo se llama tu personaje?", parent=self.ventana)
            if nombre is None:
                return None
            if nombre.strip():
                return nombre.strip()[:20]
            messagebox.showwarning("Nombre no válido", "El nombre no puede estar vacío.", parent=self.ventana)

    def _empezar(self) -> bool:
        nombre = self._pedir_nombre()
        if nombre is None:
            return False
        self.juego.nueva_partida(nombre)
        self.refrescar()
        return True

    def nueva_partida(self):
        if messagebox.askyesno(
            "Nueva partida", "Se empezará de cero (la partida guardada se sobrescribe al guardar). ¿Seguro?"
        ):
            self._empezar()

    # ------------------------------------------------------------ pintar
    def refrescar(self):
        p = self.juego.personaje
        self.nombre_var.set(p.nombre)
        self.nivel_var.set(f"Nivel {self.juego.nivel}")
        self.vida_var.set(f"Vida  {p.vida} / {p.vida_max}")
        self.barra_var.set(100 * p.vida / p.vida_max)
        baja = p.vida < p.vida_max * 0.3
        self.barra.configure(style="VidaBaja.Horizontal.TProgressbar" if baja else "Vida.Horizontal.TProgressbar")
        bonus = p.ataque_total - p.ataque
        self.ataque_var.set(f"Ataque   {p.ataque}" + (f"  (+{bonus} del arma)" if bonus else ""))
        self.defensa_var.set(f"Defensa  {p.defensa}")
        arma = p.objeto_equipado
        self.arma_var.set(f"Arma: {arma.nombre_o} (+{arma.bonus})" if arma else "Arma: ninguna")
        self.oro_var.set(f"Oro  {p.oro:.2f}")
        self.completadas_var.set(f"Mazmorras completadas: {self.juego.completadas}")

        seleccion = self.lista_mazmorras.curselection()
        previa = seleccion[0] if seleccion else 0
        self.lista_mazmorras.delete(0, tk.END)
        for m in self.juego.campana.mazmorras:
            self.lista_mazmorras.insert(tk.END, f"{m.nombre_m}   [{m.progreso}/{len(m.salas)}]")
        if self.juego.campana.mazmorras:
            self.lista_mazmorras.selection_set(min(previa, len(self.juego.campana.mazmorras) - 1))
        self._mostrar_salas()

    def _mostrar_salas(self):
        self.lista_salas.delete(0, tk.END)
        seleccion = self.lista_mazmorras.curselection()
        if not seleccion:
            return
        mazmorra = self.juego.campana.mazmorras[seleccion[0]]
        for i, sala in enumerate(mazmorra.salas):
            if i < mazmorra.progreso:
                texto, color = f"✔  Sala {i}: {sala.tipo} (superada)", VERDE
            elif i == mazmorra.progreso:
                # de la sala actual se enseña lo que hay dentro, de las siguientes no
                if sala.enemigos:
                    e = sala.enemigos[0]
                    detalle = f"{e.nombre} (vida {e.vida}, ataque {e.ataque}, defensa {e.defensa})"
                elif sala.objetos:
                    detalle = "hay un objeto"
                else:
                    detalle = sala.tipo
                texto, color = f"▶  Sala {i}: {detalle}", ORO
            else:
                texto, color = f"·  Sala {i}: ???", APAGADO
            self.lista_salas.insert(tk.END, texto)
            self.lista_salas.itemconfig(i, foreground=color)

    def escribir_log(self, texto: str):
        # el juego avisa de cada cosa que pasa y aqui se pinta
        etiqueta = ("malo",) if "Has caído" in texto else ("bueno",) if "completada" in texto else ()
        self.log.configure(state="normal")
        self.log.insert("end", texto + "\n", etiqueta)
        self.log.see("end")
        self.log.configure(state="disabled")

    # ------------------------------------------------------------ acciones
    def _indice(self):
        seleccion = self.lista_mazmorras.curselection()
        if not seleccion:
            messagebox.showinfo("Mazmorras", "No hay ninguna mazmorra seleccionada. Pulsa Generar mazmorra.")
            return None
        return seleccion[0]

    def preguntar_equipar(self, objeto) -> bool:
        # siempre se pregunta, y solo se puede llevar un objeto
        actual = self.juego.personaje.objeto_equipado
        texto = f"Has encontrado: {objeto.nombre_o} (+{objeto.bonus} ataque)\n{objeto.descripcion_o}\n\n"
        if actual:
            texto += f"Ahora llevas {actual.nombre_o} (+{actual.bonus}). Si te equipas con este lo perderás.\n\n"
        else:
            texto += "No llevas ningún objeto.\n\n"
        return messagebox.askyesno("Objeto encontrado", texto + "¿Quieres equiparte con él?", parent=self.ventana)

    def entrar(self):
        indice = self._indice()
        if indice is None:
            return
        nombre = self.juego.campana.mazmorras[indice].nombre_m
        try:
            estado = self.juego.avanzar(indice, self.preguntar_equipar)
        except ErrorMazmorra as error:
            messagebox.showerror("No se puede entrar", str(error), parent=self.ventana)
            return
        self.refrescar()
        if estado == "derrota":
            messagebox.showwarning("Derrota", f"Has caído. {nombre} vuelve a empezar.", parent=self.ventana)
        elif estado == "completada":
            messagebox.showinfo("¡Mazmorra completada!", f"Has completado {nombre}.", parent=self.ventana)

    def generar(self):
        try:
            self.juego.generar_mazmorra()
        except ErrorMazmorra as error:
            messagebox.showinfo("Generar mazmorra", str(error), parent=self.ventana)
            return
        self.refrescar()

    # ------------------------------------------------------------ guardar / exportar / cerrar
    def guardar(self) -> bool:
        try:
            self.juego.guardar()
        except ErrorMazmorra as error:
            messagebox.showerror("No se pudo guardar", str(error), parent=self.ventana)
            return False
        self.escribir_log(f"Partida guardada en {self.juego.ruta}")
        return True

    def exportar(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown", "*.md")])
        if not ruta:
            return
        try:
            self.juego.exportar("md", ruta)
        except ErrorMazmorra as error:
            messagebox.showerror("No se pudo exportar", str(error), parent=self.ventana)
            return
        self.escribir_log(f"Mazmorras exportadas a {ruta}")

    def cerrar(self):
        # sin personaje (nombre cancelado al empezar) no hay nada que guardar
        if self.juego.personaje is None or self.guardar():
            self.ventana.destroy()
        elif messagebox.askyesno("Cerrar", "No se ha podido guardar. ¿Cerrar igualmente?"):
            self.ventana.destroy()


def lanzar(juego: Juego | None = None):
    ventana = tk.Tk()
    App(ventana, juego or Juego())
    ventana.mainloop()
