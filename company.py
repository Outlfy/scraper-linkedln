import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
from .utils import linkedin_login

class Company:
    """
    Company class for LinkedIn company profiles
    """
    def __init__(self, linkedin_url=None, name=None, driver=None, close_on_complete=True):
        self.linkedin_url = linkedin_url
        self.name = name
        self.driver = driver
        self.close_on_complete = close_on_complete
        self.about_us = None
        self.website = None
        self.industry = None
        self.company_size = None
        self.headquarters = None
        self.founded = None
        self.specialties = []
        self.showcase_pages = []
        self.affiliated_companies = []
        self.employees = []
        self.category = None
        self.scrape()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.close_on_complete:
            self.driver.quit()
            
    def scrape(self):
        if self.driver is None:
            try:
                # Setup Chrome options
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                
                # Initialize Chrome driver with webdriver_manager
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                print(f"Error initializing Chrome driver: {e}")
                print("Trying alternative setup...")
                try:
                    # Alternative setup using Service
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                except Exception as e:
                    print(f"Error with alternative setup: {e}")
                    raise Exception("Could not initialize Chrome driver. Make sure Chrome is installed.")
            
        if self.linkedin_url is not None:
            self.driver.get(self.linkedin_url)
            self._scrape_company()
        elif self.name is not None:
            self.driver.get(f"https://www.linkedin.com/search/results/companies/?keywords={self.name}")
            self._find_company_by_name()
            
    def _find_company_by_name(self):
        try:
            search_results = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-result__info"))
            )
            if search_results:
                search_results[0].click()
                time.sleep(3)
                self._scrape_company()
        except (NoSuchElementException, TimeoutException):
            print(f"Could not find {self.name}")
            
    def _scrape_company(self):
        try:
            # Get company name
            self.name = self.driver.find_element(By.CSS_SELECTOR, ".org-top-card-summary__title").text
            
            # Get about us
            try:
                about_tab = self.driver.find_element(By.XPATH, "//a[contains(@href, '/about/')]")
                about_tab.click()
                time.sleep(2)
                
                self.about_us = self.driver.find_element(By.CSS_SELECTOR, ".org-about-us-organization-description__text").text
                
                # Get company details
                details = self.driver.find_elements(By.CSS_SELECTOR, ".org-about-company-module__container")
                for detail in details:
                    label = detail.find_element(By.CSS_SELECTOR, ".org-about-company-module__label").text
                    value = detail.find_element(By.CSS_SELECTOR, ".org-about-company-module__text").text
                    
                    if "Website" in label:
                        self.website = value
                    elif "Industry" in label:
                        self.industry = value
                    elif "Company size" in label:
                        self.company_size = value
                    elif "Headquarters" in label:
                        self.headquarters = value
                    elif "Founded" in label:
                        self.founded = value
                        
                # Get specialties
                try:
                    specialties = self.driver.find_element(By.CSS_SELECTOR, ".org-about-company-module__specialities").text
                    self.specialties = [s.strip() for s in specialties.split(",")]
                except NoSuchElementException:
                    pass
                    
            except (NoSuchElementException, TimeoutException):
                pass
                
            # Get showcase pages
            try:
                showcase_tab = self.driver.find_element(By.XPATH, "//a[contains(@href, '/showcase/')]")
                showcase_tab.click()
                time.sleep(2)
                
                showcase_elements = self.driver.find_elements(By.CSS_SELECTOR, ".org-showcase-pages-module__page-name")
                for showcase in showcase_elements:
                    self.showcase_pages.append(showcase.text)
            except (NoSuchElementException, TimeoutException):
                pass
                
            # Get affiliated companies
            try:
                affiliated_tab = self.driver.find_element(By.XPATH, "//a[contains(@href, '/affiliated-companies/')]")
                affiliated_tab.click()
                time.sleep(2)
                
                affiliated_elements = self.driver.find_elements(By.CSS_SELECTOR, ".org-affiliated-companies-module__company-name")
                for affiliated in affiliated_elements:
                    self.affiliated_companies.append(affiliated.text)
            except (NoSuchElementException, TimeoutException):
                pass
                
            # Get employees (sample)
            try:
                people_tab = self.driver.find_element(By.XPATH, "//a[contains(@href, '/people/')]")
                people_tab.click()
                time.sleep(2)
                
                employee_elements = self.driver.find_elements(By.CSS_SELECTOR, ".org-people-profile-card__profile-title")
                for i, employee in enumerate(employee_elements):
                    if i >= 10:  # Limit to 10 employees
                        break
                    name = employee.text
                    try:
                        title = employee.find_element(By.CSS_SELECTOR, ".org-people-profile-card__profile-position").text
                        self.employees.append({"name": name, "title": title})
                    except NoSuchElementException:
                        self.employees.append({"name": name})
            except (NoSuchElementException, TimeoutException):
                pass
                
        except Exception as e:
            print(f"Error scraping company: {e}")
            
    def set_category(self, category):
        """Set the audience category for this company"""
        self.category = category
        
    def get_category(self):
        """Get the audience category for this company"""
        return self.category
            
    def to_dict(self):
        """Convert the company profile to a dictionary"""
        return {
            "name": self.name,
            "about_us": self.about_us,
            "website": self.website,
            "industry": self.industry,
            "company_size": self.company_size,
            "headquarters": self.headquarters,
            "founded": self.founded,
            "specialties": self.specialties,
            "showcase_pages": self.showcase_pages,
            "affiliated_companies": self.affiliated_companies,
            "employees": self.employees,
            "category": self.category,
            "linkedin_url": self.linkedin_url
        }
