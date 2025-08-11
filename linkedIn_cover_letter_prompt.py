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
        job_id = url.split('/')[5]
        linkedIn_api_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}/"
        
        # Make a GET request to fetch the page content
        response = requests.get(linkedIn_api_url)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        
        # Parse the page content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract role title and company name
        role_title = soup.find('h2')
        company_name = soup.find('a', class_="topcard__org-name-link")

        role_title = role_title.get_text(strip=True) if role_title else "N/A"
        company_url = company_name.get('href').split("?")[0]
        company_name = company_name.get_text(strip=True) if company_name else "N/A"

        # Locate job description section
        job_description = soup.find('div', class_='description__text')
        if not job_description:
            raise ValueError("Job card container not found!")
        
        # Extract role details        
        role_information = job_description.find('div').get_text(strip=True)

        '''        
        # Get Company Information
        response = requests.get(company_url)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract company details
        company_information = company_card.find_all('div', recursive=False)[4].find('div').find_all('p', recursive=False)

        if(len(company_information) > 1):
            company_whatWeDo = company_information[0].get_text(strip=True)
        else:
            company_whatWeDo = "Company Information not provided."
        '''

        return {
            "Job Title": role_title,
            "Company Name": company_name,
            "Job Description": role_information,
            #"Company Description": company_whatWeDo,
            #"Company Why Work With Us": company_whyWorkWithUs
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")



def generate(job_title, company_name, job_description):
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

    First, please perform some research and analysis on {company_name}. From your research, generate a brief summary of {company_name}'s company bio, culture, and why I should work for them.

    Second, please read through the job description and respond with a summary of the job description, job requirements, and technical/non-technical skills required.
        
    Third, please help me by using the following information to create a cover letter in first person written in a tone that expresses professionalism, conciseness, and integrity that is written by a human. Make sure to clearly state the connection between my resume information and the job description, job skills, as well as the company's culture and values.

    Use the following information:

    Company Description: the company description summary you generate from your research
    Company Why Work With Us: the company culture summary you generate from your research
    Job Description: {job_description}
    Job Skills: the job requirements and skills you generate from your research

    My Full Name: "{name} {surname}":
    My Current Job Position: "{current_job_experience_position}"
    My Current Job Company: "{current_job_experience_company}"
    My Job Key Responsibilities: "{current_job_expeience_responsibilities}"
    My Job Skills Acquired: "{list(current_job_experience_skills.keys())}"
    My Personal Projects: "{projects}"
    My Certifications: "{certifications}"
    My Interests: "{interests}"

    Additional instructions: The cover letter should be no more than 5 paragraphs, and between 375 to 425 words. Please do not use any Em Dashes. 

    Thank you for your help in creating a cover letter. I appreciate your time and effort.
    """

    return prompt

def main():
    # Prompt the user for a URL
    url = input("Please enter a valid LinkedIn.com Job Application URL: ")

    # Validate the URL format
    if not url.startswith("https://www.linkedin.com/jobs/"):
        print("Invalid LinkedIn.com URL format. Please make sure you are on the LinkedIn job's individual page.")
        return
    
    # Call the scrape_data function with the user-provided URL
    job_information = scrape_job_application_data(url)
    cover_letter_prompt = generate(job_title= job_information['Job Title'], company_name= job_information['Company Name'], job_description= job_information['Job Description'])

    # Print the cover letter prompt
    print("Here is your cover letter prompt:")
    print("-----------------------------")
    print(cover_letter_prompt)
    print('\n')

    pyperclip.copy(cover_letter_prompt)
    print("Cover letter prompt copied to clipboard.")

if __name__ == "__main__":
    main()