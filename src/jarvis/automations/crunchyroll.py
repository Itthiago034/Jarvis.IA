import pyautogui  # type: ignore[reportMissingModuleSource]
import time
from pathlib import Path

# Caminho para a pasta de imagens
ASSETS_DIR = Path(__file__).parent.parent.parent.parent / "assets" / "images"

def abrir_crunchyroll():
    print("Claro chefe, abrindo a Crunchyroll")
    pyautogui.press('win')
    time.sleep(0.5)
    pyautogui.write('Crunchyroll')
    time.sleep(0.3)
    pyautogui.press('enter')
    time.sleep(5)
    pyautogui.hotkey('win', 'up')
    time.sleep(2)

def fazer_login():
    botao_login = pyautogui.locateOnScreen(str(ASSETS_DIR / 'login_button.png'), confidence=0.8)
    if botao_login:
        print("Tela de login inicial detectada!")
        pyautogui.click(botao_login)
        time.sleep(3)
        pyautogui.press('escape')
        time.sleep(0.5)
        print("Digitando email...")
        pyautogui.write('kiyottiago@gmail.com', interval=0.08)
        time.sleep(0.8)
        pyautogui.press('enter')
        time.sleep(3)
        print("Clicando no botão LOGIN laranja...")
        pyautogui.click(x=921, y=626)
        time.sleep(5)
        return True
    return False

def selecionar_perfil():
    print("Procurando o perfil do Kiyottiago na tela...")
    time.sleep(3)  # Aguarda a tela carregar completamente
    perfil = pyautogui.locateOnScreen(str(ASSETS_DIR / 'kiyottiago_perfil.png'), confidence=0.8)
    if perfil:
        pyautogui.click(perfil)
        print("Perfil do Kiyottiago selecionado!")
    else:
        print("Perfil do Kiyottiago NÃO encontrado! Verifique a imagem e a tela.")

def fluxo_principal():
    abrir_crunchyroll()
    time.sleep(1)
    if fazer_login():
        selecionar_perfil()
        print("Perfil selecionado com sucesso após login!")
    else:
        print("Tela de seleção de perfil detectada! (Já estava logado)")
        selecionar_perfil()
        print("Perfil selecionado direto!")

if __name__ == "__main__":
    fluxo_principal()
    # Aqui você pode adicionar a automação para buscar e iniciar o anime desejado