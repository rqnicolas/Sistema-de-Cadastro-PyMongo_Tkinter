import re
from tkinter import ttk, messagebox
import customtkinter as ctk
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGO_URI = "mongodb+srv://nicolasqueirozmarques03407_db_user:nicolasqueirozmarques03407_db_user@clusterprojeto.qhwle3d.mongodb.net/"

ctk.set_appearance_mode("dark")   #"dark", "light" ou "system"
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cadastro de Alunos")
        self.geometry("860x640")
        self.minsize(780, 580)
        
        self.aluno_id = None            #_id de aluno selecionando na tabela
        self.colecao = self.conectar()  # None se o MongoDB estiver fora

        self.criar_interface()
        self.aplicar_estilo_tabela

        if self.colecao is None:
            self.status("Sem conexão com o MongoDB.", erro=True)
            self.after(300, lambda: messagebox.showerror(
                "Erro de conexão.",
                "Não foi possivel conectar ao MongoDB em localhost:27017."
                "Verifique se o serviço está rodand e reabra p programa."
            ))
        else:
            self.listar()
    #----------------------------------------------------------------------------------
    # BANCO DE DADOS
    #---------------------------------------------------------------------------------

    def conectar (self):
        try:
            cliente = MongoClient(MONGO_URI,
            serverSelectTimeoutMS = 3000)
            cliente.admin.command("ping") # força a checagem da conexão agora
            return cliente["escola"]["alunos"]
        except PyMongoError:
            return None
        
    def banco_ok(self):
        if self.colecao is None:
            messagebox.showerror("Erro", "sem conexão com o MongoDB")

    #---------------------------------------------------
    #INTERFACE
    #---------------------------------------------------

    def criar_interface(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Cabeçalho
        cab = ctk.CTkFrame(self, fg_color="transparent")
        cab.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 8))
        cab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            cab, text="Cadastro de Alunos",
            font=ctk.CTkFont(size=26, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            cab, text="Gerencie os alunos da escola",
            font=ctk.CTkFont(size=13), text_color=("gray40", "gray60")
        ).grid(row=1, column=0, sticky="w")

        self.sw_tema = ctk.CTkSwitch(
            cab, text="Modo escuro", command=self.alternar_tema)
        self.sw_tema.select()
        self.sw_tema.grid(row=0, column=1, rowspan=2, sticky="e")

        # Formulário
        form = ctk.CTkFrame(self, corner_radius=12)
        form.grid(row=1, column=0, sticky="ew", padx=28, pady=8)
        form.grid_columnconfigure(0, weight=3)
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="Nome", anchor="w").grid(
            row=0, column=0, sticky="w", padx=(18, 8), pady=(16, 0))
        ctk.CTkLabel(form, text="Idade", anchor="w").grid(
            row=0, column=1, sticky="w", padx=(8, 18), pady=(16, 0))

        self.ent_nome = ctk.CTkEntry(
            form, placeholder_text="Nome completo", height=38)
        self.ent_nome.grid(row=1, column=0, sticky="ew",
                           padx=(18, 8), pady=(4, 12))
        self.ent_idade = ctk.CTkEntry(
            form, placeholder_text="Ex.: 18", height=38)
        self.ent_idade.grid(row=1, column=1, sticky="ew",
                            padx=(8, 18), pady=(4, 12))

        botoes = ctk.CTkFrame(form, fg_color="transparent")
        botoes.grid(row=2, column=0, columnspan=2,
                    sticky="ew", padx=18, pady=(0, 16))
        for i in range(4):
            botoes.grid_columnconfigure(i, weight=1)

        self.btn_cadastrar = ctk.CTkButton(
            botoes, text="Cadastrar", height=38, command=self.cadastrar)
        self.btn_alterar = ctk.CTkButton(
            botoes, text="Alterar", height=38, state="disabled",
            fg_color="#d98c1f", hover_color="#b87413", command=self.alterar)
        self.btn_excluir = ctk.CTkButton(
            botoes, text="Excluir", height=38, state="disabled",
            fg_color="#c0392b", hover_color="#992d22", command=self.excluir)
        self.btn_limpar = ctk.CTkButton(
            botoes, text="Limpar", height=38,
            fg_color=("gray70", "gray30"), hover_color=("gray60", "gray40"),
            text_color=("gray10", "gray90"), command=self.limpar)

        for i, b in enumerate((self.btn_cadastrar, self.btn_alterar,
                               self.btn_excluir, self.btn_limpar)):
            b.grid(row=0, column=i, sticky="ew", padx=4)

        # Busca
        self.ent_busca = ctk.CTkEntry(
            self, placeholder_text="Buscar aluno pelo nome...", height=38)
        self.ent_busca.grid(row=2, column=0, sticky="ew", padx=28, pady=(8, 8))
        self.ent_busca.bind("<KeyRelease>", lambda e: self.listar())

        # Tabela
        area = ctk.CTkFrame(self, corner_radius=12)
        area.grid(row=3, column=0, sticky="nsew", padx=28, pady=(0, 8))
        area.grid_columnconfigure(0, weight=1)
        area.grid_rowconfigure(0, weight=1)

        self.tabela = ttk.Treeview(
            area, columns=("nome", "idade"), show="headings", selectmode="browse")
        self.tabela.heading("nome", text="Nome")
        self.tabela.heading("idade", text="Idade")
        self.tabela.column("nome", anchor="w", width=500)
        self.tabela.column("idade", anchor="center", width=100)
        self.tabela.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        self.tabela.bind("<<TreeviewSelect>>", self.ao_selecionar)

        barra = ctk.CTkScrollbar(area, command=self.tabela.yview)
        barra.grid(row=0, column=1, sticky="ns", padx=(0, 6), pady=10)
        self.tabela.configure(yscrollcommand=barra.set)

        # Barra de status
        self.lbl_status = ctk.CTkLabel(
            self, text="", anchor="w", font=ctk.CTkFont(size=12))
        self.lbl_status.grid(row=4, column=0, sticky="ew",
                             padx=30, pady=(0, 14))

    def aplicar_estilo_tabela(self):
        escuro = ctk.get_appearance_mode() == "Dark"
        fundo = "#1f1f1f" if escuro else "#ffffff"
        texto = "#e6e6e6" if escuro else "#1a1a1a"
        cabecalho = "#2d2d2d" if escuro else "#e6e6e6"

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Treeview", background=fundo, fieldbackground=fundo,
            foreground=texto, borderwidth=0, rowheight=34, font=("Segoe UI", 12))
        estilo.configure(
            "Treeview.Heading", background=cabecalho, foreground=texto,
            relief="flat", font=("Segoe UI", 12, "bold"), padding=6)
        estilo.map("Treeview",
                   background=[("selected", "#1f6aa5")],
                   foreground=[("selected", "#ffffff")])
        estilo.map("Treeview.Heading", background=[("active", cabecalho)])

    def alternar_tema(self):
        ctk.set_appearance_mode("dark" if self.sw_tema.get() else "light")
        self.aplicar_estilo_tabela()

  
    # AUXILIARES

    def status(self, texto, erro=False):
        cor = "#e74c3c" if erro else ("#2e8b57", "#4cc38a")
        self.lbl_status.configure(text=texto, text_color=cor)

    def validar(self):
        nome = self.ent_nome.get().strip()
        idade = self.ent_idade.get().strip()

        if not nome:
            messagebox.showwarning("Atenção", "Informe o nome do aluno.")
            self.ent_nome.focus()
            return None
        if not idade.isdigit() or not (0 < int(idade) <= 120):
            messagebox.showwarning(
                "Atenção", "Informe uma idade válida (1 a 120).")
            self.ent_idade.focus()
            return None
        return nome, int(idade)

    def definir_botoes(self, tem_selecao):
        estado = "normal" if tem_selecao else "disabled"
        self.btn_alterar.configure(state=estado)
        self.btn_excluir.configure(state=estado)

    def ao_selecionar(self, _evento=None):
        selecao = self.tabela.selection()
        if not selecao:
            return
        iid = selecao[0]
        nome, idade = self.tabela.item(iid, "values")
        self.aluno_id = ObjectId(iid)

        self.ent_nome.delete(0, "end")
        self.ent_nome.insert(0, nome)
        self.ent_idade.delete(0, "end")
        self.ent_idade.insert(0, idade)
        self.definir_botoes(True)


    # AÇÕES (CRUD)

    def cadastrar(self):
        if not self.banco_ok():
            return
        dados = self.validar()
        if dados is None:
            return
        nome, idade = dados
        try:
            self.colecao.insert_one({"nome": nome, "idade": idade})
        except PyMongoError as erro:
            messagebox.showerror("Erro", f"Falha ao cadastrar:\n{erro}")
            return
        self.limpar()
        self.listar()
        self.status(f"Aluno '{nome}' cadastrado com sucesso.")

    def listar(self):
        if self.colecao is None:
            return
        filtro = {}
        termo = self.ent_busca.get().strip()
        if termo:
            filtro = {"nome": {"$regex": re.escape(termo), "$options": "i"}}

        for item in self.tabela.get_children():
            self.tabela.delete(item)

        try:
            alunos = list(self.colecao.find(filtro).sort("nome", 1))
        except PyMongoError as erro:
            self.status(f"Erro ao listar: {erro}", erro=True)
            return

        for aluno in alunos:
            self.tabela.insert(
                "", "end", iid=str(aluno["_id"]),
                values=(aluno.get("nome", ""), aluno.get("idade", "")))
        self.status(f"{len(alunos)} aluno(s) encontrado(s).")

    def alterar(self):
        if not self.banco_ok():
            return
        if self.aluno_id is None:
            messagebox.showwarning("Atenção", "Selecione um aluno na tabela.")
            return
        dados = self.validar()
        if dados is None:
            return
        nome, idade = dados
        try:
            self.colecao.update_one(
                {"_id": self.aluno_id},
                {"$set": {"nome": nome, "idade": idade}})
        except PyMongoError as erro:
            messagebox.showerror("Erro", f"Falha ao alterar:\n{erro}")
            return
        self.limpar()
        self.listar()
        self.status(f"Aluno '{nome}' atualizado com sucesso.")

    def excluir(self):
        if not self.banco_ok():
            return
        if self.aluno_id is None:
            messagebox.showwarning("Atenção", "Selecione um aluno na tabela.")
            return
        nome = self.ent_nome.get().strip()
        if not messagebox.askyesno("Confirmar exclusão", f"Excluir o aluno '{nome}'?"):
            return
        try:
            self.colecao.delete_one({"_id": self.aluno_id})
        except PyMongoError as erro:
            messagebox.showerror("Erro", f"Falha ao excluir:\n{erro}")
            return
        self.limpar()
        self.listar()
        self.status(f"Aluno '{nome}' excluído.")

    def limpar(self):
        self.ent_nome.delete(0, "end")
        self.ent_idade.delete(0, "end")
        self.aluno_id = None
        self.tabela.selection_remove(self.tabela.selection())
        self.definir_botoes(False)
        self.ent_nome.focus()


if __name__ == "__main__":
    App().mainloop()
