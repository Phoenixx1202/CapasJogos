import os
import re
import requests
import sys
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Combobox
from threading import Thread
from tkinter import ttk

# Configurações da API do TheGamesDB
API_KEY = 'SUA API KEY'
API_BASE_URL = 'https://api.thegamesdb.net/v1'

# URL base do repositório GitHub onde o executável atualizado estará hospedado
GITHUB_REPO = 'Phoenixx1202/CapasJogos'
LATEST_RELEASE_URL = f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest'

plataformas = [
    (25, '3DO'),
    (22, 'Atari 2600'),
    (26, 'Atari 5200'),
    (27, 'Atari 7800'),
    (4943, 'Atari 800'),
    (28, 'Atari Jaguar'),
    (29, 'Atari Jaguar CD'),
    (4924, 'Atari Lynx'),
    (4950, 'Game & Watch'),
    (24, 'Neo Geo'),
    (4956, 'Neo Geo CD'),
    (4922, 'Neo Geo Pocket'),
    (4923, 'Neo Geo Pocket Color'),
    (4938, 'N-Gage'),
    (4912, 'Nintendo 3DS'),
    (3, 'Nintendo 64'),
    (8, 'Nintendo DS'),
    (7, 'Nintendo Entertainment System (NES)'),
    (4, 'Nintendo Game Boy'),
    (5, 'Nintendo Game Boy Advance'),
    (41, 'Nintendo Game Boy Color'),
    (2, 'Nintendo GameCube'),
    (4957, 'Nintendo Pokémon Mini'),
    (4971, 'Nintendo Switch'),
    (4918, 'Nintendo Virtual Boy'),
    (33, 'Sega 32X'),
    (21, 'Sega CD'),
    (16, 'Sega Dreamcast'),
    (20, 'Sega Game Gear'),
    (18, 'Sega Genesis'),
    (35, 'Sega Master System'),
    (36, 'Sega Mega Drive'),
    (4958, 'Sega Pico'),
    (17, 'Sega Saturn'),
    (4949, 'SEGA SG-1000'),
    (13, 'PSP'),
    (10, 'Sony Playstation'),
    (11, 'Sony Playstation 2'),
    (4925, 'WonderSwan'),
    (4926, 'WonderSwan Color'),
]

# Função para verificar e atualizar o programa
def check_for_updates():
    try:
        response = requests.get(LATEST_RELEASE_URL)
        response.raise_for_status()
        download_url = response.json()['assets'][0]['browser_download_url']
        latest_version = response.json()['tag_name']

        current_version = get_current_version()

        if current_version < latest_version:
            answer = messagebox.askyesno("Atualização Disponível", "Há uma nova versão disponível. Deseja atualizar agora?")
            if answer:
                update_program(download_url)
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao verificar atualizações: {e}")

# Função para obter a versão atual do programa
def get_current_version():
    return "v1.3"

# Função para atualizar o programa
def update_program(download_url):
    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        filename = os.path.basename(download_url)
        filepath = os.path.join(os.getcwd(), filename)
        
        with open(filepath, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        
        messagebox.showinfo("Atualização Concluída", "O programa foi atualizado com sucesso. Reinicie o aplicativo.")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao atualizar o programa: {e}")

# Função para buscar informações do jogo pelo nome e plataforma
def get_game_info(game_name, platform_id):
    try:
        url = f'{API_BASE_URL}/Games/ByGameName'
        params = {
            'apikey': API_KEY,
            'name': game_name,
            'filter[platform]': platform_id
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        game_info = response.json()
        return game_info
    except requests.exceptions.RequestException as e:
        print(f'Erro ao buscar informações do jogo: {str(e)}')
        return None

# Função para buscar a capa do jogo pelo ID do jogo
def get_game_cover(game_id):
    try:
        url = f'{API_BASE_URL}/Games/Images'
        params = {
            'apikey': API_KEY,
            'games_id': game_id,
            'filter[type]': 'boxart'
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        game_images = response.json()
        return game_images
    except requests.exceptions.RequestException as e:
        print(f'Erro ao buscar capa do jogo: {str(e)}')
        return None

# Função para extrair o nome principal do jogo
def extract_main_game_name(file_name):
    pattern = r'^(.*?)\s*[\(\[][^)\]]*[\)\]]?.*$'
    match = re.match(pattern, file_name)
    if match:
        return match.group(1).strip()
    else:
        return file_name

# Função para importar os nomes dos jogos de uma pasta
def get_game_names_from_folder(folder_path):
    game_names = []
    for file_name in os.listdir(folder_path):
        if os.path.isdir(os.path.join(folder_path, file_name)):
            continue
        name_without_extension, _ = os.path.splitext(file_name)
        main_game_name = extract_main_game_name(name_without_extension)
        game_names.append((main_game_name, name_without_extension))  # Armazena o nome filtrado e o nome original sem extensão
    return game_names

def download_game_cover(game_name, platform_id, output_folder, progress_var, original_file_name, save_as_png=False, save_as_jpg=False):
    game_info = get_game_info(game_name, platform_id)
    if game_info and 'data' in game_info and 'games' in game_info['data'] and game_info['data']['games']:
        game = next((g for g in game_info['data']['games'] if g['platform'] == platform_id), None)
        if game:
            game_id = game['id']
            game_cover = get_game_cover(game_id)
            if game_cover and 'data' in game_cover and 'images' in game_cover['data']:
                images = game_cover['data']['images']
                if images and str(game_id) in images:
                    for image_info in images[str(game_id)]:
                        if image_info['type'] == 'boxart' and image_info['side'] == 'front':
                            base_url = game_cover['data']['base_url']['original']
                            filename = image_info['filename']
                            url = f"{base_url}{filename}"

                            response = requests.get(url)
                            if response.status_code == 200:
                                if save_as_png:
                                    image_path = os.path.join(output_folder, f"{original_file_name}.png")
                                elif save_as_jpg:
                                    image_path = os.path.join(output_folder, f"{original_file_name}.jpg")
                                else:
                                    image_path = os.path.join(output_folder, f"{original_file_name}.jpg")  # Default to JPG if neither PNG nor JPG selected

                                with open(image_path, 'wb') as f:
                                    f.write(response.content)
                                print(f'Capa do jogo "{game_name}" baixada e salva em: {image_path}')
                            else:
                                print(f'Erro ao baixar a capa do jogo "{game_name}": Status {response.status_code}')
                        else:
                            print(f'Capa do jogo "{game_name}" não encontrada.')
                else:
                    print(f'Capa do jogo "{game_name}" não encontrada.')
            else:
                print(f'Capa do jogo "{game_name}" não encontrada.')
        else:
            print(f'Jogo "{game_name}" não encontrado para a plataforma "{platform_id}".')
    else:
        print(f'Jogo "{game_name}" não encontrado para a plataforma "{platform_id}".')
    progress_var.set(progress_var.get() + 1)

# Função para iniciar o download das capas
def start_download(folder_path, output_folder, progress_var, progress_bar, cancel_flag, save_as_png_var, save_as_jpg_var):
    platform_id = get_selected_platform_id()
    if platform_id is None:
        messagebox.showerror("Erro", "Por favor, selecione uma plataforma válida.")
        return
    
    
    game_names = get_game_names_from_folder(folder_path)
    progress_bar['maximum'] = len(game_names)
    progress_var.set(0)

    # Convertendo os valores booleanos dos checkboxes para True/False
    save_as_png = save_as_png_var.get() == 1
    save_as_jpg = save_as_jpg_var.get() == 1

    # Chamada para iniciar o download das capas
    for game_name, original_file_name in game_names:
        if cancel_flag[0]:
            break

        download_game_cover(game_name, platform_id, output_folder, progress_var, original_file_name, save_as_png, save_as_jpg)
        progress_bar.update()

    messagebox.showinfo("Download", "Download concluído!" if not cancel_flag[0] else "Download cancelado!")

# Função para selecionar a pasta de entrada
def select_input_folder():
    folder_selected = filedialog.askdirectory()
    input_folder_var.set(folder_selected)

# Função para selecionar a pasta de saída
def select_output_folder():
    folder_selected = filedialog.askdirectory()
    output_folder_var.set(folder_selected)

# Função para cancelar o download
def cancel_download():
    cancel_flag[0] = True

# Função para obter o código da plataforma selecionada
def get_selected_platform_id():
    selected_platform = platform_combo.get()
    for platform in plataformas:
        if selected_platform == platform[1]:
            return platform[0]
    return None

# Interface gráfica
root = tk.Tk()
root.title("Programa de Download de Capas de Jogos")
root.geometry("500x790")
root.configure(background='light blue')

# Definindo ícone
icon_path = 'C:/Users/USER/OneDrive/Imagens/teste.ico'
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

input_folder_var = tk.StringVar()
output_folder_var = tk.StringVar()
platform_var = tk.StringVar()
progress_var = tk.IntVar()
save_as_png_var = tk.IntVar()
save_as_jpg_var = tk.IntVar()
cancel_flag = [False]



# Pasta para guardar as img.
label = tk.Label(root, text="Pasta dos Jogos:", background='light blue', font=('Arial', 12, 'bold'))
label.pack(pady=5)
entry = tk.Entry(root, textvariable=input_folder_var, width=50, font=('Arial', 10))
entry.pack(pady=5)
button = tk.Button(root, text="Selecionar Pasta", command=select_input_folder, font=('Arial', 10, 'bold'))
button.pack(pady=5)




# Pasta para guardar as img.
label1 = tk.Label(root, text="Pasta das Imagens", background='light blue', font=('Arial', 12, 'bold'))
label1.pack(pady=5)
entry = tk.Entry(root, textvariable=output_folder_var, width=50, font=('Arial', 10))
entry.pack(pady=5)
button = tk.Button(root, text="Selecionar Pasta", command=select_output_folder, font=('Arial', 10, 'bold'))
button.pack(pady=5)





# Combobox para selecionar a plataforma
tk.Label(root, text="Selecione a Plataforma:", background='light blue',font=('Arial', 12, 'bold')).pack(pady=5)
platform_combo = ttk.Combobox(root, textvariable=platform_var, values=[platform[1] for platform in plataformas], width=47)
platform_combo.pack(pady=5)

# Barra de progresso
progress_bar = Progressbar(root, length=300, variable=progress_var)
progress_bar.pack(pady=5)

# Botões para iniciar e cancelar o download
tk.Button(root, text="Iniciar Download",font=('Arial', 12, 'bold'), command=lambda: Thread(target=start_download, args=(input_folder_var.get(), output_folder_var.get(), progress_var, progress_bar, cancel_flag,save_as_png_var, save_as_jpg_var)).start()).pack(pady=5)
tk.Button(root, text="Cancelar Download", font=('Arial', 12, 'bold'),command=cancel_download).pack(pady=5)

# Verificação de atualizações
check_for_updates()



ttk.Checkbutton(root, text="Salvar como PNG", variable=save_as_png_var).pack(padx=5, pady=5, anchor=tk.CENTER)
ttk.Checkbutton(root, text="Salvar como JPG", variable=save_as_jpg_var).pack(padx=5, pady=5, anchor=tk.CENTER)


# Imagem do programa
image_path = 'C:/Users/USER/OneDrive/Imagens/test.png'  # Substitua pelo caminho correto da sua imagem
if os.path.exists(image_path):
    image = tk.PhotoImage(file=image_path)
    image = image.subsample(2, 2)
    image_label = tk.Label(root, image=image, background='light blue')
    image_label.pack(pady=10)
    


# informações do programa
label_text = "Programa criado por: @Phoenixx1202"
bold_font = ('Arial', 12, 'bold')
label = tk.Label(root, text=label_text, background='light blue', font=bold_font)
label.pack(side="bottom", pady=10)

version_label = tk.Label(root, text=f'Versão Atual: {get_current_version()}', background='light blue', font=('Arial', 12, 'bold'))
version_label.pack(pady=10)

root.mainloop()
