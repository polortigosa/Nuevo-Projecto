
from aircraft import *

class BarcelonaAP:
    def __init__(self, code):
        self.code = code
        self.terminals = []

class Terminal:
    def __init__(self, name):
        self.name = name
        self.boarding_areas = []
        self.airlines = []

class BoardingArea:
    def __init__(self, name, type):
        self.name = name
        self.type = type #si es schengen o no
        self.gates = []

class Gate:
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft_id =""

def SetGates (area, init_gate, end_gate, prefix):
    if end_gate <= init_gate:
        return -1

    area.gates = []#lista de las puertas

    for number in range(init_gate, end_gate + 1): # +1 porque en el range no se tiene en cuenta el ultimio valor
        gate_name = f"{prefix}{number}"# el nombe de cada puerta
        gate = Gate(gate_name)
        area.gates.append(gate)# mete en una lista, las peurtas que hay metiendo en la lista toda la informacion en la clase
    return 0

def LoadAirlines (terminal, t_name):
    filename = f"{t_name}_Airlines.txt" #para que abra el archivo de la terminal determinada T1 /T2

    try:
        file = open(filename, "r")
    except FileNotFoundError:
        return -1

    airlines_temp = []

    for line in file: #quue ela cada linea del archivo y que elimine espacios y saltos de linea
        line = line.strip()
        if line == "": #si esta vacia
            continue
        parts = line.split()
        airline_code = parts[-1]# ICAO code siempre esta al final
        airlines_temp.append(airline_code)
    file.close()
    terminal.airlines = airlines_temp
    return 0

def LoadAirportStructure (filename):
    try:
        file = open(filename, "r")
    except FileNotFoundError:
        return -1

    first_line = file.readline().strip().split()
    airport_code = first_line[0]
    bcn = BarcelonaAP(airport_code)# es bcn porque sabemos que el codigo de aeropuerto en este caso es LEBL que es el de bcn
    lines = file.readlines()

    i = 0
    while i < len(lines):
        parts = lines[i].strip().split()
        if parts[0] == "Terminal":
            terminal_name = parts[1] #guarda el nombre de la terminal T1/T2
            num_areas = int(parts[2]) #guarda cuantas areas tiene
            terminal = Terminal(terminal_name) #mete la info guardada en la clase

            LoadAirlines(terminal, terminal_name) #ejecuta la funcion para leer el archivo correspondiente a esa terminal

            for j in range(num_areas):
                i += 1
                area_line = lines[i].strip().split()
                area_name = area_line[1]# si es A B C D ...
                area_type = area_line[2] # si es schengen o no
                init_gate = int(area_line[4]) # la inicial
                end_gate = int(area_line[6])# la final

                boarding_area = BoardingArea(area_name, area_type)#guarda los datos con la clase
                prefix = f"{terminal_name}{area_name}G"#genera el nombre de la puerta sin tener la posicon en esa terminal

                SetGates(boarding_area, init_gate, end_gate, prefix) #ejecuta la funcion para tener la posicion de la puerta exacta
                terminal.boarding_areas.append(boarding_area)
            bcn.terminals.append(terminal)# mete la ppsicon de la terminal dnetro del aeropuerto
        i += 1
    file.close()
    return bcn

def GateOccupancy (bcn):
    occupancy_list = []
    for terminal in bcn.terminals:
        for area in terminal.boarding_areas:
            for gate in area.gates:
                if gate.occupied:
                    status = "Occupied"
                else:
                    status = "Free"
                occupancy_list.append([gate.name, status, gate.aircraft_id])
    return occupancy_list

def IsAirlineInTerminal (terminal, name):
    if name == "":
        return False
    if len(terminal.airlines) == 0:
        return False

    return name in terminal.airlines

def SearchTerminal (bcn, name):
    for terminal in bcn.terminals:
        if IsAirlineInTerminal(terminal, name):
            return terminal.name
    return ""

def AssignGate(bcn, aircraft):
    terminal_name = SearchTerminal(bcn, aircraft.company)

    if terminal_name == "":
        return -1
    SetSchengenAircrafts(aircraft)#llamamos a la funcion para poder determinar el tipo de avion
    if aircraft.schengen:
        flight_type = "Schengen"
    else:
        flight_type = "non-Schengen"
    for terminal in bcn.terminals:
        if terminal.name == terminal_name:
            for area in terminal.boarding_areas:
                if area.type == flight_type:
                    for gate in area.gates:
                        if not gate.occupied:
                            gate.occupied = True
                            gate.aircraft_id = aircraft.id
                            return gate.name
    return -1