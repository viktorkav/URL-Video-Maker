from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import os
import subprocess
import time

# Configurações
url = 'https://github.com/viktorkav'
output_folder = 'screenshots'
output_image = 'fullpage_screenshot.png'
output_video = 'output.mp4'
duration = 10  # Duração do vídeo em segundos
fps = 60      # Frames por segundo

# Certifique-se de que a pasta de saída existe
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
output_image_path = os.path.join(output_folder, output_image)
output_video_path = os.path.join(output_folder, output_video)

def capture_fullpage_screenshot(url, output_path):
    # Configurações do navegador
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_service = Service(ChromeDriverManager().install())

    # Iniciar o navegador
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get(url)

    # Aplicar zoom de 200%
    driver.execute_script("document.body.style.zoom='200%'")

    # Definir a largura da página para 3840 pixels
    driver.set_window_size(3840, 2160)  # Altura inicial grande para capturar todo conteúdo

    # Aguardar a renderização completa da página
    time.sleep(25)

    # Ajustar altura para capturar todo o conteúdo
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
    driver.set_window_size(3840, total_height)

    # Capturar screenshot da página inteira
    driver.save_screenshot(output_path)
    driver.quit()

def create_pan_down_video(image_path, output_video, duration, fps):
    # Carrega a imagem para obter suas dimensões
    img_width, img_height = Image.open(image_path).size

    # Se a imagem capturada for menor que a altura do vídeo, não será possível fazer o scroll
    if img_height < 2160:
        raise ValueError("A altura da imagem capturada é menor que a altura necessária para o vídeo (2160 pixels).")

    # Cálculo da taxa de rolagem baseada na altura da imagem e a duração do vídeo
    scroll_rate = (img_height - 2160) / (8 * duration)

    # Comando ffmpeg ajustado para o efeito de rolagem
    ffmpeg_cmd = f"ffmpeg -loop 1 -i {image_path} -vf \"crop=3840:2160:0:y='min(t*{scroll_rate},in_h-2160)'\" -t {duration} -r {fps} -pix_fmt yuv420p {output_video}"
    subprocess.call(ffmpeg_cmd, shell=True)




# Execução
capture_fullpage_screenshot(url, output_image_path)
create_pan_down_video(output_image_path, output_video_path, duration, fps)