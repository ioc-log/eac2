import random
import string
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from polls.models import Question, Choice

class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
        
        # Crear un superusuario
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_create_questions_with_choices(self):
        # Iniciar sesión
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        self.selenium.find_element(By.NAME, "username").send_keys('isard')
        self.selenium.find_element(By.NAME, "password").send_keys('pirineus')
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()
        
        # Verificar la página de administración
        self.assertEqual(self.selenium.title, "Site administration | Django site admin")
        
        # Crear una Question con 1 Choice
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/polls/question/add/'))
        self.selenium.find_element(By.NAME, "question_text").send_keys("Pregunta con una opción")
        self.selenium.find_element(By.TAG_NAME, "details").click()  # Abre el desplegable
        self.selenium.find_element(By.NAME, "pub_date_0").send_keys("2023-11-01")
        
        # Añadir el primer Choice inline
        choice_input = self.selenium.find_element(By.NAME, "choice_set-0-choice_text")
        choice_input.send_keys("Primera opción")
        
        # Guardar la pregunta con el Choice
        self.selenium.find_element(By.NAME, "_save").click()
        
        # Crear otra Question con 100 Choices
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/polls/question/add/'))
        self.selenium.find_element(By.NAME, "question_text").send_keys("Pregunta con 100 opciones")
        self.selenium.find_element(By.NAME, "pub_date").send_keys("2023-11-01")
        
        # Añadir 100 Choices utilizando el bucle
        for i in range(100):
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.NAME, f"choice_set-{i}-choice_text"))
            )
            choice_text_input = self.selenium.find_element(By.NAME, f"choice_set-{i}-choice_text")
            choice_text_input.send_keys(self.random_text())
            
            if i < 99:  # No agregar un nuevo Choice después de la última
                self.selenium.find_element(By.LINK_TEXT, "Add another Choice").click()
        
        # Guardar la pregunta con los 100 Choices
        self.selenium.find_element(By.NAME, "_save").click()
        
        # Verificar que los Choices están disponibles en el menú de Choices
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/polls/choice/'))
        
        # Contar el número de filas en la lista de Choices
        choices_count = len(self.selenium.find_elements(By.CLASS_NAME, 'row'))
        self.assertEqual(choices_count, 101)
    
    @staticmethod
    def random_text():
        """Genera un texto aleatorio de 10 caracteres para los Choices."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))