import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from fpdf import FPDF
import json
import os
import shutil
import datetime
import csv

FILE = "rubrica.json"
FOTO_DIR = "foto"

# -------------------------------
#  FUNZIONI DATABASE
# -------------------------------

def carica_contatti():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salva_contatti(contatti):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(contatti, f, indent=4, ensure_ascii=False)

def aggiungi_contatto(dati):
    contatti = carica_contatti()
    contatti.append(dati)
    salva_contatti(contatti)

def cerca_contatti(nome="", cognome="", telefono=""):
    contatti = carica_contatti()
    risultati = []
    for c in contatti:
        if (nome.lower() in c["nome"].lower() if nome else True) and \
           (cognome.lower() in c["cognome"].lower() if cognome else True) and \
           (telefono in c["telefono"] if telefono else True):
            risultati.append(c)
    return risultati

def elenco_ordinato():
    contatti = carica_contatti()
    return sorted(contatti, key=lambda x: (x["cognome"].lower(), x["nome"].lower()))

def aggiorna_contatto(vecchio_contatto, nuovo_contatto):
    contatti = carica_contatti()
    for i, c in enumerate(contatti):
        if c == vecchio_contatto:
            contatti[i] = nuovo_contatto
            break
    salva_contatti(contatti)

def elimina_contatto(contatto):
    contatti = carica_contatti()
    contatti = [c for c in contatti if c != contatto]
    salva_contatti(contatti)

# -------------------------------
#  GESTIONE FOTO
# -------------------------------

def salva_foto(path_originale, nome, cognome):
    if not path_originale:
        return ""
    if not os.path.exists(FOTO_DIR):
        os.makedirs(FOTO_DIR)
    est = os.path.splitext(path_originale)[1]
    nuovo_nome = f"{nome}_{cognome}{est}"
    nuovo_path = os.path.join(FOTO_DIR, nuovo_nome)
    shutil.copy(path_originale, nuovo_path)
    return nuovo_path

# -------------------------------
#  STAMPA PDF — SINGOLO CONTATTO
# -------------------------------

def stampa_pdf_contatto(contatto):
    pdf = FPDF()
    pdf.add_page()

    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 25)

    pdf.set_font("Arial", "B", 18)
    pdf.ln(20)
    pdf.cell(0, 10, "Scheda Contatto", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    data_ora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 10, f"Stampato il: {data_ora}", ln=True, align="C")

    pdf.ln(10)

    pdf.set_font("Arial", "", 14)
    for campo in ["nome", "cognome", "telefono", "email", "via", "citta", "cap"]:
        pdf.cell(0, 10, f"{campo.capitalize()}: {contatto[campo]}", ln=True)

    pdf.ln(10)

    if contatto["foto"] and os.path.exists(contatto["foto"]):
        pdf.image(contatto["foto"], x=60, w=90)

    nome_file = f"contatto_{contatto['nome']}_{contatto['cognome']}.pdf"
    pdf.output(nome_file)
    messagebox.showinfo("PDF creato", f"File generato: {nome_file}")

# -------------------------------
#  STAMPA PDF — ELENCO COMPLETO
# -------------------------------

def stampa_pdf_elenco():
    contatti = elenco_ordinato()
    if not contatti:
        messagebox.showwarning("Vuoto", "Nessun contatto da stampare.")
        return

    pdf = FPDF()
    pdf.add_page()

    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 25)

    pdf.set_font("Arial", "B", 18)
    pdf.ln(20)
    pdf.cell(0, 10, "Rubrica Telefonica - Elenco Completo", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    data_ora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 10, f"Stampato il: {data_ora}", ln=True, align="C")

    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(60, 10, "Cognome", 1, 0, "C", True)
    pdf.cell(60, 10, "Nome", 1, 0, "C", True)
    pdf.cell(70, 10, "Telefono", 1, 1, "C", True)

    pdf.set_font("Arial", "", 12)
    for c in contatti:
        pdf.cell(60, 10, c["cognome"], 1)
        pdf.cell(60, 10, c["nome"], 1)
        pdf.cell(70, 10, c["telefono"], 1, 1)

    nome_file = "rubrica_elenco_completo.pdf"
    pdf.output(nome_file)
    messagebox.showinfo("PDF creato", f"File generato: {nome_file}")
# -------------------------------
#  STAMPA PDF — ELENCO CON FOTO 40x40
# -------------------------------

def stampa_pdf_elenco_con_foto():
    contatti = elenco_ordinato()
    if not contatti:
        messagebox.showwarning("Vuoto", "Nessun contatto da stampare.")
        return

    pdf = FPDF()
    pdf.add_page()

    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 25)

    pdf.set_font("Arial", "B", 18)
    pdf.ln(20)
    pdf.cell(0, 10, "Rubrica - Elenco con Foto", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    data_ora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 10, f"Stampato il: {data_ora}", ln=True, align="C")

    pdf.ln(10)

    foto_w = 40
    foto_h = 40
    y_step = 45

    pdf.set_font("Arial", "", 12)

    for c in contatti:
        y = pdf.get_y()

        # Foto
        if c["foto"] and os.path.exists(c["foto"]):
            try:
                pdf.image(c["foto"], x=10, y=y, w=foto_w, h=foto_h)
            except:
                pass

        # Testo accanto alla foto
        pdf.set_xy(10 + foto_w + 5, y)
        pdf.cell(0, 8, f"{c['cognome']} {c['nome']}", ln=True)
        pdf.set_x(10 + foto_w + 5)
        pdf.cell(0, 8, f"Tel: {c['telefono']}", ln=True)
        pdf.set_x(10 + foto_w + 5)
        pdf.cell(0, 8, f"{c['citta']} (CAP {c['cap']})", ln=True)

        pdf.set_y(y + y_step)

        # Nuova pagina se necessario
        if pdf.get_y() > 260:
            pdf.add_page()

    nome_file = "rubrica_elenco_con_foto.pdf"
    pdf.output(nome_file)
    messagebox.showinfo("PDF creato", f"File generato: {nome_file}")

# -------------------------------
#  ESPORTAZIONE CSV
# -------------------------------

def esporta_csv():
    contatti = elenco_ordinato()
    if not contatti:
        messagebox.showwarning("Vuoto", "Nessun contatto da esportare.")
        return

    nome_file = "rubrica_export.csv"
    with open(nome_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Nome", "Cognome", "Via", "Città", "CAP", "Telefono", "Email", "Foto"])
        for c in contatti:
            writer.writerow([
                c["nome"], c["cognome"], c["via"], c["citta"],
                c["cap"], c["telefono"], c["email"], c["foto"]
            ])

    messagebox.showinfo("CSV creato", f"File generato: {nome_file}")

# -------------------------------
#  FINESTRA DETTAGLI CONTATTO
# -------------------------------

def mostra_contatto(contatto):
    win = tk.Toplevel()
    win.title("Dettagli contatto")

    nome_var = tk.StringVar(value=contatto["nome"])
    cognome_var = tk.StringVar(value=contatto["cognome"])
    via_var = tk.StringVar(value=contatto["via"])
    citta_var = tk.StringVar(value=contatto["citta"])
    cap_var = tk.StringVar(value=contatto["cap"])
    tel_var = tk.StringVar(value=contatto["telefono"])
    email_var = tk.StringVar(value=contatto["email"])
    foto_var = tk.StringVar(value=contatto["foto"])

    tk.Label(win, text="Scheda contatto", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

    campi = [
        ("Nome", nome_var),
        ("Cognome", cognome_var),
        ("Via", via_var),
        ("Città", citta_var),
        ("CAP", cap_var),
        ("Telefono", tel_var),
        ("Email", email_var),
    ]

    for i, (label, var) in enumerate(campi, start=1):
        tk.Label(win, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
        tk.Entry(win, textvariable=var).grid(row=i, column=1, padx=5, pady=3)

    def scegli_foto_contatto():
        path = filedialog.askopenfilename(filetypes=[("Immagini", "*.png;*.jpg;*.jpeg")])
        if path:
            nuovo_path = salva_foto(path, nome_var.get(), cognome_var.get())
            foto_var.set(nuovo_path)
            aggiorna_foto()

    tk.Button(win, text="Scegli foto", command=scegli_foto_contatto).grid(row=8, column=0, padx=5, pady=5)
    tk.Entry(win, textvariable=foto_var).grid(row=8, column=1, padx=5, pady=5)

    foto_label = tk.Label(win)
    foto_label.grid(row=0, column=2, rowspan=9, padx=10, pady=10)

    def aggiorna_foto():
        if foto_var.get() and os.path.exists(foto_var.get()):
            img = Image.open(foto_var.get())
            img = img.resize((150, 150))
            img = ImageTk.PhotoImage(img)
            foto_label.config(image=img, text="")
            foto_label.image = img
        else:
            foto_label.config(image="", text="Nessuna foto")
            foto_label.image = None

    aggiorna_foto()

    def salva_modifiche():
        nuovo = {
            "nome": nome_var.get(),
            "cognome": cognome_var.get(),
            "via": via_var.get(),
            "citta": citta_var.get(),
            "cap": cap_var.get(),
            "telefono": tel_var.get(),
            "email": email_var.get(),
            "foto": foto_var.get()
        }
        aggiorna_contatto(contatto, nuovo)
        messagebox.showinfo("OK", "Contatto aggiornato.")
        win.destroy()

    def elimina():
        if messagebox.askyesno("Conferma", "Vuoi davvero eliminare questo contatto?"):
            elimina_contatto(contatto)
            messagebox.showinfo("Eliminato", "Contatto eliminato.")
            win.destroy()

    def stampa_pdf_corrente():
        nuovo = {
            "nome": nome_var.get(),
            "cognome": cognome_var.get(),
            "via": via_var.get(),
            "citta": citta_var.get(),
            "cap": cap_var.get(),
            "telefono": tel_var.get(),
            "email": email_var.get(),
            "foto": foto_var.get()
        }
        stampa_pdf_contatto(nuovo)

    tk.Button(win, text="Salva modifiche", command=salva_modifiche).grid(row=9, column=0, columnspan=2, pady=10)
    tk.Button(win, text="Elimina contatto", command=elimina, fg="red").grid(row=10, column=0, columnspan=2, pady=5)
    tk.Button(win, text="Stampa PDF", command=stampa_pdf_corrente).grid(row=11, column=0, columnspan=2, pady=5)
# -------------------------------
#  FINESTRA RISULTATI
# -------------------------------

def mostra_risultati(lista):
    win = tk.Toplevel()
    win.title("Risultati ricerca")

    if not lista:
        tk.Label(win, text="Nessun risultato trovato").pack(padx=10, pady=10)
        return

    for c in lista:
        testo = f"{c['cognome']} {c['nome']} - {c['telefono']}"
        b = tk.Button(win, text=testo, command=lambda c=c: mostra_contatto(c))
        b.pack(fill="x", padx=10, pady=3)

# -------------------------------
#  GUI PRINCIPALE
# -------------------------------

def avvia_gui():
    root = tk.Tk()
    root.title("Rubrica Telefonica")

    nome = tk.StringVar()
    cognome = tk.StringVar()
    via = tk.StringVar()
    citta = tk.StringVar()
    cap = tk.StringVar()
    telefono = tk.StringVar()
    email = tk.StringVar()
    foto_path = tk.StringVar()

    def scegli_foto():
        path = filedialog.askopenfilename(filetypes=[("Immagini", "*.png;*.jpg;*.jpeg")])
        if path:
            foto_path.set(path)

    def salva():
        if not nome.get() or not cognome.get():
            messagebox.showwarning("Dati mancanti", "Nome e cognome sono obbligatori.")
            return

        path_foto = salva_foto(foto_path.get(), nome.get(), cognome.get()) if foto_path.get() else ""

        dati = {
            "nome": nome.get(),
            "cognome": cognome.get(),
            "via": via.get(),
            "citta": citta.get(),
            "cap": cap.get(),
            "telefono": telefono.get(),
            "email": email.get(),
            "foto": path_foto
        }

        aggiungi_contatto(dati)
        messagebox.showinfo("OK", "Contatto aggiunto!")

    def cerca():
        risultati = cerca_contatti(nome.get(), cognome.get(), telefono.get())
        mostra_risultati(risultati)

    def mostra_elenco():
        risultati = elenco_ordinato()
        mostra_risultati(risultati)

    campi = [
        ("Nome", nome),
        ("Cognome", cognome),
        ("Via", via),
        ("Città", citta),
        ("CAP", cap),
        ("Telefono", telefono),
        ("Email", email)
    ]

    for i, (label, var) in enumerate(campi):
        tk.Label(root, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(root, textvariable=var).grid(row=i, column=1, padx=5, pady=5)

    tk.Button(root, text="Scegli foto", command=scegli_foto).grid(row=7, column=0, pady=5)
    tk.Entry(root, textvariable=foto_path).grid(row=7, column=1, pady=5)

    tk.Button(root, text="Aggiungi contatto", command=salva).grid(row=8, column=0, columnspan=2, pady=10)
    tk.Button(root, text="Cerca", command=cerca).grid(row=9, column=0, columnspan=2, pady=5)
    tk.Button(root, text="Elenco completo", command=mostra_elenco).grid(row=10, column=0, columnspan=2, pady=5)
    tk.Button(root, text="Stampa elenco PDF", command=stampa_pdf_elenco).grid(row=11, column=0, columnspan=2, pady=5)
    tk.Button(root, text="Stampa elenco con foto", command=stampa_pdf_elenco_con_foto).grid(row=12, column=0, columnspan=2, pady=5)
    tk.Button(root, text="Esporta CSV", command=esporta_csv).grid(row=13, column=0, columnspan=2, pady=5)
    root.mainloop()

# -------------------------------
#  AVVIO PROGRAMMA
# -------------------------------

if __name__ == "__main__":
    avvia_gui()


