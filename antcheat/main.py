import time
import os
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

API_URL = "http://exemplo.com/api/arquivo-alterado"

directory_to_watch = "/mnt/c/Users/Administrator/Documents/Euro Truck Simulator 2"

if not os.path.exists(directory_to_watch):
    raise ValueError(f"Diretório '{directory_to_watch}' não encontrado.")


monitored_files = ['config.cfg']

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        if filename in monitored_files:
            print(f"Arquivo alterado: {filename}")
            
            changed_content = read_changed_content(filepath)
            if changed_content:
                
                previous_content = get_previous_content(filepath)
                diff = compare_content(previous_content, changed_content)
                
                if diff:
                    #print("Alterações no arquivo:")
                    for line in diff:
                        if line.startswith('+') or line.startswith('-'):
                            print(line.strip())
                
                update_previous_content(filepath, changed_content)
                send_post(filepath, changed_content)

def read_changed_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            changed_content = file.read()
            return changed_content
    except Exception as e:
        print(f"Erro ao ler conteúdo do arquivo alterado: {e}")
        return None

def get_previous_content(filepath):
    try:
        previous_content = ""
        previous_file = f"{filepath}.previous"
        if os.path.exists(previous_file):
            with open(previous_file, 'r', encoding='utf-8') as file:
                previous_content = file.read()
        return previous_content
    except Exception as e:
        print(f"Erro ao ler conteúdo anterior do arquivo: {e}")
        return ""

def compare_content(previous_content, current_content):
    
    import difflib
    differ = difflib.Differ()
    diff = list(differ.compare(previous_content.splitlines(), current_content.splitlines()))
    return diff

def update_previous_content(filepath, content):
    try:
        previous_file = f"{filepath}.previous"
        with open(previous_file, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"Erro ao atualizar conteúdo anterior do arquivo: {e}")

def send_post(filepath, content):
    try:
        data = {
            'filepath': filepath,
            'content': content
        }
        response = requests.post(API_URL, json=data)
        #print(f"Resposta da API: {response.status_code}")
    except Exception as e:
        print(f"Erro ao enviar POST para a API: {e}")

if __name__ == "__main__":
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, directory_to_watch, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
