from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
import csv
from .person import Person
from .company import Company
from .search import LeadSearch
from .utils import linkedin_login, save_to_csv, categorize_company

class LeadFinder:
    """
    Main class for finding leads on LinkedIn using tags and audience categories
    """
    def __init__(self, username=None, password=None, headless=False):
        self.username = username
        self.password = password
        self.headless = headless
        self.driver = None
        self.search = None
        self.leads = []
        self.tagged_leads = {}
        self.categorized_companies = {}
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()
            
    def initialize(self):
        """Initialize the web driver and log in to LinkedIn"""
        # Set up Chrome options
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        
        # Initialize Chrome driver
        try:
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
                print("Could not initialize Chrome driver. Make sure Chrome is installed.")
                return False
                
        self.driver.maximize_window()
        
        # Log in to LinkedIn
        success = linkedin_login(self.driver, self.username, self.password)
        if not success:
            print("Failed to log in to LinkedIn. Please check your credentials.")
            self.driver.quit()
            return False
            
        # Initialize search
        self.search = LeadSearch(driver=self.driver, close_on_complete=False)
        return True
        
    def find_people_leads(self, keywords, location=None, industry=None, company=None, school=None, connection_level=None, limit=10):
        """
        Find people leads based on search criteria
        
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
        if self.search is None:
            if not self.initialize():
                return []
                
        people = self.search.search_people(
            keywords=keywords,
            location=location,
            industry=industry,
            company=company,
            school=school,
            connection_level=connection_level,
            limit=limit
        )
        
        self.leads.extend(people)
        return people
        
    def find_company_leads(self, keywords, industry=None, company_size=None, location=None, limit=10):
        """
        Find company leads based on search criteria
        
        Args:
            keywords (str): Search keywords
            industry (str): Industry filter
            company_size (str): Company size filter
            location (str): Location filter
            limit (int): Maximum number of results to return
            
        Returns:
            list: List of Company objects
        """
        if self.search is None:
            if not self.initialize():
                return []
                
        companies = self.search.search_companies(
            keywords=keywords,
            industry=industry,
            company_size=company_size,
            location=location,
            limit=limit
        )
        
        # Auto-categorize companies
        for company in companies:
            category = categorize_company(company.to_dict())
            company.set_category(category)
            
            # Add to categorized companies
            if category not in self.categorized_companies:
                self.categorized_companies[category] = []
            self.categorized_companies[category].append(company)
            
        self.leads.extend(companies)
        return companies
        
    def tag_lead(self, lead, tag):
        """
        Add a tag to a lead
        
        Args:
            lead (Person or Company): Lead to tag
            tag (str): Tag to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        if isinstance(lead, Person):
            lead.add_tag(tag)
        elif isinstance(lead, Company):
            lead.set_category(tag)
        else:
            return False
            
        # Add to tagged leads
        if tag not in self.tagged_leads:
            self.tagged_leads[tag] = []
        self.tagged_leads[tag].append(lead)
        
        return True
        
    def get_leads_by_tag(self, tag):
        """
        Get leads by tag
        
        Args:
            tag (str): Tag to filter by
            
        Returns:
            list: List of leads with the specified tag
        """
        return self.tagged_leads.get(tag, [])
        
    def get_leads_by_category(self, category):
        """
        Get company leads by category
        
        Args:
            category (str): Category to filter by
            
        Returns:
            list: List of company leads with the specified category
        """
        return self.categorized_companies.get(category, [])
        
    def search_by_tags(self, tags):
        """
        Search for leads with specific tags
        
        Args:
            tags (list): List of tags to search for
            
        Returns:
            list: List of leads with any of the specified tags
        """
        results = []
        for tag in tags:
            if tag in self.tagged_leads:
                results.extend(self.tagged_leads[tag])
                
        return results
        
    def search_by_categories(self, categories):
        """
        Search for company leads with specific categories
        
        Args:
            categories (list): List of categories to search for
            
        Returns:
            list: List of company leads with any of the specified categories
        """
        results = []
        for category in categories:
            if category in self.categorized_companies:
                results.extend(self.categorized_companies[category])
                
        return results
        
    def save_leads(self, filename, leads=None, format='json'):
        """
        Save leads to a file
        
        Args:
            filename (str): Name of the file to save leads to
            leads (list): List of leads to save (defaults to all leads)
            format (str): File format ('json' or 'csv')
            
        Returns:
            bool: True if successful, False otherwise
        """
        if leads is None:
            leads = self.leads
            
        if not leads:
            print("No leads to save.")
            return False
            
        # Convert leads to dictionaries
        leads_dict = [lead.to_dict() for lead in leads]
        
        if format.lower() == 'json':
            try:
                with open(filename, 'w') as f:
                    json.dump(leads_dict, f, indent=4)
                return True
            except Exception as e:
                print(f"Error saving leads to JSON: {e}")
                return False
        elif format.lower() == 'csv':
            return save_to_csv(leads_dict, filename)
        else:
            print(f"Unsupported format: {format}")
            return False
            
    def load_leads(self, filename, format='json'):
        """
        Load leads from a file
        
        Args:
            filename (str): Name of the file to load leads from
            format (str): File format ('json' or 'csv')
            
        Returns:
            list: List of dictionaries containing lead data
        """
        if format.lower() == 'json':
            try:
                with open(filename, 'r') as f:
                    leads = json.load(f)
                return leads
            except Exception as e:
                print(f"Error loading leads from JSON: {e}")
                return []
        elif format.lower() == 'csv':
            try:
                leads = []
                with open(filename, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        leads.append(row)
                return leads
            except Exception as e:
                print(f"Error loading leads from CSV: {e}")
                return []
        else:
            print(f"Unsupported format: {format}")
            return []
            
    def close(self):
        """Close the web driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.search = None
