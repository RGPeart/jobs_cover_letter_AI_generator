import chromedriver_autoinstaller
from selenium import webdriver
from bs4 import BeautifulSoup
import os 
import yaml

chromedriver_autoinstaller.install()

def load_resume(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def scrape_job_application_data(url):
    role_title = ""
    company_name = ""
    company_description = ""
    role_requirements_list = []
    role_details_list = []

    # Make a GET request to the URL
    driver = webdriver.Chrome()
    driver.get(url)
    html = driver.page_source
    
    # Create a BeautifulSoup object with the response content
    soup = BeautifulSoup(html, 'html.parser')
    job_and_company = soup.find('h2', attrs={'data-testid': 'job-title'}).text.split(',')
    role_title = job_and_company[0].strip()
    company_name = job_and_company[1].strip()

    job_card = soup.find_all('div', attrs={'class': 'sc-eIWua-D glFjkJ'})

    job_details = job_card[0].find_all('div', attrs={'class': 'sc-gJFNMl izfOyw'})
    role_requirements = job_details[0]
    role_details = job_details[-1]
    role_requirements_list = []
    role_details_list = []

    for requirement in role_requirements.find_all('li'):
        role_requirements_list.append(requirement.text)

    for details in role_details.find_all('li'):
        role_details_list.append(details.text)
        
    company_description = job_card[1].find_all('div', attrs={'class': 'sc-gJFNMl izfOyw'})[4].text

    driver.quit()
    return role_title, company_name, company_description, role_requirements_list, role_details_list



def generate(role_title, company_name, company_description, role_requirements_list, role_details_list):
    resume_info = load_resume('./data_folder/plain_text_resume.yaml')

    name = resume_info.get('name', 'Ryan')
    surname = resume_info.get('surname', 'Peart')

    job_experience = resume_info.get('experienceDetails', [])
    current_job_experience_position = job_experience[0]['position']
    current_job_experience_company = job_experience[0]['company']
    current_job_expeience_responsibilities = job_experience[0]['keyResponsibilities']
    current_job_experience_skills = job_experience[0]['skillsAcquired']
    #education = resume_info.get('educationDetails', [])
    projects = resume_info.get('projects', [])
    certifications = resume_info.get('certifications', [])
    interests = resume_info.get('interests', [])
    
    prompt = f"""
    Ignore all previous cover letter responses.

    I am currently applying for the {role_title} position at {company_name}, and I am seeking assistance with writing a compelling and personalized cover letter.

    Please help me by using the following information to create a cover letter in first person written in a tone that expresses professionalism, conciseness, and integrity that is written by a human. Make sure to clearly state the connection between my resume information and the job description and details, as well as the company description.

    Use the following information:

    Company Description: {company_description}
    Job Requirements: {role_requirements_list}
    Job Details: {role_details_list}

    My Full Name: {name} {surname}
    My Current Job Position: {current_job_experience_position}
    My Current Job Company: {current_job_experience_company}
    My Job Key Responsibilities: {current_job_expeience_responsibilities}
    My Job Skills Acquired: {list(current_job_experience_skills.keys())}
    My Personal Projects: {projects}
    My Certifications: {certifications}
    My Interests: {interests}

    Additional instructions: The cover letter should be no more than 5 paragraphs, and between 350 to 400 words.

    Thank you for your help in creating a cover letter. I appreciate your time and effort.
    """

    return prompt

def main():
    # Prompt the user for a URL
    url = input("Please enter a valid Job Application URL: ")
    
    # Call the scrape_data function with the user-provided URL
    role_title, company_name, company_description, role_requirements_list, role_details_list = scrape_job_application_data(url)
    cover_letter_prompt = generate(role_title, company_name, company_description, role_requirements_list, role_details_list)

    # Print the cover letter prompt
    print("Here is your cover letter prompt:")
    print("-----------------------------")
    print(cover_letter_prompt)

if __name__ == "__main__":
    main()