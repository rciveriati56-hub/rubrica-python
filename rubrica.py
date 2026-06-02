import flet as ft
import os

def main(page: ft.Page):
    # Configurazione della schermata iniziale di Android
    page.title = "Rubrica Telefonica"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = "adaptive"
    page.padding = 20

    # Percorso sicuro per salvare i contatti su Android
    DATA_FILE = os.path.join(page.client_storage.get_user_data_dir(), "rubrica.txt")

    # --- FUNZIONI DI SERVIZIO (LOGICA) ---
    def carica_contatti():
        contatti = {}
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                for linea in f:
                    if ":" in linea:
                        nome, numero = linea.strip().split(":", 1)
                        contatti[nome.lower()] = {"nome_originale": nome, "numero": numero}
        return contatti

    def salva_contatti(contatti):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            for c in contatti.values():
                f.write(f"{c['nome_originale']}:{c['numero']}\n")

    # --- FUNZIONI DELL'INTERFACCIA (AZIONI) ---
    def aggiorna_lista(filtro=""):
        contatti = carica_contatti()
        lista_contatti.controls.clear()
        
        for nome_chiave, dati in contatti.items():
            if filtro == "" or filtro in nome_chiave:
                lista_contatti.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE),
                        title=ft.Text(dati["nome_originale"], weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(dati["numero"]),
                        trailing=ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, n=dati["nome_originale"]: eliminazione_contatto(n)
                        )
                    )
                )
        page.update()

    def aggiungi_nuovo_contatto(e):
        nome = input_nome.value.strip()
        numero = input_numero.value.strip()

        if not nome or not numero:
            mostra_messaggio("Compila entrambi i campi!", ft.Colors.RED)
            return

        contatti = carica_contatti()
        if nome.lower() in contatti:
            mostra_messaggio("Questo contatto esiste già!", ft.Colors.ORANGE)
            return

        contatti[nome.lower()] = {"nome_originale": nome, "numero": numero}
        salva_contatti(contatti)
        
        # Pulisce i campi e aggiorna la schermata
        input_nome.value = ""
        input_numero.value = ""
        mostra_messaggio(f"Contatto '{nome}' aggiunto!", ft.Colors.GREEN)
        aggiorna_lista()

    def eliminazione_contatto(nome_da_eliminare):
        contatti = carica_contatti()
        if nome_da_eliminare.lower() in contatti:
            del contatti[nome_da_eliminare.lower()]
            salva_contatti(contatti)
            mostra_messaggio(f"Contatto '{nome_da_eliminare}' eliminato.", ft.Colors.BLUE)
            aggiorna_lista(input_cerca.value.lower().strip())

    def cerca_contatto(e):
        aggiorna_lista(input_cerca.value.lower().strip())

    def mostra_messaggio(testo, colore):
        page.snack_bar = ft.SnackBar(ft.Text(testo), bg_color=colore)
        page.snack_bar.open = True
        page.update()

    # --- ELEMENTI VISIVI (INTERFACCIA) ---
    # Campi per l'inserimento
    input_nome = ft.TextField(label="Nome Contatto", prefix_icon=ft.Icons.PERSON_ADD)
    input_numero = ft.TextField(label="Numero di Telefono", keyboard_type=ft.KeyboardType.PHONE, prefix_icon=ft.Icons.PHONE)
    btn_aggiungi = ft.ElevatedButton("Aggiungi in Rubrica", icon=ft.Icons.SAVE, on_click=aggiungi_nuovo_contatto, width=400)

    # Campo per la ricerca
    input_cerca = ft.TextField(label="Cerca contatto...", prefix_icon=ft.Icons.SEARCH, on_change=cerca_contatto)

    # Contenitore della lista contatti
    lista_contatti = ft.ListView(expand=True, spacing=10, padding=10)

    # Struttura della pagina principale
    page.add(
        ft.Text("Nuovo Contatto", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
        input_nome,
        input_numero,
        ft.Row([btn_aggiungi], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(height=20, thickness=2),
        ft.Text("I tuoi Contatti", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
        input_cerca,
        lista_contatti
    )

    # Carica la lista iniziale all'avvio dell'applicazione
    aggiorna_lista()

# Avvia l'applicazione
ft.app(target=main)
