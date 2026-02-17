import os
import imaplib
import email
import requests
import shutil
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- CONFIGURAÇÕES ---
load_dotenv()
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
IMAP_SERVER = 'imap.gmail.com'
PASTA_DOWNLOADS = 'downloads'
DIAS_RETENCAO = 30  # Deleta pastas com mais de 30 dias

def limpar_backups_antigos():
    """Remove pastas de downloads mais antigas que a retenção"""
    limite = datetime.now() - timedelta(days=DIAS_RETENCAO)
    if not os.path.exists(PASTA_DOWNLOADS): return

    for item in os.listdir(PASTA_DOWNLOADS):
        caminho = os.path.join(PASTA_DOWNLOADS, item)
        if os.path.isdir(caminho):
            try:
                data_pasta = datetime.strptime(item, '%Y-%m-%d')
                if data_pasta < limite:
                    print(f"🧹 Removendo backup antigo: {item}")
                    shutil.rmtree(caminho)
            except ValueError:
                continue

def extrair_link(html):
    """Encontra o link href na palavra 'aqui'"""
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a', href=True):
        if "aqui" in a.text.lower():
            return a['href']
    return None

def baixar_arquivo(url, pasta_data):
    """Baixa o arquivo APENAS se ele ainda não existir"""
    if not os.path.exists(pasta_data):
        os.makedirs(pasta_data)
    
    nome_arquivo = "fiscal_flow_docs.zip"
    caminho_final = os.path.join(pasta_data, nome_arquivo)
    
    # --- PROTEÇÃO CONTRA DUPLICIDADE ---
    if os.path.exists(caminho_final):
        print(f" Arquivo já existe: {caminho_final}. Plando download.")
        return
    # -----------------------------------

    print(f" Baixando de: {url}")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(caminho_final, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f" Sucesso! Salvo em: {caminho_final}")
    except Exception as e:
        print(f" Erro no download: {e}")
        # Remove arquivo corrompido/vazio se der erro
        if os.path.exists(caminho_final):
            os.remove(caminho_final)

def processar_emails():
    print(f"[{datetime.now()}] Conectando ao Gmail...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select('inbox')

        # Busca apenas e-mails NÃO LIDOS (UNSEEN)
        criterio = '(UNSEEN FROM "noreply@fiscalflow.linx.com.br")'
        status, data = mail.search(None, criterio)
        
        ids = data[0].split()
        if not ids:
            print("ℹ️ Nenhum e-mail novo (não lido) encontrado.")
        else:
            for num in ids:
                status, data = mail.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(data[0][1])
                
                # Extrai corpo HTML
                html_content = None
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/html":
                            html_content = part.get_payload(decode=True).decode()
                            break
                else:
                    html_content = msg.get_payload(decode=True).decode()

                if html_content:
                    link = extrair_link(html_content)
                    if link:
                        # Usa data de HOJE para a pasta
                        pasta_hoje = os.path.join(PASTA_DOWNLOADS, datetime.now().strftime('%Y-%m-%d'))
                        baixar_arquivo(link, pasta_hoje)
                
        mail.logout()
        limpar_backups_antigos()
    except Exception as e:
        print(f"Erro geral: {e}")

if __name__ == "__main__":
    processar_emails()
