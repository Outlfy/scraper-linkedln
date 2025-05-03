from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
import time
import json
import os
from .person import Person
from .company import Company
from .utils import linkedin_login

class LeadSearch:
    """
    Class for searching LinkedIn for leads based on various criteria
    """
    def __init__(self, driver=None, close_on_complete=True):
        self.driver = driver
        self.close_on_complete = close_on_complete
        self.search_results = []
        self.people_results = []
        self.company_results = []
        
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
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.close_on_complete:
            self.driver.quit()
            
    def search_people(self, keywords, location=None, industry=None, company=None, school=None, connection_level=None, limit=10):
        """
        Search for people on LinkedIn based on various filters
        
        Args:
            keywords (str): Search keywords
            location (str): Location filter
            industry (str): Industry filter
            company (str): Company filter
            school (str): School filter
            connection_level (str): Connection level (1st, 2nd, 3rd)
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of Person objects
        """
        # Build search URL
        base_url = "https://www.linkedin.com/search/results/people/?keywords="
        search_url = f"{base_url}{keywords.replace(' ', '%20')}"
        
        if location:
            search_url += f"&geoUrn=%5B%22{location.replace(' ', '%20')}%22%5D"
            
        # Navigate to search URL
        self.driver.get(search_url)
        time.sleep(3)
        
        # Apply filters if provided
        if any([industry, company, school, connection_level]):
            try:
                # Click on All Filters button
                all_filters_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'All filters')]")
                all_filters_button.click()
                time.sleep(2)
                
                # Apply industry filter
                if industry:
                    industry_dropdown = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Industry')]")
                    industry_dropdown.click()
                    time.sleep(1)
                    
                    industry_option = self.driver.find_element(By.XPATH, f"//label[contains(text(), '{industry}')]")
                    industry_option.click()
                    
                # Apply company filter
                if company:
                    company_input = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Current company')]/..//input")
                    company_input.send_keys(company)
                    time.sleep(1)
                    
                    # Select first option
                    company_input.send_keys(Keys.DOWN)
                    company_input.send_keys(Keys.ENTER)
                    
                # Apply school filter
                if school:
                    school_input = self.driver.find_element(By.XPATH, "//label[contains(text(), 'School')]/..//input")
                    school_input.send_keys(school)
                    time.sleep(1)
                    
                    # Select first option
                    school_input.send_keys(Keys.DOWN)
                    school_input.send_keys(Keys.ENTER)
                    
                # Apply connection level filter
                if connection_level:
                    if connection_level == "1st":
                        connection_option = self.driver.find_element(By.XPATH, "//label[contains(text(), '1st')]")
                    elif connection_level == "2nd":
                        connection_option = self.driver.find_element(By.XPATH, "//label[contains(text(), '2nd')]")
                    elif connection_level == "3rd":
                        connection_option = self.driver.find_element(By.XPATH, "//label[contains(text(), '3rd')]")
                        
                    connection_option.click()
                    
                # Apply filters
                apply_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Show results')]")
                apply_button.click()
                time.sleep(3)
                
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Error applying filters: {e}")
                
        # Collect search results
        try:
            search_results = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".reusable-search__result-container"))
            )
            
            count = 0
            for result in search_results:
                if count >= limit:
                    break
                    
                try:
                    # Get profile link
                    profile_link = result.find_element(By.CSS_SELECTOR, ".app-aware-link").get_attribute("href")
                    
                    # Create Person object
                    person = Person(linkedin_url=profile_link, driver=self.driver, close_on_complete=False)
                    self.people_results.append(person)
                    count += 1
                    
                except (NoSuchElementException, TimeoutException):
                    continue
                    
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Error collecting search results: {e}")
            
        return self.people_results
        
    def search_companies(self, keywords, industry=None, company_size=None, location=None, limit=10):
        """
        Search for companies on LinkedIn based on various filters
        
        Args:
            keywords (str): Search keywords
            industry (str): Industry filter
            company_size (str): Company size filter
            location (str): Location filter
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of Company objects
        """
        # Build search URL
        base_url = "https://www.linkedin.com/search/results/companies/?keywords="
        search_url = f"{base_url}{keywords.replace(' ', '%20')}"
        
        # Navigate to search URL
        self.driver.get(search_url)
        time.sleep(3)
        
        # Apply filters if provided
        if any([industry, company_size, location]):
            try:
                # Click on All Filters button
                all_filters_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'All filters')]")
                all_filters_button.click()
                time.sleep(2)
                
                # Apply industry filter
                if industry:
                    industry_dropdown = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Industry')]")
                    industry_dropdown.click()
                    time.sleep(1)
                    
                    industry_option = self.driver.find_element(By.XPATH, f"//label[contains(text(), '{industry}')]")
                    industry_option.click()
                    
                # Apply company size filter
                if company_size:
                    size_dropdown = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Company size')]")
                    size_dropdown.click()
                    time.sleep(1)
                    
                    size_option = self.driver.find_element(By.XPATH, f"//label[contains(text(), '{company_size}')]")
                    size_option.click()
                    
                # Apply location filter
                if location:
                    location_input = self.driver.find_element(By.XPATH, "//label[contains(text(), 'Locations')]/..//input")
                    location_input.send_keys(location)
                    time.sleep(1)
                    
                    # Select first option
                    location_input.send_keys(Keys.DOWN)
                    location_input.send_keys(Keys.ENTER)
                    
                # Apply filters
                apply_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Show results')]")
                apply_button.click()
                time.sleep(3)
                
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Error applying filters: {e}")
                
        # Collect search results
        try:
            search_results = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".reusable-search__result-container"))
            )
            
            count = 0
            for result in search_results:
                if count >= limit:
                    break
                    
                try:
                    # Get company link
                    company_link = result.find_element(By.CSS_SELECTOR, ".app-aware-link").get_attribute("href")
                    
                    # Create Company object
                    company = Company(linkedin_url=company_link, driver=self.driver, close_on_complete=False)
                    self.company_results.append(company)
                    count += 1
                    
                except (NoSuchElementException, TimeoutException):
                    continue
                    
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Error collecting search results: {e}")
            
        return self.company_results
        
    def filter_by_tags(self, tags, results=None):
        """
        Filter search results by tags
        
        Args:
            tags (list): List of tags to filter by
            results (list): List of Person or Company objects to filter (defaults to all results)
            
        Returns:
            list: Filtered list of Person or Company objects
        """
        if results is None:
            results = self.people_results + self.company_results
            
        filtered_results = []
        
        for result in results:
            if isinstance(result, Person):
                # For Person objects, check if any of the specified tags are in the person's tags
                if any(tag in result.get_tags() for tag in tags):
                    filtered_results.append(result)
            elif isinstance(result, Company):
                # For Company objects, check if the company's category matches any of the specified tags
                if result.get_category() in tags:
                    filtered_results.append(result)
                    
        return filtered_results
        
    def save_results(self, filename, results=None):
        """
        Save search results to a JSON file
        
        Args:
            filename (str): Name of the file to save results to
            results (list): List of Person or Company objects to save (defaults to all results)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if results is None:
            results = self.people_results + self.company_results
            
        try:
            results_dict = []
            
            for result in results:
                results_dict.append(result.to_dict())
                
            with open(filename, 'w') as f:
                json.dump(results_dict, f, indent=4)
                
            return True
        except Exception as e:
            print(f"Error saving results: {e}")
            return False
            
    def load_results(self, filename):
        """
        Load search results from a JSON file
        
        Args:
            filename (str): Name of the file to load results from
            
        Returns:
            list: List of dictionaries containing search results
        """
        try:
            with open(filename, 'r') as f:
                results = json.load(f)
                
            return results
        except Exception as e:
            print(f"Error loading results: {e}")
            return []
