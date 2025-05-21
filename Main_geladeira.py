import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os
from datetime import datetime
from tkcalendar import DateEntry


# Caminho do banco de dados na mesma pasta do script
DB_PATH = os.path.join(os.path.dirname(__file__), "bebidas.db")

# Configuração do banco de dados
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bebidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                volume TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco REAL NOT NULL,
                data_registro TEXT DEFAULT (datetime('now'))
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_registro TEXT,
                id_bebida INTEGER,
                nome TEXT,
                categoria TEXT,
                quantidade_total INTEGER,
                preco_total_vendas REAL,
                data_venda TEXT,
                met_pag TEXT
            )
        ''')
        
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Erro no Banco de Dados", f"Erro ao inicializar o banco de dados: {e}")
    finally:
        conn.close()
        entry_nome.focus_set()
# Função para limpar os campos
def limpar_campos():
    entry_nome.delete(0, tk.END)
    entry_categoria.delete(0, tk.END)
    entry_volume.delete(0, tk.END)
    entry_quantidade.delete(0, tk.END)
    entry_preco.delete(0, tk.END)
    entry_quantidade_venda.delete(0, tk.END)
    entry_metodo_pagamento.delete(0, tk.END)
def atualizar_lista():
    try:
        tree.delete(*tree.get_children())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bebidas")
        bebidas = cursor.fetchall()
        for bebida in bebidas:
            tree.insert("", "end", values=bebida)
    except sqlite3.Error as e:
        messagebox.showerror("Erro no Banco de Dados", f"Erro ao atualizar a lista de bebidas: {e}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao atualizar a lista de bebidas: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
# Função para preencher campos ao selecionar item
def preencher_campos():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Erro", "Selecione uma bebida para editar!")
        return
    
    try:
        item = tree.item(selected_item)['values']
        if not item:
            messagebox.showerror("Erro", "Não foi possível obter os dados da bebida!")
            return
               
        entry_nome.delete(0, tk.END)
        entry_categoria.delete(0, tk.END)
        entry_volume.delete(0, tk.END)
        entry_quantidade.delete(0, tk.END)
        entry_preco.delete(0, tk.END)
        
        entry_nome.insert(0, item[1])  # Nome
        entry_categoria.insert(0, item[2])  # Categoria
        entry_volume.insert(0, item[3])  # Volume
        entry_quantidade.insert(0, item[4])  # Quantidade
        entry_preco.insert(0, item[5])  # Preço

    except IndexError:
        messagebox.showerror("Erro", "Os dados da bebida não estão completos!")
# Função para adicionar bebida
def adicionar_bebida():
    nome = entry_nome.get().capitalize()
    categoria = entry_categoria.get().capitalize()
    volume = entry_volume.get()
    quantidade = entry_quantidade.get()
    preco = entry_preco.get().replace(",", ".")
    
    
    if not (nome and categoria and volume and quantidade and preco):
        messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bebidas (nome, categoria, volume, quantidade, preco, data_registro) VALUES (?, ?, ?, ?, ?, date('now'))",
                    (nome, categoria, volume, quantidade, preco))
        conn.commit()    
        messagebox.showinfo("Sucesso", "Bebida adicionada com sucesso!")    
    except sqlite3.Error as e:
        messagebox.showerror("Erro no Banco de Dados", f"Erro ao adicionar bebida: {e}")
    finally:
        conn.close()
    entry_nome.focus_set()
    limpar_campos()
    atualizar_lista()
# Função para editar bebida
def editar_bebida():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Erro", "Selecione uma bebida para editar!")
        return

    try:
        item_id = tree.item(selected_item)['values'][0]

        nome = entry_nome.get()
        categoria = entry_categoria.get()
        volume = entry_volume.get()
        quantidade = entry_quantidade.get()
        preco = entry_preco.get()

        if not (nome and categoria and volume and quantidade and preco):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        
        try:
            volume = float(volume)
            quantidade = int(quantidade)
            preco = float(preco)
        except ValueError:
            messagebox.showerror("Erro", "Volume, quantidade e preço devem ser números válidos!")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bebidas SET 
            nome = ?, categoria = ?, volume = ?, quantidade = ?, preco = ?
            WHERE id = ?
        """, (nome, categoria, volume, quantidade, preco, item_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            messagebox.showerror("Erro", "Nenhuma bebida foi atualizada. Verifique o ID.")
        else:
            messagebox.showinfo("Sucesso", "Bebida editada com sucesso!")

    except sqlite3.Error as e:
        messagebox.showerror("Erro no Banco de Dados", f"Ocorreu um erro ao atualizar a bebida: {e}")

    finally:
        if 'conn' in locals():
            conn.close()

    limpar_campos()
    atualizar_lista()
# Função para registrar venda
def registrar_venda():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Erro", "Selecione uma bebida para registrar a venda!")
        return

    try:
        quantidade_vendida = entry_quantidade_venda.get().strip()

        # Validação da quantidade vendida
        if not quantidade_vendida.isdigit() or int(quantidade_vendida) <= 0:
            messagebox.showerror("Erro", "A quantidade vendida deve ser um número inteiro maior que 0!")
            return
        quantidade_vendida = int(quantidade_vendida)

        bebida_id = tree.item(selected_item)['values'][0]
        preco = tree.item(selected_item)['values'][5]
        met_pag = entry_metodo_pagamento.get().strip()

        # Validação do método de pagamento
        if not met_pag:
            messagebox.showerror("Erro", "Selecione um método de pagamento!")
            return

        try:
            preco = float(preco)
        except ValueError:
            messagebox.showerror("Erro", "Erro ao obter o preço da bebida. Verifique os dados!")
            return

        total = preco * quantidade_vendida

        # Conectar ao banco de dados e buscar a bebida
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bebidas WHERE id = ?", (bebida_id,))
        bebida = cursor.fetchone()

        if not bebida:
            messagebox.showerror("Erro", "Bebida não encontrada no banco de dados!")
            return

        # Verifica se há estoque suficiente
        estoque_atual = bebida[4]  # Supondo que a quantidade está na quarta posição
        if quantidade_vendida > estoque_atual:
            messagebox.showerror("Erro", f"Estoque insuficiente! Apenas {estoque_atual} unidades disponíveis.")
            return

        # Registrar a venda
        cursor.execute("""INSERT INTO vendas 
                          (data_registro, id_bebida, nome, categoria, quantidade_total, preco_total_vendas, data_venda, met_pag) 
                          VALUES (?, ?, ?, ?, ?, ?, date('now'), ?)""",
                       (bebida[6], bebida_id, bebida[1], bebida[2], quantidade_vendida, total, met_pag))

        # Atualizar estoque
        cursor.execute("UPDATE bebidas SET quantidade = quantidade - ? WHERE id = ?", (quantidade_vendida, bebida_id))
        conn.commit()
        messagebox.showinfo("Sucesso", f"Venda registrada com sucesso! Total: R$ {total:.2f}")

    except sqlite3.Error as e:
        messagebox.showerror("Erro no Banco de Dados", f"Ocorreu um erro ao registrar a venda: {e}")

    finally:
        if 'conn' in locals():
            conn.close()

    limpar_campos()
    atualizar_lista()
   # Função para exibir vendas totais
def exibir_vendas_totais():
    def filtrar_vendas():
        data_inicio = cal_inicio.get()
        data_fim = cal_fim.get()
        # Convertendo as datas para o formato "dd-mm-yyyy"
        data_inicio_formatada = datetime.strptime(data_inicio, '%Y-%m-%d').strftime('%d-%m-%Y')
        data_fim_formatada = datetime.strptime(data_fim, '%Y-%m-%d').strftime('%d-%m-%Y')
        
        
        tree.delete(*tree.get_children())  # Limpa a tabela antes de exibir novos dados
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        query = """
            SELECT data_venda, nome, categoria, quantidade_total, preco_total_vendas, met_pag
            FROM vendas
            WHERE data_venda BETWEEN ? AND ?
        """
        cursor.execute(query, (data_inicio, data_fim))
        vendas = cursor.fetchall()
        conn.close()
        
        total_vendas = 0
        for venda in vendas:
            # Formatando a data da venda para "dd-mm-yyyy"
            data_venda_formatada = datetime.strptime(venda[0], '%Y-%m-%d').strftime('%d-%m-%Y')
            venda_formatada = (data_venda_formatada,) + venda[1:]  # Substituindo a data no resultado
            
            tree.insert("", "end", values=venda_formatada)
            total_vendas += venda[4]
        
        lbl_total.config(text=f"Total de Vendas: R$ {total_vendas:.2f}")

    nova_janela = tk.Toplevel(tk_root)
    nova_janela.title("Vendas Totais")
    #nova_janela.geometry("700x400")
    
    frame_filtro = tk.Frame(nova_janela)
    frame_filtro.pack(fill="x", pady=5, padx=10)
    
    tk.Label(frame_filtro, text="Data Início:").pack(side="left", padx=5)
    cal_inicio = DateEntry(frame_filtro, date_pattern='yyyy-mm-dd')
    cal_inicio.pack(side="left", padx=5)
    
    tk.Label(frame_filtro, text="Data Fim:").pack(side="left", padx=5)
    cal_fim = DateEntry(frame_filtro, date_pattern='yyyy-mm-dd')
    cal_fim.pack(side="left", padx=5)
    
    btn_filtrar = tk.Button(frame_filtro, text="Filtrar", command=filtrar_vendas)
    btn_filtrar.pack(side="left", padx=10)
    
    tree = ttk.Treeview(nova_janela, columns=("Data Venda", "Nome", "Categoria", "QTD Vendida", "Total Vendido", "Pagamento"), show="headings")
    for col in ("Data Venda", "Nome", "Categoria", "QTD Vendida", "Total Vendido", "Pagamento"):
        tree.heading(col, text=col, anchor="center")
        tree.column(col, anchor="center")
    
    tree.pack(fill="both", expand=True)
    
    frame_total = tk.Frame(nova_janela)
    frame_total.pack(fill="x", pady=10, padx=10)
    
    lbl_total = tk.Label(frame_total, text="Total de Vendas: R$ 0.00", font=("Arial", 12, "bold"))
    lbl_total.pack(side="right")

       
    # Função para apagar bebida
def apagar_bebida():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Erro", "Selecione uma bebida para apagar!")
        return

    item_id = tree.item(selected_item)['values'][0]

    if messagebox.askyesno("Confirmação", "Tem certeza que deseja apagar esta bebida?"):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bebidas WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Bebida apagada com sucesso!")
        limpar_campos()
        atualizar_lista()


def centralizar_janela(root, largura, altura):
    # Obtém as dimensões da tela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    # Calcula as posições x e y para centralizar a janela
    pos_x = (largura_tela // 2) - (largura // 2)
    pos_y = (altura_tela // 2) - (altura // 2)
    root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

#MAIN PROGRAM

tk_root = tk.Tk()
tk_root.title("Controle de Bebidas")

# Definindo a dimensão da janela (largura x altura)
largura = 570
altura = 520

# Centralizando a janela
centralizar_janela(tk_root, largura, altura)

# Tornando a janela não ajustável
tk_root.resizable(False, False)

# Configuração da grid para garantir que as colunas tenham o tamanho correto
tk_root.columnconfigure(0, weight=1)
tk_root.columnconfigure(1, weight=1)

# Configuração da Label e Entry
ttk.Label(tk_root, text="Nome:").grid(row=0, column=0, sticky="W")
entry_nome = tk.Entry(tk_root, width=25)
entry_nome.grid(row=0, column=1, sticky="W")

tk.Label(tk_root, text="Categoria:").grid(row=1, column=0, sticky="W")
entry_categoria = tk.Entry(tk_root, width=25)
entry_categoria.grid(row=1, column=1, sticky="W")

tk.Label(tk_root, text="Volume:").grid(row=2, column=0, sticky="W")
entry_volume = tk.Entry(tk_root, width=25)
entry_volume.grid(row=2, column=1, sticky="W")

tk.Label(tk_root, text="Quantidade:").grid(row=3, column=0, sticky="W")
entry_quantidade = tk.Entry(tk_root, width=25)
entry_quantidade.grid(row=3, column=1, sticky="W")

tk.Label(tk_root, text="Preço:").grid(row=4, column=0, sticky="W")
entry_preco = tk.Entry(tk_root, width=25)
entry_preco.grid(row=4, column=1, sticky="W")

linha_horizontal = tk.Frame(tk_root, height=2, bd=1, relief="sunken", bg="black")
linha_horizontal.grid(row=5, columnspan=20, sticky="we", pady=10)

# Botões
tk.Button(tk_root, text="Adicionar Bebida", width=20, command=adicionar_bebida).grid(row=0, column=10, sticky="E")
tk.Button(tk_root, text="Editar Bebida", width=20, command=editar_bebida).grid(row=1, column=10, sticky="E", pady=2)
tk.Button(tk_root, text="Apagar Bebida", foreground="red", width=20, command=apagar_bebida).grid(row=4, column=10, sticky="E")

# Definindo as colunas do Treeview
columns = ("ID", "Nome", "Categoria", "Volume", "QTD", "Preço", "Data/Entrada")
tree = ttk.Treeview(tk_root, columns=columns, show="headings")

# Seção de vendas
tk.Label(tk_root, text="SAÍDAS", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky="W", pady=(0, 6))
tk.Label(tk_root, text="Geladeira", font=("Arial", 10, "bold"), foreground="blue").grid(row=11, column=0, sticky="W", pady=(0, 6))

tk.Label(tk_root, text="Quantidade:").grid(row=7, column=0, sticky="W")
entry_quantidade_venda = tk.Entry(tk_root)
entry_quantidade_venda.grid(row=7, column=1, sticky="W")

tk.Label(tk_root, text="Método de Pagamento:").grid(row=8, column=0, sticky="W")
entry_metodo_pagamento = tk.Entry(tk_root)
entry_metodo_pagamento.grid(row=8, column=1, sticky="W")

tk.Button(tk_root, text="Registrar Venda", width=20, command=registrar_venda).grid(row=7, column=10, sticky="E")
tk.Button(tk_root, text="Exibir Vendas Totais", width=20, command=exibir_vendas_totais).grid(row=8, column=10, sticky="E", pady=2)


# Configurando os cabeçalhos das colunas
for col in columns:
    tree.heading(col, text=col)

tree.column("ID", width=30, stretch=False, anchor="center")
tree.column("Nome", width=120, stretch=False, anchor="center")
tree.column("Categoria", width=100, stretch=False, anchor="center")
tree.column("Volume", width=80, stretch=False, anchor="center")
tree.column("QTD", width=50, stretch=False, anchor="center")
tree.column("Preço", width=55, stretch=False, anchor="center")
tree.column("Data/Entrada", width=120, stretch=False, anchor="center")

# Posicionando o Treeview na grade
tree.grid(row=20, column=0, columnspan=12, sticky="ew")


# Configurando o layout para garantir que o Treeview expanda corretamente
tk_root.grid_columnconfigure(0, weight=1)
tree.bind("<Double-Button-1>", lambda event: preencher_campos())


init_db()
atualizar_lista()


tk_root.mainloop()
