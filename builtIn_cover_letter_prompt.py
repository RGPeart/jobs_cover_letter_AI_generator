import chromedriver_autoinstaller
from bs4 import BeautifulSoup
import requests
import os 
import yaml
import pyperclip

def load_resume(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def scrape_job_application_data(url):
    try:
        # Make a GET request to fetch the page content
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        
        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract role title and company name
        role_title = soup.find('h1')
        company_name = soup.find('h2')

        role_title = role_title.get_text(strip=True) if role_title else "N/A"
        company_name = company_name.get_text(strip=True) if company_name else "N/A"

        # Locate job description section
        job_card = soup.find('div', class_='container py-lg')
        if not job_card:
            raise ValueError("Job card container not found!")
        
        # Split job and company details
        role_and_company_details = job_card.find_all(lambda tag: tag.name == 'div' and 'col-12' in tag.get('class', []) and 'col-lg-6' in tag.get('class', []))
        if len(role_and_company_details) < 2:
            raise ValueError("Expected job and company details in separate sections.")

        role_card = role_and_company_details[0]
        company_card = role_and_company_details[1]

        # Extract role details        
        role_information = role_card.find_all('div', recursive=False)
        if len(role_information) > 1:
            role_details = role_information[1].find_all('div', recursive=False)
            role_skills = role_information[2]

            role_summary = role_details[0].get_text(strip=True)
            role_description = role_details[2].get_text()

            skills_container = role_skills.find_all('div', recursive=False)[1]
            skills_list = skills_container.find_all('div')
            role_skills = []
            for skill in skills_list:
                role_skills.append(skill.get_text(strip=True))            

        # Extract company details
        company_information = company_card.find_all('div', recursive=False)[4].find('div')

        if(len(company_information) > 1):
            company_whatWeDo = company_information.find_all('p')[0].get_text(strip=True)
            company_whyWorkWithUs = company_information.find_all('p')[1].get_text(strip=True)

        return {
            "Job Title": role_title,
            "Company Name": company_name,
            "Job Summary": role_summary,
            "Job Description": role_description,
            "Job Skills": role_skills,
            "Company Description": company_whatWeDo,
            "Company Why Work With Us": company_whyWorkWithUs
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")



def generate(job_title, company_name, job_summary, job_description, job_skills, company_description, company_whyWorkWithUs):
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

    I am currently applying for the {job_title} position at {company_name}, and I am seeking assistance with writing a compelling and personalized cover letter.

    Please help me by using the following information to create a cover letter in first person written in a tone that expresses professionalism, conciseness, and integrity that is written by a human. Make sure to clearly state the connection between my resume information and the job description and details, as well as the company description.

    Use the following information:

    Company Description: "{company_description}"
    Company Why Work With Us: "{company_whyWorkWithUs}"
    Job Summary: "{job_summary}"
    Job Description: "{job_description}"
    Job Skills: "{job_skills}"

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
    url = input("Please enter a valid BuiltIn.com Job Application URL: ")
    
    # Call the scrape_data function with the user-provided URL
    job_information = scrape_job_application_data(url)
    cover_letter_prompt = generate(job_title= job_information['Job Title'], company_name= job_information['Company Name'], job_summary= job_information['Job Summary'], job_description= job_information['Job Description'], job_skills= job_information['Job Skills'], company_description= job_information['Company Description'], company_whyWorkWithUs= job_information['Company Why Work With Us'])

    # Print the cover letter prompt
    print("Here is your cover letter prompt:")
    print("-----------------------------")
    print(cover_letter_prompt)
    print('\n')

    pyperclip.copy(cover_letter_prompt)
    print("Cover letter prompt copied to clipboard.")

if __name__ == "__main__":
    main()