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
        
        # Crear un superusuari
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()

    @classmethod
    def tearDownClass(cls):
        #cls.selenium.quit()
        super().tearDownClass()

    def test_create_questions_with_choices(self):
        # Iniciar sesio
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        self.selenium.find_element(By.NAME, "username").send_keys('isard')
        self.selenium.find_element(By.NAME, "password").send_keys('pirineus')
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()
        
        # Verificar la pagina de administracio
        self.assertEqual(self.selenium.title, "Site administration | Django site admin")
        
        # Crear una Question  1 Choice
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/polls/question/add/'))
        self.selenium.find_element(By.NAME, "question_text").send_keys("Pregunta con una opción")
        self.selenium.find_element(By.TAG_NAME, "details").click()  
        self.selenium.find_element(By.NAME, "pub_date_0").send_keys("2023-11-01")
        self.selenium.find_element(By.NAME, "pub_date_1").send_keys("14:30")  
        
        # El primer Choice inline
        choice_input = self.selenium.find_element(By.NAME, "choice_set-0-choice_text")
        choice_input.send_keys("Primera opción")
        
        # Guardar la pregunta amb el Choice
        self.selenium.find_element(By.NAME, "_save").click()
        
        # Crear altre Question amb 100 Choices
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/polls/question/add/'))
        self.selenium.find_element(By.NAME, "question_text").send_keys("Pregunta con 100 opciones")
        self.selenium.find_element(By.TAG_NAME, "details").click()  
        self.selenium.find_element(By.NAME, "pub_date_0").send_keys("2023-11-01")
        self.selenium.find_element(By.NAME, "pub_date_1").send_keys("14:30")  
        # 100 Choices en bucle
        for i in range(100):
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.NAME, f"choice_set-{i}-choice_text"))
            )
            choice_text_input = self.selenium.find_element(By.NAME, f"choice_set-{i}-choice_text")
            choice_text_input.send_keys(self.random_text())
            
            if i < 99:  # No mes 
                self.selenium.find_element(By.LINK_TEXT, "Add another Choice").click()
        
        # Guardar la pregunta i 100 Choices
        self.selenium.find_element(By.NAME, "_save").click()
        
        # Verificar que Choices están disponibles en el menú Choices
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/polls/choice/'))

        choices_count = self.selenium.find_element(By.CSS_SELECTOR, "p.paginator").text
        self.assertIn("101 choices", choices_count)
    	
    @staticmethod
    def random_text():
        """text aleatori de 10 caracteres per els Choices."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))