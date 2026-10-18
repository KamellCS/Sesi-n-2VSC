import re
from datetime import datetime

from storage import load, save

DEFAULT_BUSES = [
    {'placa': 'ABC-123', 'unidad': '45B', 'capacidad': 40},
    {'placa': 'DEF-456', 'unidad': '458', 'capacidad': 32},
]
DEFAULT_ROUTES = [
    {'origen': 'Lima', 'destino': 'Ica', 'hora': '10:00', 'bus': '45B', 'precio': 45.0},
    {'origen': 'Lima', 'destino': 'Huacho', 'hora': '13:00', 'bus': '458', 'precio': 30.0},
]

NAME_RE = re.compile(r"[^\W\d_]+(?:[ '\-][^\W\d_]+)*")


def records(kind):
    defaults = {'buses': DEFAULT_BUSES, 'rutas': DEFAULT_ROUTES, 'pasajeros': [], 'ventas': []}
    return load(kind, defaults[kind])


def add(kind, item):
    items = records(kind)
    items.append(item)
    save(kind, items)


def replace(kind, items):
    save(kind, items)


# ---------- Pasajeros ----------

def validate_passenger(dni, nombres, apellidos, telefono):
    """Valida los datos y devuelve un diccionario limpio. Lanza ValueError si algo falla."""
    fields = {
        'dni': dni.strip(),
        'nombres': ' '.join(nombres.split()),
        'apellidos': ' '.join(apellidos.split()),
        'telefono': telefono.strip(),
    }
    if not all(fields.values()):
        raise ValueError('Todos los campos son obligatorios.')
    if not re.fullmatch(r'\d{8}', fields['dni']):
        raise ValueError('El DNI debe tener exactamente 8 dígitos.')
    if not NAME_RE.fullmatch(fields['nombres']):
        raise ValueError('Los nombres solo pueden contener letras.')
    if not NAME_RE.fullmatch(fields['apellidos']):
        raise ValueError('Los apellidos solo pueden contener letras.')
    if not re.fullmatch(r'9\d{8}', fields['telefono']):
        raise ValueError('El teléfono debe tener 9 dígitos y empezar con 9.')
    return fields


def search_passengers(query=''):
    q = query.strip().lower()
    people = records('pasajeros')
    if not q:
        return people
    return [p for p in people if q in ' '.join(str(v) for v in p.values()).lower()]


def save_passenger(dni, nombres, apellidos, telefono, original_dni=None):
    """Registra un pasajero nuevo (original_dni=None) o actualiza uno existente.
    Si cambia el DNI, también se actualizan sus ventas."""
    fields = validate_passenger(dni, nombres, apellidos, telefono)
    people = records('pasajeros')
    if any(p['dni'] == fields['dni'] and p['dni'] != original_dni for p in people):
        raise ValueError('Ya existe un pasajero con ese DNI.')
    if original_dni is None:
        people.append(fields)
    else:
        idx = next((i for i, p in enumerate(people) if p['dni'] == original_dni), None)
        if idx is None:
            raise ValueError('Pasajero no encontrado.')
        people[idx] = fields
        if original_dni != fields['dni']:
            sales = records('ventas')
            for s in sales:
                if s['dni'] == original_dni:
                    s['dni'] = fields['dni']
            replace('ventas', sales)
    replace('pasajeros', people)
    return fields


def delete_passenger(dni):
    if any(v['dni'] == dni for v in records('ventas')):
        raise ValueError('No se puede eliminar un pasajero con ventas registradas.')
    replace('pasajeros', [p for p in records('pasajeros') if p['dni'] != dni])


# ---------- Buses ----------

def register_bus(placa, unidad, capacidad):
    placa, unidad = placa.strip().upper(), unidad.strip()
    if not placa or not unidad:
        raise ValueError('Placa y número de unidad son obligatorios.')
    try:
        capacidad = int(capacidad)
    except ValueError:
        raise ValueError('La capacidad debe ser un número entero.')
    if capacidad <= 0:
        raise ValueError('La capacidad debe ser mayor que cero.')
    if any(b['unidad'] == unidad for b in records('buses')):
        raise ValueError('Ya existe un bus con esa unidad.')
    add('buses', {'placa': placa, 'unidad': unidad, 'capacidad': capacidad})


def delete_bus(unidad):
    if any(r['bus'] == unidad for r in records('rutas')):
        raise ValueError('El bus tiene rutas asignadas. Elimine primero esas rutas.')
    replace('buses', [b for b in records('buses') if b['unidad'] != unidad])


# ---------- Rutas ----------

def register_route(origen, destino, hora, bus, precio):
    origen, destino, bus = origen.strip(), destino.strip(), bus.strip()
    if not origen or not destino:
        raise ValueError('Origen y destino son obligatorios.')
    if not any(b['unidad'] == bus for b in records('buses')):
        raise ValueError('El bus no existe.')
    try:
        datetime.strptime(hora.strip(), '%H:%M')
    except ValueError:
        raise ValueError('La hora debe tener formato HH:MM.')
    try:
        precio = float(precio)
    except ValueError:
        raise ValueError('El precio debe ser un número.')
    if precio <= 0:
        raise ValueError('El precio debe ser mayor que cero.')
    add('rutas', {'origen': origen, 'destino': destino, 'hora': hora.strip(), 'bus': bus, 'precio': precio})


def delete_route(index):
    routes = records('rutas')
    if not 0 <= index < len(routes):
        raise ValueError('Ruta no válida.')
    del routes[index]
    replace('rutas', routes)


# ---------- Asientos y ventas ----------

def seats(bus):
    capacity = next((int(b['capacidad']) for b in records('buses') if b['unidad'] == bus), 40)
    occupied = {int(v['asiento']) for v in records('ventas') if v['bus'] == bus}
    return [(i, 'Ocupado' if i in occupied else 'Disponible') for i in range(1, capacity + 1)]


def available_seats(bus):
    return [n for n, status in seats(bus) if status == 'Disponible']


def sell(dni, route_index, seat):
    if not any(p['dni'] == dni for p in records('pasajeros')):
        raise ValueError('Primero registre al pasajero.')
    routes = records('rutas')
    if not 0 <= route_index < len(routes):
        raise ValueError('Seleccione una ruta válida.')
    route = routes[route_index]
    if (seat, 'Disponible') not in seats(route['bus']):
        raise ValueError('Asiento ocupado o fuera de rango.')
    sale = {
        'dni': dni,
        'ruta': f"{route['origen']} - {route['destino']}",
        'hora': route['hora'],
        'bus': route['bus'],
        'asiento': seat,
        'precio': float(route['precio']),
    }
    add('ventas', sale)
    return sale
