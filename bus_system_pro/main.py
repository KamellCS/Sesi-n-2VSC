import tkinter as tk
from tkinter import ttk, messagebox
from services import (
    records, search_passengers, save_passenger, delete_passenger,
    register_bus, delete_bus, register_route, delete_route,
    available_seats, seats, sell,
)

NAVY = '#10365d'
TEAL = '#00a8b7'
BG = '#edf3f8'
GREEN = '#24a35a'
BLUE = '#1788cf'
RED = '#ef5555'


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('BUS SYSTEM PRO | Gestión de transporte')
        self.geometry('1150x730')
        self.minsize(900, 600)
        self.configure(bg=BG)

        sidebar = tk.Frame(self, bg=NAVY, width=240)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text='🚌 BUS SYSTEM PRO', bg=NAVY, fg='white',
                 font=('Arial', 16, 'bold'), pady=24).pack(fill='x')

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side='right', expand=True, fill='both')

        menu = [
            ('TABLERO PRINCIPAL', self.dashboard),
            ('VENTA DE PASAJES', self.sales),
            ('MAPA DE ASIENTOS', self.map_seats),
            ('REGISTRO DE PASAJEROS', self.passengers),
            ('GESTIÓN DE BUSES', self.buses),
            ('RUTAS Y HORARIOS', self.routes),
            ('INFORMES', self.reports),
            ('CONFIGURACIÓN', self.settings),
            ('CERRAR SESIÓN', self.destroy),
        ]
        for title, callback in menu:
            tk.Button(sidebar, text=title, command=callback, bg=NAVY, fg='white',
                      activebackground=TEAL, activeforeground='white', relief='flat',
                      anchor='w', padx=18, pady=15, font=('Arial', 10, 'bold')).pack(fill='x')
        self.dashboard()

    # ---------- utilidades ----------

    def page(self, title):
        for child in self.content.winfo_children():
            child.destroy()
        tk.Label(self.content, text=title, font=('Arial', 20, 'bold'), bg=BG,
                 fg='#132638').pack(anchor='w', padx=28, pady=(25, 18))
        panel = tk.Frame(self.content, bg='white', padx=18, pady=18)
        panel.pack(fill='both', expand=True, padx=28, pady=(0, 28))
        return panel

    def table(self, parent, columns, items, height=13):
        frame = tk.Frame(parent, bg='white')
        frame.pack(fill='both', expand=True, pady=10)
        tree = ttk.Treeview(frame, columns=columns, show='headings', height=height)
        for c in columns:
            tree.heading(c, text=c)
            tree.column(c, width=120, anchor='center')
        scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        for item in items:
            tree.insert('', 'end', values=item)
        tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        return tree

    def button(self, parent, text, command, color=None, layout='pack', **place):
        opts = {'text': text, 'command': command, 'padx': 12, 'pady': 6}
        if color:
            opts.update(bg=color, fg='white', activebackground=color, activeforeground='white')
        btn = tk.Button(parent, **opts)
        getattr(btn, layout)(**place)
        return btn

    # ---------- tablero ----------

    def dashboard(self):
        p = self.page('TABLERO PRINCIPAL - Empresa de Buses El Sol')
        sales = records('ventas')
        cards = [
            ('VIAJES PROGRAMADOS', str(len(records('rutas')))),
            ('PASAJEROS REGISTRADOS', str(len(records('pasajeros')))),
            ('VENTAS TOTALES', f"S/ {sum(x['precio'] for x in sales):,.2f}"),
        ]
        for label, value in cards:
            f = tk.Frame(p, bg='#e8f6f8', padx=20, pady=18)
            f.pack(side='top', fill='x', pady=7)
            tk.Label(f, text=label, bg='#e8f6f8', fg=NAVY, font=('Arial', 11, 'bold')).pack(anchor='w')
            tk.Label(f, text=value, bg='#e8f6f8', fg='#102334', font=('Arial', 22, 'bold')).pack(anchor='w')
        tk.Label(p, text='Seleccione una opción del menú lateral para administrar el sistema.',
                 bg='white', font=('Arial', 12)).pack(pady=20)

    # ---------- registro de pasajeros ----------

    def passengers(self):
        p = self.page('REGISTRO DE PASAJEROS')
        editing = {'dni': None}  # DNI original del pasajero que se está editando

        # Formulario
        form = tk.LabelFrame(p, text=' Datos del pasajero ', bg='white', font=('Arial', 10, 'bold'),
                             padx=14, pady=10)
        form.pack(fill='x')
        entries = {}
        for col, (key, label) in enumerate([('dni', 'DNI (8 dígitos)'), ('nombres', 'Nombres'),
                                            ('apellidos', 'Apellidos'), ('telefono', 'Teléfono (9 dígitos)')]):
            tk.Label(form, text=label, bg='white').grid(row=0, column=col, sticky='w', padx=6)
            entry = tk.Entry(form, width=22)
            entry.grid(row=1, column=col, sticky='we', padx=6, pady=(2, 8))
            entries[key] = entry
            form.columnconfigure(col, weight=1)

        status = tk.Label(form, text='Modo: nuevo registro', bg='white', fg='#555')
        status.grid(row=2, column=0, columnspan=4, sticky='w', padx=6)

        def clear():
            editing['dni'] = None
            for e in entries.values():
                e.delete(0, 'end')
            entries['dni'].configure(state='normal')
            status.configure(text='Modo: nuevo registro')
            tree.selection_remove(tree.selection())

        def save():
            try:
                save_passenger(entries['dni'].get(), entries['nombres'].get(), entries['apellidos'].get(),
                               entries['telefono'].get(), original_dni=editing['dni'])
            except ValueError as exc:
                messagebox.showerror('Datos inválidos', str(exc), parent=self)
                return
            clear()
            redraw()

        def delete():
            if editing['dni'] is None:
                messagebox.showwarning('Selección', 'Seleccione un pasajero de la lista.', parent=self)
                return
            if not messagebox.askyesno('Confirmar', '¿Eliminar al pasajero seleccionado?', parent=self):
                return
            try:
                delete_passenger(editing['dni'])
            except ValueError as exc:
                messagebox.showerror('Error', str(exc), parent=self)
                return
            clear()
            redraw()

        btns = tk.Frame(form, bg='white')
        btns.grid(row=3, column=0, columnspan=4, sticky='e', pady=(6, 0))
        self.button(btns, '💾 Guardar', save, GREEN, side='left', padx=5)
        self.button(btns, 'Limpiar', clear, side='left', padx=5)
        self.button(btns, 'Eliminar', delete, RED, side='left', padx=5)

        # Búsqueda en vivo
        search_bar = tk.Frame(p, bg='white')
        search_bar.pack(fill='x', pady=(14, 0))
        tk.Label(search_bar, text='Buscar:', bg='white').pack(side='left')
        query = tk.StringVar()
        tk.Entry(search_bar, textvariable=query, width=40).pack(side='left', padx=8)
        count_lbl = tk.Label(search_bar, text='', bg='white', fg='#555')
        count_lbl.pack(side='right')

        def redraw(*_):
            tree.delete(*tree.get_children())
            people = search_passengers(query.get())
            for x in people:
                tree.insert('', 'end', values=(x['dni'], x['nombres'], x['apellidos'], x['telefono']))
            count_lbl.configure(text=f'{len(people)} pasajero(s)')

        def on_select(_event=None):
            sel = tree.selection()
            if not sel:
                return
            dni = str(tree.item(sel[0])['values'][0])
            person = next((x for x in records('pasajeros') if x['dni'] == dni), None)
            if not person:
                return
            editing['dni'] = dni
            for key, e in entries.items():
                e.delete(0, 'end')
                e.insert(0, person[key])
            status.configure(text=f'Modo: editando a {person["nombres"]} {person["apellidos"]}')

        query.trace_add('write', redraw)
        tree = self.table(p, ('DNI', 'Nombres', 'Apellidos', 'Teléfono'), [])
        tree.bind('<<TreeviewSelect>>', on_select)
        redraw()

    # ---------- buses ----------

    def buses(self):
        p = self.page('GESTIÓN DE BUSES')
        form = tk.Frame(p, bg='white')
        form.pack(fill='x')
        labels = ['Placa', 'Número de unidad', 'Capacidad']
        entries = []
        for col, label in enumerate(labels):
            tk.Label(form, text=label, bg='white').grid(row=0, column=col, sticky='w', padx=6)
            e = tk.Entry(form, width=20)
            e.grid(row=1, column=col, padx=6, pady=(2, 8))
            entries.append(e)

        def create():
            try:
                register_bus(entries[0].get(), entries[1].get(), entries[2].get())
            except ValueError as exc:
                messagebox.showerror('Error', str(exc), parent=self)
                return
            self.buses()

        def delete():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning('Selección', 'Seleccione un bus.', parent=self)
                return
            unidad = str(tree.item(sel[0])['values'][1])
            if not messagebox.askyesno('Confirmar', f'¿Eliminar el bus {unidad}?', parent=self):
                return
            try:
                delete_bus(unidad)
            except ValueError as exc:
                messagebox.showerror('Error', str(exc), parent=self)
                return
            self.buses()

        self.button(form, '+ Registrar bus', create, TEAL, layout='grid', row=1, column=3, padx=8)
        self.button(form, 'Eliminar seleccionado', delete, RED, layout='grid', row=1, column=4, padx=8)
        tree = self.table(p, ('Placa', 'Unidad', 'Capacidad'),
                          [(x['placa'], x['unidad'], x['capacidad']) for x in records('buses')])

    # ---------- rutas ----------

    def routes(self):
        p = self.page('RUTAS Y HORARIOS')
        form = tk.Frame(p, bg='white')
        form.pack(fill='x')
        labels = ['Origen', 'Destino', 'Salida (HH:MM)', 'Unidad de bus', 'Precio S/']
        entries = []
        for col, label in enumerate(labels):
            tk.Label(form, text=label, bg='white').grid(row=0, column=col, sticky='w', padx=6)
            e = tk.Entry(form, width=15)
            e.grid(row=1, column=col, padx=6, pady=(2, 8))
            entries.append(e)

        def create():
            try:
                register_route(*(e.get() for e in entries))
            except ValueError as exc:
                messagebox.showerror('Error', str(exc), parent=self)
                return
            self.routes()

        def delete():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning('Selección', 'Seleccione una ruta.', parent=self)
                return
            index = tree.index(sel[0])
            if not messagebox.askyesno('Confirmar', '¿Eliminar la ruta seleccionada?', parent=self):
                return
            delete_route(index)
            self.routes()

        self.button(form, '+ Nueva ruta', create, TEAL, layout='grid', row=1, column=5, padx=8)
        self.button(form, 'Eliminar seleccionada', delete, RED, layout='grid', row=1, column=6, padx=8)
        tree = self.table(p, ('Origen', 'Destino', 'Salida', 'Bus', 'Precio S/'),
                          [(x['origen'], x['destino'], x['hora'], x['bus'], f"{x['precio']:.2f}")
                           for x in records('rutas')])

    # ---------- venta ----------

    def sales(self):
        p = self.page('VENTA DE PASAJES')
        routes = records('rutas')
        choices = [f"{r['origen']} → {r['destino']} | {r['hora']} | Bus {r['bus']} | S/ {r['precio']:.2f}"
                   for r in routes]

        row1 = tk.Frame(p, bg='white'); row1.pack(fill='x', pady=4)
        tk.Label(row1, text='DNI del pasajero', bg='white').grid(row=0, column=0, sticky='w', padx=6)
        dni = tk.Entry(row1, width=30); dni.grid(row=1, column=0, padx=6, pady=(2, 8), sticky='w')

        tk.Label(row1, text='Ruta', bg='white').grid(row=0, column=1, sticky='w', padx=6)
        route = ttk.Combobox(row1, values=choices, state='readonly', width=60)
        route.grid(row=1, column=1, padx=6, pady=(2, 8), sticky='we')
        row1.columnconfigure(1, weight=1)

        row2 = tk.Frame(p, bg='white'); row2.pack(fill='x', pady=4)
        tk.Label(row2, text='Asiento libre', bg='white').grid(row=0, column=0, sticky='w', padx=6)
        seat = ttk.Combobox(row2, state='readonly', width=12)
        seat.grid(row=1, column=0, padx=6, pady=(2, 8), sticky='w')
        info = tk.Label(row2, text='', bg='white', fg='#555')
        info.grid(row=1, column=1, sticky='w', padx=6)

        def refresh_seats(_event=None):
            idx = route.current()
            if idx < 0:
                seat['values'] = []
                seat.set('')
                info.configure(text='')
                return
            bus = routes[idx]['bus']
            free = available_seats(bus)
            seat['values'] = free
            seat.set(free[0] if free else '')
            info.configure(text=f'{len(free)} asientos disponibles en el bus {bus}')

        def purchase():
            if route.current() < 0:
                messagebox.showerror('Error', 'Seleccione una ruta.', parent=self); return
            if not seat.get():
                messagebox.showerror('Error', 'No hay asiento seleccionado.', parent=self); return
            try:
                sale = sell(dni.get().strip(), route.current(), int(seat.get()))
            except ValueError as exc:
                messagebox.showerror('Error', str(exc), parent=self)
                return
            messagebox.showinfo('Venta realizada',
                                f"Pasaje registrado. Asiento {sale['asiento']} - S/ {sale['precio']:.2f}",
                                parent=self)
            self.sales()

        route.bind('<<ComboboxSelected>>', refresh_seats)
        if choices:
            route.current(0)
            refresh_seats()

        self.button(p, '✔ Registrar venta', purchase, GREEN, pady=10, ipadx=10)
        self.table(p, ('DNI', 'Ruta', 'Bus', 'Asiento', 'Precio'),
                   [(x['dni'], x['ruta'], x['bus'], x['asiento'], x['precio']) for x in records('ventas')],
                   height=8)

    # ---------- mapa de asientos ----------

    def map_seats(self):
        p = self.page('MAPA DE ASIENTOS')
        buses = records('buses')
        top = tk.Frame(p, bg='white'); top.pack(anchor='w')
        tk.Label(top, text='Bus:', bg='white').pack(side='left')
        selection = ttk.Combobox(top, values=[b['unidad'] for b in buses], state='readonly', width=15)
        selection.pack(side='left', padx=8)

        area = tk.Frame(p, bg='white'); area.pack(pady=15)
        legend = tk.Label(p, text='Verde: Disponible     Rojo: Ocupado     (pasillo entre columnas 2 y 3)',
                          bg='white', fg='#333')
        legend.pack()

        def render(_event=None):
            for widget in area.winfo_children():
                widget.destroy()
            if not selection.get():
                return
            for num, status in seats(selection.get()):
                color = RED if status == 'Ocupado' else '#1db66b'
                col = (num - 1) % 4
                col += 1 if col >= 2 else 0  # hueco de pasillo
                tk.Label(area, text=f'{num:02}', bg=color, fg='white', width=5, height=2,
                         font=('Arial', 10, 'bold')).grid(row=(num - 1) // 4, column=col, padx=5, pady=4)

        selection.bind('<<ComboboxSelected>>', render)
        if buses:
            selection.current(0)
            render()

    # ---------- informes ----------

    def reports(self):
        p = self.page('INFORMES DE VENTAS')
        sales = records('ventas')
        total = sum(x['precio'] for x in sales)
        tk.Label(p, text=f"Total de pasajes vendidos: {len(sales)}     |     Ingresos: S/ {total:,.2f}",
                 bg='white', font=('Arial', 14, 'bold')).pack(pady=15)

        per_bus = {}
        for x in sales:
            count, income = per_bus.get(x['bus'], (0, 0.0))
            per_bus[x['bus']] = (count + 1, income + x['precio'])
        tk.Label(p, text='Resumen por bus', bg='white', font=('Arial', 11, 'bold')).pack(anchor='w')
        self.table(p, ('Bus', 'Pasajes', 'Ingresos S/'),
                   [(bus, n, f'{inc:,.2f}') for bus, (n, inc) in sorted(per_bus.items())], height=4)

        tk.Label(p, text='Detalle de ventas', bg='white', font=('Arial', 11, 'bold')).pack(anchor='w')
        self.table(p, ('DNI', 'Ruta', 'Hora', 'Bus', 'Asiento', 'Importe'),
                   [(x['dni'], x['ruta'], x['hora'], x['bus'], x['asiento'], f"{x['precio']:.2f}")
                    for x in sales])

    # ---------- configuración ----------

    def settings(self):
        p = self.page('CONFIGURACIÓN')
        tk.Label(p, text='BUS SYSTEM PRO\nEmpresa de Buses El Sol\nAlmacenamiento local en archivos JSON\n'
                         'Versión académica 1.1', bg='white', font=('Arial', 13),
                 justify='left').pack(anchor='w', pady=15)


if __name__ == '__main__':
    App().mainloop()
