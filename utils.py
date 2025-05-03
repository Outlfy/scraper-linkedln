from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import os
import json

def linkedin_login(driver, username=None, password=None):
    """
    Login to LinkedIn
    
    Args:
        driver (webdriver): Selenium webdriver instance
        username (str): LinkedIn username (email)
        password (str): LinkedIn password
        
    Returns:
        bool: True if login successful, False otherwise
    """
    # Check if credentials are provided
    if username is None or password is None:
        # Try to get credentials from environment variables
        username = os.environ.get('LINKEDIN_USERNAME')
        password = os.environ.get('LINKEDIN_PASSWORD')
        
        # If still not available, check for credentials file
        if username is None or password is None:
            try:
                with open('credentials.json', 'r') as f:
                    credentials = json.load(f)
                    username = credentials.get('username')
                    password = credentials.get('password')
            except (FileNotFoundError, json.JSONDecodeError):
                print("No credentials provided. Please provide username and password.")
                return False
                
    # Navigate to LinkedIn login page
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)
    
    try:
        # Enter username
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        username_field.send_keys(username)
        
        # Enter password
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        
        # Click login button
        login_button = driver.find_element(By.CSS_SELECTOR, ".btn__primary--large")
        login_button.click()
        
        # Wait for login to complete
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "global-nav"))
        )
        
        return True
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Login failed: {e}")
        return False
        
def save_to_csv(data, filename):
    """
    Save data to a CSV file
    
    Args:
        data (list): List of dictionaries to save
        filename (str): Name of the CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    import csv
    
    try:
        if not data:
            print("No data to save.")
            return False
            
        # Get headers from first dictionary
        headers = data[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
            
        return True
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False
        
def extract_skills_from_text(text):
    """
    Extract potential skills from text using common skill keywords
    
    Args:
        text (str): Text to extract skills from
        
    Returns:
        list: List of potential skills
    """
    # Common skill keywords
    common_skills = [
        "python", "java", "javascript", "html", "css", "sql", "nosql", "mongodb",
        "react", "angular", "vue", "node", "express", "django", "flask", "spring",
        "aws", "azure", "gcp", "cloud", "devops", "ci/cd", "docker", "kubernetes",
        "machine learning", "artificial intelligence", "data science", "big data",
        "analytics", "tableau", "power bi", "excel", "word", "powerpoint",
        "leadership", "management", "communication", "teamwork", "problem solving",
        "critical thinking", "creativity", "time management", "project management",
        "agile", "scrum", "waterfall", "lean", "six sigma", "marketing", "sales",
        "customer service", "social media", "seo", "sem", "content marketing",
        "email marketing", "digital marketing", "brand management", "product management",
        "ux", "ui", "user experience", "user interface", "graphic design", "photoshop",
        "illustrator", "indesign", "figma", "sketch", "adobe creative suite",
        "accounting", "finance", "bookkeeping", "quickbooks", "sap", "erp", "crm",
        "salesforce", "hubspot", "zoho", "zendesk", "freshdesk", "jira", "confluence",
        "trello", "asana", "monday", "notion", "slack", "teams", "zoom", "webex",
        "google workspace", "microsoft office", "linux", "windows", "macos", "ios", "android"
    ]
    
    # Convert text to lowercase
    text = text.lower()
    
    # Find skills in text
    found_skills = []
    for skill in common_skills:
        if skill in text:
            found_skills.append(skill)
            
    return found_skills
    
def categorize_company(company_dict):
    """
    Categorize a company based on its industry, size, and other attributes
    
    Args:
        company_dict (dict): Company dictionary from Company.to_dict()
        
    Returns:
        str: Category for the company
    """
    industry = company_dict.get('industry', '').lower()
    size = company_dict.get('company_size', '').lower()
    specialties = company_dict.get('specialties', [])
    
    # Tech categories
    if any(keyword in industry for keyword in ['tech', 'software', 'it', 'computer']):
        if 'startup' in industry or (size and any(s in size for s in ['1-10', '11-50'])):
            return 'tech_startup'
        elif any(s in size for s in ['10,001+', '5,001-10,000']):
            return 'tech_enterprise'
        else:
            return 'tech_mid_market'
            
    # Finance categories
    elif any(keyword in industry for keyword in ['finance', 'banking', 'investment']):
        if 'venture' in industry or any('venture' in s.lower() for s in specialties):
            return 'venture_capital'
        elif any(keyword in industry for keyword in ['insurance']):
            return 'insurance'
        else:
            return 'financial_services'
            
    # Healthcare categories
    elif any(keyword in industry for keyword in ['health', 'medical', 'pharma', 'biotech']):
        if any(keyword in industry for keyword in ['biotech', 'pharmaceutical']):
            return 'biotech_pharma'
        else:
            return 'healthcare'
            
    # Manufacturing categories
    elif any(keyword in industry for keyword in ['manufacturing', 'industrial']):
        return 'manufacturing'
        
    # Retail categories
    elif any(keyword in industry for keyword in ['retail', 'consumer']):
        if 'e-commerce' in industry or any('e-commerce' in s.lower() for s in specialties):
            return 'ecommerce'
        else:
            return 'retail'
            
    # Education categories
    elif any(keyword in industry for keyword in ['education', 'academic', 'school', 'university']):
        return 'education'
        
    # Default category
    else:
        return 'other'
