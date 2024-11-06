# styles.py
from tkinter import ttk

def apply_styles():
    style = ttk.Style()
    style.theme_use('clam')  # Prueba con otros temas si deseas
    style.configure('TFrame', background='#e6f2ff', borderwidth=5, relief='ridge')
    style.configure('TLabel', font=('Helvetica', 12), background='#e6f2ff', foreground='#00509e')
    style.configure('TButton', font=('Helvetica', 10, 'bold'), background='#00509e', foreground='white')
    style.map('TButton',
              background=[('active', '#003366')],  # Color azul oscuro cuando se hace hover
              foreground=[('active', 'white')])
    # Estilos para Radiobutton
    style.configure('TRadiobutton', font=('Helvetica', 11), background='#e6f2ff', foreground='#00509e', padding=5)
    style.map('TRadiobutton',
              background=[('selected', '#cce0ff')],  # Color de fondo cuando está seleccionado
              foreground=[('selected', '#003366')])  # Color de texto cuando está seleccionado
