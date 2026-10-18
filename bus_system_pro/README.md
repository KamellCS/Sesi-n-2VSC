# BUS SYSTEM PRO

Prototipo académico de gestión de transporte terrestre desarrollado en Python con Tkinter y archivos JSON. Inspirado en las pantallas de referencia proporcionadas.

## Requisitos
- Python 3.10 o superior
- Tkinter (incluido normalmente con Python en Windows)

## Ejecución
```bash
python main.py
```

## Módulos
- `main.py`: interfaz gráfica, eventos, controles y navegación.
- `services.py`: operaciones de negocio, pasajeros, rutas, buses, venta y asientos.
- `storage.py`: persistencia de datos en JSON.
- `data/`: se crea automáticamente al ejecutar.

## Funciones implementadas
- **Registro de pasajeros** con formulario en pantalla: validación de DNI (8 dígitos), nombres y apellidos (solo letras), teléfono (9 dígitos, empieza con 9) y DNI único.
- Selección de un pasajero en la tabla para editarlo; búsqueda en vivo mientras se escribe.
- Si se cambia el DNI de un pasajero, sus ventas se actualizan. No se elimina a quien tiene ventas.
- Gestión de buses y rutas: registro y eliminación (un bus con rutas asignadas no se puede borrar).
- Venta de pasajes con lista de asientos libres (ya no se escribe el número a mano).
- Mapa de asientos con leyenda y pasillo; informes con resumen por bus.
- Persistencia en JSON con escritura atómica; si un archivo está dañado se respalda como `*.corrupto.json` en vez de perderse.

**Nota:** Prototipo local académico, sin autenticación real, pagos bancarios ni soporte multiusuario. La ocupación se controla por unidad de bus y no por fecha de viaje; para producción se requeriría modelar salidas individuales.

## Git y GitHub: historial progresivo real
Realiza estos commits durante el desarrollo, incorporando los archivos en cada etapa (no inventes fechas ni commits). Puedes empezar con el proyecto completo y un commit inicial honesto, y continuar registrando mejoras posteriores.

```bash
git init
git add storage.py
git commit -m "feat: implementar persistencia JSON"
git add services.py
git commit -m "feat: agregar logica de buses rutas pasajeros y ventas"
git add main.py
git commit -m "feat: construir interfaz grafica modular"
git add README.md .gitignore
git commit -m "docs: documentar instalacion y funcionamiento"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/bus-system-pro.git
git push -u origin main
```

Crea antes el repositorio vacío en GitHub y reemplaza `TU_USUARIO` por tu usuario. Los comandos de commit requieren tener Git configurado con nombre y correo.
