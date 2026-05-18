
from tkinter import *
from tkinter import filedialog, messagebox
from aircraft import *
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# DATOS GLOBALES de aircrafts y de airports
llista_aeroports = []
llista_vuelos = []

current_canvas = None  # para controlar el gráfico al iniciar, = ninguno

#para Airport.py--------------------------------------------------------------------------------------------------------
def carregar_aeroports():
    global llista_aeroports
    nom_fitxer = filedialog.askopenfilename()
    if nom_fitxer:
        llista_aeroports = LoadAirports(nom_fitxer)
        for a in llista_aeroports:
            SetSchengenAirports(a)
        messagebox.showinfo("Èxit", f"S'han carregat {len(llista_aeroports)} aeroports.")


def generar_kml():
    if llista_aeroports:
        filename = "airports_map.kml"
        MapAirports(llista_aeroports)
        messagebox.showinfo("Mapa", f"Fitxer {filename} generat correctament")
        try:
            os.startfile(filename)  # abre el archivo automáticamente
        except Exception as e:
            messagebox.showerror("Error", f"No s'ha pogut obrir el fitxer: {e}")
    else:
        messagebox.showwarning("Atenció", "Primer has de carregar el fitxer de aeroports.")

def generar_mapa_vuelos():
    if llista_vuelos:
        filename2 = "flight_map.kml"  # assegurar que MapFlights use este nombre o cambiar al que use la función
        MapFlights(llista_vuelos, llista_aeroports)
        try:
            os.startfile(filename2)  # abre el archivo automáticamente
        except Exception as e: #excepto error
            messagebox.showwarning("Avís", f"Mapa generat, però no s'ha pogut obrir automàticament. {e} ")
    else:
        messagebox.showwarning("Atenció", "Primer has de carregar el fitxer de vols i aeroports.")


#para Aircraft.py---------------------------------------------------------------------------------------------------
def carregar_vuelos():
    global llista_vuelos
    nom_fitxer = filedialog.askopenfilename()
    if nom_fitxer:
        llista_vuelos = LoadArrivals(nom_fitxer)
        for a in llista_vuelos:
            SetSchengenAircrafts(a)
        messagebox.showinfo("Èxit", f"S'han carregat {len(llista_vuelos)} vols .")


# Parte de graficos  (EMBED)
def mostrar_figura(fig):
    global current_canvas# que al inicio es none

    # limpiar gráfico anterior
    for widget in graph_frame.winfo_children(): #por todos los elementos que estan dentro de la zona de graficos
        widget.destroy()#destruye esos elementos

    current_canvas = FigureCanvasTkAgg(fig, master=graph_frame)#el grafico sera, dentro del tk, figura, dentro de la zona de graficos
    current_canvas.draw()#muestra el grafico
    current_canvas.get_tk_widget().pack(fill=BOTH, expand=True)#expande el grafico en todos lados y si se modifica las diemnsiones de la pestaña, el grafico tambien


def PlotAirports_embedded():
    fig = PlotAirports(llista_aeroports)  # debe devolver fig
    mostrar_figura(fig)


def PlotArrivals_embedded():
    fig = PlotArrivals(llista_vuelos)
    mostrar_figura(fig)


def PlotAirlines_embedded():
    global llista_vuelos, llista_aeroports
    if not llista_vuelos or not llista_aeroports:
        messagebox.showwarning("Atenció", "Primer has de carregar el fitxer de vols i aeroports.")
        return

    # vaciamos la zona del grafico ya que, como no usamos la funcion de mostar, no se vaciaria automaticamente
    for widget in graph_frame.winfo_children():
        widget.destroy()

    # zonas separadas dentro de la zona de gráficos
    filtro = Frame(graph_frame, width=250, bg="#f0f0f0", relief="sunken", bd=1)#botones de las aerolineas
    filtro.pack(side=LEFT, fill=Y, padx=5, pady=5)#posicion de los botones de las aerolineas

    chart_area = Frame(graph_frame, bg="white")# el grafico
    chart_area.pack(side=RIGHT, expand=True, fill=BOTH)#posicion de donde estara el grafico


    try:
        # Aquí es donde extraemos cada companya de la lista de vuelos
        aerolineas_unicas = sorted(list(set(v.company for v in llista_vuelos)))#saca el nombre de la compañía, una vez, de la lista .
        #sorted, ordena alfabeticamente
        #set, coge solo uno, por si en cualquier caso hay algun repetido

    except AttributeError:
        messagebox.showerror("Error", "No s'ha trobat l'atribut 'company'. Revisa aircraft.py")
        return

    Label(filtro, text="Selecciona Aerolínies:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=5)#titulo del sub apartado de los botones
    # Lista con barra de mov. para seleccionar, si hay muchas aerolineas y no caben
    list_frame = Frame(filtro)
    list_frame.pack(fill=BOTH, expand=True, padx=5)

    barra_mov = Scrollbar(list_frame)#scroll bar es la funcion de la barra para moverse
    barra_mov.pack(side=RIGHT, fill=Y)

    lat_bar = Listbox(list_frame, selectmode=MULTIPLE, yscrollcommand=barra_mov.set, exportselection=False)
    #exportselection, para q no se borre la seleccion al clicar otro boton
    for c in aerolineas_unicas:#coge cada aerolinea
        lat_bar.insert(END, c)#inserta en la barra lateral las aerolineas
    lat_bar.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0))
    barra_mov.config(command=lat_bar.yview)# si se mueve la barra de mov, que se mueva la lista

    #es una función interna para el filtro y el grafico
    def aplicar_filtro():
        indices = lat_bar.curselection()#guarda la posicion de la seleccion que escogamos en la barra

        seleccionadas = [lat_bar.get(i) for i in indices]#coge la posicion de lo q hemos seleccionado y extrae y guarda lo que haya en esa posicon

        if not seleccionadas:
            messagebox.showwarning("Atenció", "Selecciona almenys una companyia.")
            return

        #filtramos la lista
        vuelos_filtrados = [v for v in llista_vuelos if v.company in seleccionadas]#coge las compañias que esten en la lista de seleccionadas qye esten en la lista de vyelos y las guarda

        # llamamos a la función que muestra la funciion
        fig = PlotAirlines(vuelos_filtrados)

        # volvemos a limpiamos el área del gráfico anterior
        for widget in chart_area.winfo_children():
            widget.destroy()

        # insertamos el nuevo gráfico
        canvas = FigureCanvasTkAgg(fig, master=chart_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    # botón para ejecutar el filtro
    boton_filtro = Button(filtro, text="MOSTRAR GRÀFIC", command=aplicar_filtro, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), pady=10)
    boton_filtro.pack(fill=X, padx=10, pady=10)


    Label(chart_area, text="<-- Selecciona les companyies i clica el botó", font=("Arial", 12), bg="white").pack(expand=True)


def PlotFlightsType_embedded():
    fig = PlotFlightsType(llista_vuelos)
    mostrar_figura(fig)


def clear_graph():
    for widget in graph_frame.winfo_children():
        widget.destroy()
    Label(graph_frame, text="(Aquí aparecerán los gráficos)", font=("Arial", 14)).pack(expand=True)



# interfaz grafica
window = Tk()
window.title("EETAC Dashboard")
window.geometry("1600x1000")

window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)  # panel  para botones, etc
window.columnconfigure(1, weight=3)# zona de gráficos




# zona donde esta el grafico (zona lateral)

graph_frame = Frame(window, bg="white", relief="solid", bd=2)#relief soft significa q tendra borde delimitado
graph_frame.grid(row=0, column=1, sticky="nsew")
graph_frame.grid_propagate(False)# evita que se propague todo aquello que usando grid sea mayor
graph_frame.pack_propagate(False)# evita que se propague todo aquello que usando pack sea mayor

# parte inferior
bottom_frame = Frame(window)
bottom_frame.grid(row=0, column=0, sticky="nsew")

bottom_frame.columnconfigure(0, weight=1)
bottom_frame.rowconfigure(0, weight=1)
bottom_frame.rowconfigure(1, weight=1)
bottom_frame.rowconfigure(2, weight=1)



# subtema de descargar archivos
download_frame = LabelFrame(bottom_frame, text="Descarregar archius", padx=10, pady=10)
download_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

Button(download_frame, text="Carregar base d'aeroports", command=carregar_aeroports).pack(fill=X,pady = 4, ipady=16)
Button(download_frame, text="Carregar vols diaris", command=carregar_vuelos).pack(fill=X,pady = 4, ipady=16)
Button(download_frame, text="Localització Google Earth", command=generar_kml).pack(fill=X,pady = 4, ipady=16)
Button(download_frame, text="Veure recorregut Google Earth", command=generar_mapa_vuelos).pack(fill=X, pady=4, ipady=5)

# subtema de botones
charts_frame = LabelFrame(bottom_frame, text="Botons", padx=10, pady=10)
charts_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

Button(charts_frame, text="Veure Estadístiques", command=PlotAirports_embedded).pack(fill=X,pady = 4, ipady=16)
Button(charts_frame, text="Mostrar Histograma Horari", command=PlotArrivals_embedded).pack(fill=X,pady = 4, ipady=16)
Button(charts_frame, text="Gràfic per Aerolínia", command=PlotAirlines_embedded).pack(fill=X,pady = 4, ipady=16)
Button(charts_frame, text="Vols procedents de països Schengen", command=PlotFlightsType_embedded).pack(fill=X,pady = 4, ipady=16)
Button(charts_frame, text="Vuidar grafic", command=clear_graph).pack(fill=X,pady = 4, ipady=16)


# SALIR
exit_frame = Frame(bottom_frame)
exit_frame.grid(row=2, column=0, sticky="sw")

Button(exit_frame, text="Sortir", bg="red", fg="white", command=window.destroy).pack(anchor="sw")#lugar de posicion  sur-este


# iniciar vacío
clear_graph()

window.mainloop()