import re
from tkinter import ttk, messagebox

import customtkinter as ctk
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError

MONGO_URI = "mmongodb+srv://nicolasqueirozmarques03407_db_user:AhnHvyByZslYapKm@clusterprojeto.qhwle3d.mongodb.net/"

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

        #Cabeçalho
        cab = ctk.CTkFrame(self, fg_color="transparent")
        cab.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 8))
        cab.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            cab, text="Cadastro de Alunos",
            font=ctk.CTkFont (size=26, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            cab, text="Gerencie os alunos da escola",

            font=ctk.CTkFont(size=13), text_color=("gray40", "gray60")
        ).grid(row=1, column=0, sticky="w")