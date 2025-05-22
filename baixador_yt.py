import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import yt_dlp
import subprocess
import sys

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Baixador de Vídeo do YouTube")
        self.geometry("500x480")
        self.resizable(False, False)

        # Variáveis
        self.link_var = ctk.StringVar()
        self.dir_var = ctk.StringVar()
        self.res_var = ctk.StringVar(value="1080p")
        self.mp3_var = ctk.BooleanVar(value=False)
        self.ffmpeg_status_var = ctk.StringVar()

        # Status do ffmpeg
        status_frame = ctk.CTkFrame(self)
        status_frame.pack(pady=(10, 0))
        self.ffmpeg_label = ctk.CTkLabel(status_frame, textvariable=self.ffmpeg_status_var)
        self.ffmpeg_label.pack(side="left", padx=(0, 10))
        self.ffmpeg_btn = ctk.CTkButton(status_frame, text="Instalar ffmpeg", command=self.instalar_ffmpeg)
        self.ffmpeg_btn.pack(side="left")
        self.atualizar_status_ffmpeg()

        # Layout
        ctk.CTkLabel(self, text="Link do vídeo:").pack(pady=(20, 5))
        ctk.CTkEntry(self, textvariable=self.link_var, width=400).pack(pady=5)

        ctk.CTkLabel(self, text="Diretório para salvar:").pack(pady=(20, 5))
        dir_frame = ctk.CTkFrame(self)
        dir_frame.pack(pady=5)
        ctk.CTkEntry(dir_frame, textvariable=self.dir_var, width=300).pack(side="left", padx=(0, 10))
        ctk.CTkButton(dir_frame, text="Escolher", command=self.escolher_diretorio).pack(side="left")

        ctk.CTkLabel(self, text="Resolução:").pack(pady=(20, 5))
        ctk.CTkOptionMenu(self, variable=self.res_var, values=["1080p", "720p", "480p", "360p", "audio"]).pack(pady=5)

        switch_frame = ctk.CTkFrame(self)
        switch_frame.pack(pady=(20, 5))
        ctk.CTkLabel(switch_frame, text="Baixar como MP3").pack(side="left", padx=(0, 10))
        ctk.CTkSwitch(switch_frame, variable=self.mp3_var, onvalue=True, offvalue=False).pack(side="left")

        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(self, width=400, height=20, fg_color="#cccccc", progress_color="#27ae60")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(20, 5))
        self.progress_bar.pack_forget()  # Esconde inicialmente

        ctk.CTkButton(self, text="Baixar", command=self.baixar).pack(pady=(10, 10))

    def atualizar_status_ffmpeg(self):
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            self.ffmpeg_status_var.set("Ffmpeg instalado.")
            self.ffmpeg_btn.configure(state="disabled")
        except Exception:
            self.ffmpeg_status_var.set("Ffmpeg não instalado.")
            self.ffmpeg_btn.configure(state="normal")

    def instalar_ffmpeg(self):
        try:
            os.startfile("instalar_ffmpeg.txt")
        except Exception as e:
            messagebox.showerror("Erro ao abrir instruções", f"Erro: {e}")

    def escolher_diretorio(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.dir_var.set(pasta)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            if total:
                percent = downloaded / total
                self.progress_bar.set(percent)
            else:
                self.progress_bar.set(0)
        elif d['status'] == 'finished':
            self.progress_bar.set(1)

    def baixar(self):
        link = self.link_var.get()
        pasta = self.dir_var.get()
        resolucao = self.res_var.get()
        baixar_mp3 = self.mp3_var.get()

        if not link or not pasta:
            messagebox.showerror("Erro", "Preencha o link e o diretório!")
            return
        try:
            self.progress_bar.set(0)
            self.progress_bar.pack(pady=(20, 5))
            self.update()
            ydl_opts = {
                'outtmpl': os.path.join(pasta, '%(title)s.%(ext)s'),
                'quiet': True,
                'noplaylist': True,
                'progress_hooks': [self.progress_hook],
                'concurrent_fragment_downloads': 8,
                'fragment_retries': 10,
            }
            if baixar_mp3 or resolucao == "audio":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                if resolucao in ["1080p", "720p", "480p", "360p"]:
                    ydl_opts['format'] = f'bestvideo[height<={resolucao.replace("p","")}]+bestaudio/best[height<={resolucao.replace("p","")}]'
                else:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            self.progress_bar.set(1)
            messagebox.showinfo("Sucesso", "Download concluído!")
            self.progress_bar.pack_forget()
        except Exception as e:
            self.progress_bar.pack_forget()
            messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")

if __name__ == "__main__":
    app = App()
    app.mainloop() 