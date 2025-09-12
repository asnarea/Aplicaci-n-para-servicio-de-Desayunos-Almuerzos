from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

URL_CAMARA     = "http://10.150.22.49"
USUARIO_CAM    = "admin"
CLAVE_CAM      = "Telco6719"
URL_LOGIN      = f"{URL_CAMARA}/#/"
URL_CFG_GENERAL = f"{URL_CAMARA}/doc/index.html#/heop/appShow/generalIntelligentCfg"

SELECTOR_USUARIO  = 'input.el-input__inner[placeholder="Nombre de usuario"]'
SELECTOR_CLAVE    = 'input.el-input__inner[placeholder="Contraseña"]'
SELECTOR_BOTON    = 'button:has-text("Iniciar sesión")'

SELECTOR_TAB_BIBLIOTECA   = '#tab-faceLibrary'
SELECTOR_GRUPO_PRUEBA_FR  = 'div.group-count-div:has(span.groupName:has-text("PRUEBA FR"))'

RUTA_FOTO = Path("media/fotos/123.jpg").resolve()
SELECTOR_BOTON_ANADE = 'button[title="Añade"]'
SELECTOR_INPUT_FILE = 'input[name="importImage"]'

def iniciar_sesion():
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=False)  # True si no quieres ver ventana
        pagina = navegador.new_page()
        pagina.goto(URL_LOGIN, wait_until="networkidle")

        pagina.wait_for_selector(SELECTOR_USUARIO, timeout=15000)
        pagina.fill(SELECTOR_USUARIO, USUARIO_CAM)
        pagina.fill(SELECTOR_CLAVE, CLAVE_CAM)
        pagina.click(SELECTOR_BOTON)
        pagina.wait_for_load_state("networkidle")
        pagina.wait_for_timeout(2000)

        pagina.goto(URL_CFG_GENERAL, wait_until="networkidle")
        pagina.wait_for_timeout(500)

        pagina.wait_for_selector(SELECTOR_TAB_BIBLIOTECA, timeout=5000)
        pagina.click(SELECTOR_TAB_BIBLIOTECA)
        pagina.wait_for_load_state("networkidle")

        pagina.wait_for_selector(SELECTOR_GRUPO_PRUEBA_FR, timeout=5000)
        pagina.click(SELECTOR_GRUPO_PRUEBA_FR)
        pagina.wait_for_load_state("networkidle")

        #pagina.wait_for_selector(SELECTOR_BOTON_ANADE,state="visible", timeout=20000)
        #pagina.click(SELECTOR_BOTON_ANADE)
        boton = pagina.get_by_role("button", name="Añade")
        boton.click()

        pagina.wait_for_selector(SELECTOR_INPUT_FILE, state="attached", timeout=5000)
        pagina.locator(SELECTOR_INPUT_FILE).first.set_input_files(str(RUTA_FOTO))

        pagina.wait_for_timeout(3000)
        print(f"Foto enviada al input: {RUTA_FOTO}")
        navegador.close()

if __name__ == "__main__":
    iniciar_sesion()
