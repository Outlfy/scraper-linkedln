import os
import sys
import json
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import csv
from datetime import datetime

class LinkedInScraper:
    """
    A LinkedIn scraper that can search for leads using tags and audience categories
    """
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.linkedin.com/',
            'Connection': 'keep-alive'
        }
        self.session.headers.update(self.headers)
        self.leads_database = []
        self.tagged_leads = {}
        self.categorized_companies = {}
        
    def search_people(self, keywords, location=None, industry=None, limit=10, use_real_data=False):
        """
        Search for people on LinkedIn based on keywords and location
        
        Args:
            keywords (str): Keywords to search for
            location (str): Location to filter by
            industry (str): Industry to filter by
            limit (int): Maximum number of results to return
            use_real_data (bool): Whether to use real data or mock data
            
        Returns:
            list: List of people profiles
        """
        print(f"Searching for people with keywords: {keywords}")
        
        if use_real_data:
            # In a real implementation, this would use LinkedIn's API or web scraping
            # For this demo, we'll use a more realistic but still mock dataset
            results = self._search_people_real(keywords, location, industry, limit)
        else:
            # Generate mock search results
            results = []
            for i in range(min(limit, 5)):
                person_id = f"person_{i+1}"
                results.append({
                    "id": person_id,
                    "name": f"Sample Person {i+1}",
                    "headline": f"Professional in {keywords}",
                    "location": location or "Sample Location",
                    "profile_url": f"https://www.linkedin.com/in/{person_id}",
                    "current_company": f"Company {i+1}",
                    "tags": []
                })
                
        # Add to leads database
        self.leads_database.extend(results)
        return results
        
    def _search_people_real(self, keywords, location, industry, limit):
        """
        Search for people using more realistic data
        """
        # Real-world industries and job titles
        industries = [
            "Technology", "Software", "Information Technology", "Financial Services",
            "Marketing", "Advertising", "Healthcare", "Education", "Consulting"
        ]
        
        job_titles = [
            "Software Engineer", "Product Manager", "Data Scientist", "Marketing Manager",
            "Sales Director", "CEO", "CTO", "CFO", "HR Manager", "Operations Manager"
        ]
        
        locations = [
            "New York, NY", "San Francisco, CA", "London, UK", "Berlin, Germany",
            "Toronto, Canada", "Sydney, Australia", "Singapore", "Tokyo, Japan"
        ]
        
        companies = [
            "Google", "Microsoft", "Amazon", "Apple", "Facebook", "Netflix", "IBM",
            "Oracle", "Salesforce", "Adobe", "Intel", "Cisco", "Dell", "HP"
        ]
        
        # Generate realistic profiles
        results = []
        for i in range(min(limit, 10)):
            # Generate a realistic name
            first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
                          "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
            last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
                         "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson"]
            
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            full_name = f"{first_name} {last_name}"
            
            # Create a realistic LinkedIn URL
            url_name = f"{first_name.lower()}-{last_name.lower()}-{random.randint(10000, 99999)}"
            
            # Select job title and company based on keywords if possible
            selected_title = None
            for title in job_titles:
                if keywords.lower() in title.lower():
                    selected_title = title
                    break
            
            if not selected_title:
                selected_title = random.choice(job_titles)
                
            selected_company = random.choice(companies)
            selected_location = location or random.choice(locations)
            selected_industry = industry or random.choice(industries)
            
            # Create profile
            results.append({
                "id": url_name,
                "name": full_name,
                "headline": f"{selected_title} at {selected_company}",
                "location": selected_location,
                "industry": selected_industry,
                "profile_url": f"https://www.linkedin.com/in/{url_name}/",
                "current_company": selected_company,
                "tags": []
            })
            
        return results
        
    def search_companies(self, keywords, industry=None, company_size=None, limit=10, use_real_data=False):
        """
        Search for companies on LinkedIn based on keywords and industry
        
        Args:
            keywords (str): Keywords to search for
            industry (str): Industry to filter by
            company_size (str): Company size to filter by
            limit (int): Maximum number of results to return
            use_real_data (bool): Whether to use real data or mock data
            
        Returns:
            list: List of company profiles
        """
        print(f"Searching for companies with keywords: {keywords}")
        
        if use_real_data:
            # In a real implementation, this would use LinkedIn's API or web scraping
            # For this demo, we'll use a more realistic but still mock dataset
            results = self._search_companies_real(keywords, industry, company_size, limit)
        else:
            # Generate mock search results
            results = []
            industries = ["Technology", "Finance", "Healthcare", "Education", "Retail"]
            sizes = ["1-10", "11-50", "51-200", "201-500", "501-1000", "1001-5000", "5001-10000", "10001+"]
            
            for i in range(min(limit, 5)):
                company_id = f"company_{i+1}"
                selected_industry = industry or random.choice(industries)
                results.append({
                    "id": company_id,
                    "name": f"Sample {selected_industry} Company {i+1}",
                    "industry": selected_industry,
                    "size": random.choice(sizes),
                    "location": "Sample Location",
                    "website": f"https://www.{company_id}.com",
                    "company_url": f"https://www.linkedin.com/company/{company_id}",
                    "category": None
                })
                
        # Categorize companies
        for company in results:
            category = self.categorize_company(company)
            company["category"] = category
            
            # Add to categorized companies
            if category not in self.categorized_companies:
                self.categorized_companies[category] = []
            self.categorized_companies[category].append(company)
            
        # Add to leads database
        self.leads_database.extend(results)
        return results
        
    def _search_companies_real(self, keywords, industry, company_size, limit):
        """
        Search for companies using more realistic data
        """
        # Real-world industries and company types
        industries = [
            "Technology", "Software", "Information Technology", "Financial Services",
            "Marketing", "Advertising", "Healthcare", "Education", "Consulting",
            "E-commerce", "Retail", "Manufacturing", "Telecommunications"
        ]
        
        company_types = [
            "Startup", "Enterprise", "Agency", "Consultancy", "Corporation",
            "Non-profit", "Government", "Educational Institution"
        ]
        
        locations = [
            "New York, NY", "San Francisco, CA", "London, UK", "Berlin, Germany",
            "Toronto, Canada", "Sydney, Australia", "Singapore", "Tokyo, Japan"
        ]
        
        company_prefixes = [
            "Tech", "Global", "Advanced", "Smart", "Digital", "Future", "Next",
            "Innovative", "Strategic", "Dynamic", "Integrated", "Connected"
        ]
        
        company_suffixes = [
            "Solutions", "Systems", "Technologies", "Innovations", "Group",
            "Partners", "Associates", "Enterprises", "Networks", "Labs"
        ]
        
        sizes = ["1-10", "11-50", "51-200", "201-500", "501-1000", "1001-5000", "5001-10000", "10001+"]
        
        # Generate realistic company profiles
        results = []
        for i in range(min(limit, 10)):
            # Generate a realistic company name
            if random.random() < 0.5:
                company_name = f"{random.choice(company_prefixes)}{random.choice(company_suffixes)}"
            else:
                letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                company_name = ''.join(random.choice(letters) for _ in range(random.randint(2, 4)))
                
            # Create a realistic LinkedIn URL
            url_name = f"{company_name.lower().replace(' ', '-')}-{random.randint(10000, 99999)}"
            
            # Select industry based on keywords if possible
            selected_industry = None
            for ind in industries:
                if keywords.lower() in ind.lower():
                    selected_industry = ind
                    break
            
            if not selected_industry:
                selected_industry = industry or random.choice(industries)
                
            selected_size = company_size or random.choice(sizes)
            selected_location = random.choice(locations)
            
            # Create company profile
            results.append({
                "id": url_name,
                "name": company_name,
                "industry": selected_industry,
                "size": selected_size,
                "location": selected_location,
                "website": f"https://www.{url_name.lower()}.com",
                "company_url": f"https://www.linkedin.com/company/{url_name}/",
                "category": None,
                "description": f"A leading provider of {selected_industry.lower()} solutions.",
                "founded": str(random.randint(1990, 2020))
            })
            
        return results
        
    def tag_lead(self, lead, tag):
        """
        Add a tag to a lead
        
        Args:
            lead (dict): Lead to tag
            tag (str): Tag to add
            
        Returns:
            dict: Updated lead
        """
        if "tags" in lead:
            if tag not in lead["tags"]:
                lead["tags"].append(tag)
        else:
            lead["category"] = tag
            
        # Add to tagged leads
        if tag not in self.tagged_leads:
            self.tagged_leads[tag] = []
        
        # Check if lead is already in tagged_leads
        if lead not in self.tagged_leads[tag]:
            self.tagged_leads[tag].append(lead)
            
        return lead
        
    def categorize_company(self, company):
        """
        Categorize a company based on its industry
        
        Args:
            company (dict): Company to categorize
            
        Returns:
            str: Category for the company
        """
        industry = company.get("industry", "").lower()
        
        if "tech" in industry or "software" in industry or "it" in industry:
            return "tech"
        elif "finance" in industry or "banking" in industry:
            return "finance"
        elif "health" in industry or "medical" in industry:
            return "healthcare"
        elif "education" in industry or "school" in industry:
            return "education"
        elif "retail" in industry or "consumer" in industry or "e-commerce" in industry:
            return "retail"
        elif "marketing" in industry or "advertising" in industry:
            return "marketing"
        elif "consulting" in industry or "professional services" in industry:
            return "consulting"
        else:
            return "other"
            
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
            
    def filter_by_tags(self, leads, tags):
        """
        Filter leads by tags
        
        Args:
            leads (list): List of leads to filter
            tags (list): List of tags to filter by
            
        Returns:
            list: Filtered list of leads
        """
        filtered_leads = []
        
        for lead in leads:
            if "tags" in lead:
                # For people
                if any(tag in lead["tags"] for tag in tags):
                    filtered_leads.append(lead)
            elif "category" in lead:
                # For companies
                if lead["category"] in tags:
                    filtered_leads.append(lead)
                    
        return filtered_leads
        
    def save_leads(self, leads, filename, format='json'):
        """
        Save leads to a file
        
        Args:
            leads (list): List of leads to save
            filename (str): Name of the file to save leads to
            format (str): File format ('json' or 'csv')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if format.lower() == 'json':
                with open(filename, 'w') as f:
                    json.dump(leads, f, indent=2)
            elif format.lower() == 'csv':
                if not leads:
                    print("No leads to save.")
                    return False
                    
                # Get headers from first lead
                headers = leads[0].keys()
                
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(leads)
            else:
                print(f"Unsupported format: {format}")
                return False
                
            print(f"Saved {len(leads)} leads to {filename}")
            return True
        except Exception as e:
            print(f"Error saving leads: {e}")
            return False
            
    def load_leads(self, filename, format='json'):
        """
        Load leads from a file
        
        Args:
            filename (str): Name of the file to load leads from
            format (str): File format ('json' or 'csv')
            
        Returns:
            list: List of leads
        """
        try:
            if format.lower() == 'json':
                with open(filename, 'r') as f:
                    leads = json.load(f)
            elif format.lower() == 'csv':
                leads = []
                with open(filename, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        leads.append(row)
            else:
                print(f"Unsupported format: {format}")
                return []
                
            print(f"Loaded {len(leads)} leads from {filename}")
            
            # Add leads to database
            self.leads_database.extend(leads)
            
            # Categorize companies and tag leads
            for lead in leads:
                if "category" in lead:
                    category = lead["category"]
                    if category not in self.categorized_companies:
                        self.categorized_companies[category] = []
                    self.categorized_companies[category].append(lead)
                if "tags" in lead and lead["tags"]:
                    for tag in lead["tags"]:
                        if tag not in self.tagged_leads:
                            self.tagged_leads[tag] = []
                        self.tagged_leads[tag].append(lead)
                        
            return leads
        except Exception as e:
            print(f"Error loading leads: {e}")
            return []
            
    def export_leads_report(self, leads, filename):
        """
        Export a detailed report of leads
        
        Args:
            leads (list): List of leads to export
            filename (str): Name of the file to export to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filename, 'w') as f:
                f.write(f"LinkedIn Leads Report\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Count by type
                people_count = sum(1 for lead in leads if "tags" in lead)
                company_count = sum(1 for lead in leads if "category" in lead)
                
                f.write(f"Total Leads: {len(leads)}\n")
                f.write(f"People: {people_count}\n")
                f.write(f"Companies: {company_count}\n\n")
                
                # People leads
                if people_count > 0:
                    f.write("=== People Leads ===\n\n")
                    for lead in leads:
                        if "tags" in lead:
                            f.write(f"Name: {lead.get('name', 'Unknown')}\n")
                            f.write(f"Headline: {lead.get('headline', 'Unknown')}\n")
                            f.write(f"Company: {lead.get('current_company', 'Unknown')}\n")
                            f.write(f"Location: {lead.get('location', 'Unknown')}\n")
                            f.write(f"Profile URL: {lead.get('profile_url', 'Unknown')}\n")
                            f.write(f"Tags: {', '.join(lead.get('tags', []))}\n\n")
                
                # Company leads
                if company_count > 0:
                    f.write("=== Company Leads ===\n\n")
                    for lead in leads:
                        if "category" in lead:
                            f.write(f"Name: {lead.get('name', 'Unknown')}\n")
                            f.write(f"Industry: {lead.get('industry', 'Unknown')}\n")
                            f.write(f"Size: {lead.get('size', 'Unknown')}\n")
                            f.write(f"Location: {lead.get('location', 'Unknown')}\n")
                            f.write(f"Website: {lead.get('website', 'Unknown')}\n")
                            f.write(f"LinkedIn URL: {lead.get('company_url', 'Unknown')}\n")
                            f.write(f"Category: {lead.get('category', 'Unknown')}\n\n")
                
                f.write("=== End of Report ===\n")
                
            print(f"Exported leads report to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting leads report: {e}")
            return False

    def get_company_posts(self, company_name):
        """
        Get company posts from LinkedIn
        """
        url = f"https://www.linkedin.com/company/{company_name}/posts/?feedView=all"
        response = self.session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        posts = []
        for post in soup.find_all('li', {'class': 'occludable-update'}):
            post_data = {
                'title': post.find('h3', {'class': 'feed-item-title'}).text.strip(),
                'text': post.find('div', {'class': 'feed-item-description'}).text.strip(),
                'comments': post.find('span', {'class': 'comments-count'}).text.strip(),
                'likes': post.find('span', {'class': 'likes-count'}).text.strip()
            }
            posts.append(post_data)
        
        return posts

# Example usage
if __name__ == "__main__":
    # Create a LinkedIn scraper
    scraper = LinkedInScraper()
    
    # Search for people with real-looking data
    print("\n=== Searching for Marketing Professionals ===")
    marketing_people = scraper.search_people("marketing", location="New York", use_real_data=True)
    print(f"Found {len(marketing_people)} marketing professionals")
    
    # Search for companies with real-looking data
    print("\n=== Searching for Tech Companies ===")
    tech_companies = scraper.search_companies("software", industry="Technology", use_real_data=True)
    print(f"Found {len(tech_companies)} tech companies")
    
    # Tag leads
    print("\n=== Tagging Leads ===")
    for person in marketing_people:
        if "manager" in person["headline"].lower():
            scraper.tag_lead(person, "decision_maker")
        if "director" in person["headline"].lower() or "ceo" in person["headline"].lower():
            scraper.tag_lead(person, "executive")
        if "marketing" in person["headline"].lower():
            scraper.tag_lead(person, "marketing_professional")
    
    # Get leads by tags
    print("\n=== Getting Leads by Tags ===")
    decision_makers = scraper.get_leads_by_tag("decision_maker")
    executives = scraper.get_leads_by_tag("executive")
    print(f"Found {len(decision_makers)} decision makers")
    print(f"Found {len(executives)} executives")
    
    # Get leads by categories
    print("\n=== Getting Leads by Categories ===")
    tech_leads = scraper.get_leads_by_category("tech")
    finance_leads = scraper.get_leads_by_category("finance")
    print(f"Found {len(tech_leads)} tech companies")
    print(f"Found {len(finance_leads)} finance companies")
    
    # Save leads to files
    print("\n=== Saving Leads ===")
    all_leads = marketing_people + tech_companies
    scraper.save_leads(all_leads, "all_leads.json")
    scraper.save_leads(decision_makers, "decision_makers.csv", format="csv")
    
    # Export leads report
    print("\n=== Exporting Leads Report ===")
    scraper.export_leads_report(all_leads, "leads_report.txt")
    
    # Print sample lead
    print("\n=== Sample Lead ===")
    if marketing_people:
        print(json.dumps(marketing_people[0], indent=2))
    
    print("\nLinkedIn scraper demo completed successfully!")