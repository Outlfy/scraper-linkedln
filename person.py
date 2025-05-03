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
import re
from .utils import linkedin_login

class Person:
    """
    Person class for LinkedIn profiles
    """
    def __init__(self, linkedin_url=None, name=None, driver=None, close_on_complete=True):
        self.linkedin_url = linkedin_url
        self.name = name
        self.driver = driver
        self.close_on_complete = close_on_complete
        self.skills = []
        self.experience = []
        self.education = []
        self.location = None
        self.headline = None
        self.summary = None
        self.tags = []
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
            self._scrape_profile()
        elif self.name is not None:
            self.driver.get(f"https://www.linkedin.com/search/results/people/?keywords={self.name}")
            self._find_person_by_name()
            
    def _find_person_by_name(self):
        try:
            search_results = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-result__info"))
            )
            if search_results:
                search_results[0].click()
                time.sleep(3)
                self._scrape_profile()
        except (NoSuchElementException, TimeoutException):
            print(f"Could not find {self.name}")
            
    def _scrape_profile(self):
        try:
            # Get name
            self.name = self.driver.find_element(By.CSS_SELECTOR, ".text-heading-xlarge").text
            
            # Get headline
            try:
                self.headline = self.driver.find_element(By.CSS_SELECTOR, ".text-body-medium").text
            except NoSuchElementException:
                self.headline = None
                
            # Get location
            try:
                self.location = self.driver.find_element(By.CSS_SELECTOR, ".text-body-small.inline.t-black--light.break-words").text
            except NoSuchElementException:
                self.location = None
                
            # Get summary
            try:
                self.driver.execute_script("window.scrollTo(0, 500)")
                time.sleep(1)
                self.summary = self.driver.find_element(By.CSS_SELECTOR, ".inline-show-more-text.inline-show-more-text--is-collapsed").text
            except NoSuchElementException:
                self.summary = None
                
            # Get experience
            try:
                self.driver.execute_script("window.scrollTo(0, 800)")
                time.sleep(1)
                experience_section = self.driver.find_element(By.ID, "experience-section")
                experience_elements = experience_section.find_elements(By.CSS_SELECTOR, ".pv-entity__position-group-pager")
                
                for experience in experience_elements:
                    company = experience.find_element(By.CSS_SELECTOR, ".pv-entity__secondary-title").text
                    title = experience.find_element(By.CSS_SELECTOR, ".t-16.t-black.t-bold").text
                    date_range = experience.find_element(By.CSS_SELECTOR, ".pv-entity__date-range span:nth-child(2)").text
                    
                    self.experience.append({
                        "company": company,
                        "title": title,
                        "date_range": date_range
                    })
            except (NoSuchElementException, TimeoutException):
                pass
                
            # Get education
            try:
                self.driver.execute_script("window.scrollTo(0, 1200)")
                time.sleep(1)
                education_section = self.driver.find_element(By.ID, "education-section")
                education_elements = education_section.find_elements(By.CSS_SELECTOR, ".pv-education-entity")
                
                for education in education_elements:
                    school = education.find_element(By.CSS_SELECTOR, ".pv-entity__school-name").text
                    degree = education.find_element(By.CSS_SELECTOR, ".pv-entity__degree-name").text
                    
                    self.education.append({
                        "school": school,
                        "degree": degree
                    })
            except (NoSuchElementException, TimeoutException):
                pass
                
            # Get skills
            try:
                self.driver.execute_script("window.scrollTo(0, 1500)")
                time.sleep(1)
                
                # Click on 'Show more skills' button if it exists
                try:
                    show_more_button = self.driver.find_element(By.CSS_SELECTOR, ".pv-skills-section__chevron-icon")
                    show_more_button.click()
                    time.sleep(1)
                except NoSuchElementException:
                    pass
                    
                skills_section = self.driver.find_element(By.ID, "skills-section")
                skill_elements = skills_section.find_elements(By.CSS_SELECTOR, ".pv-skill-category-entity__name-text")
                
                for skill in skill_elements:
                    self.skills.append(skill.text)
            except (NoSuchElementException, TimeoutException):
                pass
                
        except Exception as e:
            print(f"Error scraping profile: {e}")
            
    def add_tag(self, tag):
        """Add a custom tag to the person profile"""
        if tag not in self.tags:
            self.tags.append(tag)
            
    def remove_tag(self, tag):
        """Remove a tag from the person profile"""
        if tag in self.tags:
            self.tags.remove(tag)
            
    def get_tags(self):
        """Get all tags for this person"""
        return self.tags
            
    def to_dict(self):
        """Convert the person profile to a dictionary"""
        return {
            "name": self.name,
            "headline": self.headline,
            "location": self.location,
            "summary": self.summary,
            "experience": self.experience,
            "education": self.education,
            "skills": self.skills,
            "tags": self.tags,
            "linkedin_url": self.linkedin_url
        }
