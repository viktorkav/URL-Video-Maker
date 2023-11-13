from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import os
import subprocess
import time
import av
import numpy as np

# Configurações
url = 'https://pyav.org/docs/stable/'
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

def create_pan_down_video_pyav(image_path, output_video, duration, fps):
    # Carrega a imagem e obtém suas dimensões
    img = Image.open(image_path)
    img_width, img_height = img.size

    # Se a imagem capturada for menor que a altura do vídeo, não será possível fazer o scroll
    if img_height < 2160:
        raise ValueError("A altura da imagem capturada é menor que a altura necessária para o vídeo (2160 pixels).")

    # Taxa de rolagem
    scroll_rate = (img_height - 2160) / (duration * fps)

    # Criação do contêiner de saída
    output_container = av.open(output_video, mode='w')

    # Criação do stream de vídeo
    stream = output_container.add_stream('mpeg4', rate=fps)
    stream.width = 3840
    stream.height = 2160
    stream.pix_fmt = 'yuv420p'

    for frame_number in range(duration * fps):
        img_frame = Image.new("RGB", (3840, 2160), (255, 255, 255))
        scroll_pos = int(min(frame_number * scroll_rate, img_height - 2160))

        img_frame.paste(img.crop((0, scroll_pos, 3840, scroll_pos + 2160)), (0, 0))

        # Conversão da imagem PIL para frame de vídeo
        frame = av.VideoFrame.from_image(img_frame)
        
        # Codificação do frame
        for packet in stream.encode(frame):
            output_container.mux(packet)

    # Finalizando a codificação
    for packet in stream.encode():
        output_container.mux(packet)

    # Fechando o contêiner
    output_container.close()




# Execução
capture_fullpage_screenshot(url, output_image_path)
create_pan_down_video_pyav(output_image_path, output_video_path, duration, fps)
