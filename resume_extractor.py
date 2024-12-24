from datetime import datetime
import os
import re
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import spacy
# nlp = spacy.load("en_core_web_sm")

class ResumeExtractor:

    @staticmethod
    def preprocess_text(text):
        return text.lower()
    
    @staticmethod
    def extract_skills(text, skill_set):
        return [skill for skill in skill_set if skill.lower() in text.lower()]
    
    @staticmethod
    def extract_name(text):
        lines = text.split("\n")
        potential_name_lines = lines[:10]
        for line in potential_name_lines:
            line = line.strip()
            if line.replace(" ", "").isalpha() and len(line.split()) in [2, 3] and "resume" not in line.lower():
                return line
        return "Name not found"
   
    @staticmethod
    def extract_mobile_number(text):
        phone_pattern = re.compile(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        phone_matches = phone_pattern.findall(text)
        return [re.sub(r'[^0-9+]', '', match) for match in phone_matches] or ["Phone number not found"]
    
    @staticmethod
    def extract_email(text):
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        email_matches = email_pattern.findall(text)
        return email_matches[0] if email_matches else "Email not found"
    
    # @staticmethod
    # def extract_experience(text):
    #     def convert_word_to_number(word):
    #         word_to_number = {
    #             "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    #             "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    #             "eleven": 11, "twelve": 12
    #         }
    #         return word_to_number.get(word.lower(), 0)
        
    #     # Exclude education-related sections
    #     education_keywords = ["education", "degree", "bachelor", "master", "phd", "university", "college", "school"]
    #     education_pattern = re.compile(r'(education|bachelor|master|phd|university|college|school)', re.IGNORECASE)
    #     text_sections = re.split(r'\n+', text)
    #     filtered_text = "\n".join(
    #         section for section in text_sections if not education_pattern.search(section)
    #     )

    #     total_experience_months = 0
    #     seen_date_ranges = set()

    #     # Handle date range patterns
    #     date_pattern = re.compile(r'(\w+\s+\d{4}|\d{1,2}/\d{4})\s*[—-]\s*(\w+\s+\d{4}|\d{1,2}/\d{4})', re.IGNORECASE)
    #     date_matches = date_pattern.findall(filtered_text)
    #     for start, end in date_matches:
    #         if (start, end) in seen_date_ranges:
    #             continue
    #         seen_date_ranges.add((start, end))
    #         try:
    #             if '/' in start:
    #                 start_date = datetime.strptime(start.strip(), '%m/%Y')
    #                 end_date = datetime.strptime(end.strip(), '%m/%Y')
    #             else:
    #                 start_date = datetime.strptime(start.strip(), '%B %Y')
    #                 end_date = datetime.strptime(end.strip(), '%B %Y')
    #             months_difference = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    #             total_experience_months += months_difference
    #         except ValueError:
    #             continue

    #     # Handle textual patterns for years and months
    #     year_month_pattern = re.findall(r'(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s*(years?|yrs?|months?|mos?)', filtered_text, re.IGNORECASE)
    #     for value, unit in year_month_pattern:
    #         if value.isdigit():
    #             value = int(value)
    #         else:
    #             value = convert_word_to_number(value)
    #         if 'month' in unit.lower() or 'mos' in unit.lower():
    #             total_experience_months += value
    #         elif 'year' in unit.lower() or 'yr' in unit.lower():
    #             total_experience_months += value * 12

    #     # Convert months to years and months
    #     total_experience_months = max(total_experience_months, 0)
    #     years = total_experience_months // 12
    #     months = total_experience_months % 12

    #     if total_experience_months == 0:
    #         return "Fresher"
        
    #     return {"years": years, "months": months}

    @staticmethod
    def calculate_total_experience(experiences):
        """
        Calculates the total experience in years and months based on the dates.

        Args:
            experiences (list[dict]): List of experience entries.

        Returns:
            str: Total experience in the format 'X years Y months'.
        """
        total_months = 0
        for exp in experiences:
            if 'dates' in exp and exp['dates']:
                print(exp['dates'])
                start_date, end_date = ResumeExtractor.parse_dates(exp['dates'])
                print('start_date',start_date,'end_date',end_date)
                if start_date and end_date:
                    total_months += (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

        years, months = divmod(total_months, 12)
        return {"years":years,"months": months}

    @staticmethod
    def parse_dates(date_range):
        """
        Parses start and end dates from a date range string.

        Args:
            date_range (str): Date range in formats like 'Month Year — Month Year', 'Year - Year', or 'Year - Present'.

        Returns:
            tuple: Start and end dates as datetime objects.
        """
        try:
            if '—' in date_range or '-' in date_range or "–" in date_range:
                if '—' in date_range:
                    separator = '—'
                elif "–" in date_range:
                    separator = "–"
                else:
                    separator = '-'

                start_date, end_date = date_range.split(separator)

                start_date = ResumeExtractor.parse_date_string(start_date.strip())
                if "Present" in end_date.strip() or "Current" in end_date.strip() or "current" in end_date.strip():
                    end_date = datetime.now()
                else:
                    end_date = ResumeExtractor.parse_date_string(end_date.strip())
                return start_date, end_date
        except ValueError:
            return None, None

    @staticmethod
    def parse_date_string(date_string):
        """
        Parses a date string into a datetime object.

        Args:
            date_string (str): A date string like 'January 2022' or '2022'.

        Returns:
            datetime: A datetime object representing the parsed date.
        """
        try:
            if any(month in date_string for month in [
                "January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"]):
                return datetime.strptime(date_string, "%B %Y")
            elif any(month in date_string for month in ["Jan","Feb","Apr","Aug","Sep","Oct","Nov","Dec"]):
                return datetime.strptime(date_string, "%b %Y")
            else:
                return datetime.strptime(date_string, "%Y")
        except ValueError:
            return None


    @staticmethod
    def extract_experience(experience_text):
        """
        Extracts job experience details from the provided text, handling diverse formats.

        Args:
            experience_text (str): The raw text containing job experiences.

        Returns:
            list[dict]: A list of dictionaries containing structured experience details.
        """
        experiences = []

        # Regular expression patterns
#         job_title_pattern = re.compile(
#     r"(?:\b(?:Python|Full Stack|Frontend|Backend|Software|Data|Machine Learning|AI|Cloud|System|DevOps|Network|Embedded)\b\s*)?"  # Optional prefix like 'Python' or 'Full Stack'
#     r"(Developer|Engineer|Internship|Consultant|Architect|Specialist|Manager)",  # Match the main job title
#     re.IGNORECASE
# )
        job_title_pattern = re.compile(
    r"(?:\b(?:Senior|Junior|Lead|Associate|Freelance|Temporary|Full-time|Part-time|Remote|Intern)\b\s*)?"  # Optional prefix like 'Senior' or 'Intern'
    r"([A-Za-z]+(?:\s[A-Za-z]+)*\s*)"  # Match the main job title (handles multi-word titles)
    r"(Developer|Engineer|Consultant|Manager|Specialist|Coordinator|Analyst|Administrator|Assistant|Supervisor|Plumber|Teacher|Clerk|Designer|Director|Architect|Supervisor|Operator|Representative|Sales|Chef|Nurse|Driver|Technician|Leader|Assistant|Worker|Custodian|Support|Planner|Trainer|Writer|Accountant|Scientist|Creator|Artist|Consultant|Technologist|Developer|Support|Coordinator)",  # Common job roles
    re.IGNORECASE
)
        company_pattern = re.compile(
    r"(?i)(?<=\bCompany:\s)([^\n]+)",  # Match text following 'Company:' until the end of the line
    re.IGNORECASE
)
#         date_pattern = re.compile(r"""
#     \b(                             # Begin capturing group for the entire date range
#         (                           # First option: Full month and year range
#             (January|February|March|April|May|June|July|August|September|October|November|December)
#             \s+\d{4}\s*[-—]\s*      # Month-Year followed by a separator (- or —)
#             (Present|Current|\w+\s+\d{4})  # Match "Present", "Current", or another Month-Year
#         )
#         |                           # OR
#         (\d{4}\s*[-—]\s*(Present|Current|\d{4})) # Second option: Year-only range
#         |
#         (?:[A-Za-z]+ \d{4})\s*[-–—]\s*(?:[A-Za-z]+ \d{4})
                                  
#     )
#     \b                              # Word boundary to prevent partial matches
# """, re.IGNORECASE | re.VERBOSE)

        date_pattern = re.compile(r"""
    \b(                                     # Begin capturing group for the entire date range
        (                                   # First option: Full month and year range
            (January|February|March|April|May|June|July|August|September|October|November|December|
            Jan|Feb|Mar|Apr|Aug|Sep|Oct|Nov|Dec)  # Match the full month names
            \s+\d{4}\s*[-—]\s*              # Match month-year followed by a separator (- or —)
            (Present|Current|Summer|\w+\s+\d{4})    # Match "Present", "Current", or another Month-Year
        )
        |                                   # OR
        (\d{4}\s*[-—]\s*(Present|Current|Summer|\d{4}))  # Year-only range (e.g., 2012 – Present, 2020 – 2023)
        |                                   # OR
        ([A-Za-z]+ \d{4})\s*[-–—]\s*([A-Za-z]+ \d{4})  # Month-Year range (e.g., "August 2019 – June 2020")
        |
        ([A-Za-z]+\s*\d{4})\s*[-–—]\s*(\d{4}|\w+\s*\d{4})
    )
    \b                                      # Word boundary to prevent partial matches
""", re.IGNORECASE | re.VERBOSE)

        responsibility_pattern = re.compile(r"(?:•\s*)(.*)")

        current_experience = {}
        responsibilities_buffer = []
        if experience_text.get('experience') is not None:
            for line in experience_text['experience'].splitlines():
                print("line=====>",line)
                line = line.strip()

                # Match job title
                job_title_match = job_title_pattern.match(line)
                print("job_title_match===>",job_title_match)

                #-need this
                if job_title_match:
                    if current_experience:  
                        current_experience["responsibilities"] = responsibilities_buffer
                        experiences.append(current_experience)
                        responsibilities_buffer = []
                    current_experience = {"job_title": job_title_match.group(), "company": None, "dates": None, "responsibilities": []}
                    continue

                #-need this


                # Match company name
                company_match = company_pattern.search(line)
                print("company_match===>",company_match)

                if company_match and current_experience:
                    current_experience["company"] = company_match.group().strip()
                    continue

                # Match dates

                date_match = date_pattern.search(line)
                print("date_match===>",date_match,current_experience)
                if date_match:
                    if current_experience.get('job_title') is not None:
                        current_experience["dates"] = date_match.group(0)
                    else:
                        experiences.append({"dates":date_match.group(0)})
                    continue

                # Match responsibilities
                # responsibility_match = responsibility_pattern.match(line)
                # if responsibility_match:
                #     responsibilities_buffer.append(responsibility_match.group(1))

            # Save the last experience entry
            if current_experience:
                current_experience["responsibilities"] = responsibilities_buffer
                experiences.append(current_experience)

            # Calculate total experience
            total_experience = ResumeExtractor.calculate_total_experience(experiences)
            experiences.append({'total_experiences': total_experience})
            print("experiences=======>",experiences)

        return experiences

    
    @staticmethod
    def extract_details(resume_text, skill_set):
        skills = ResumeExtractor.extract_skills(resume_text, skill_set)
        name = ResumeExtractor.extract_name(resume_text)
        mobile_number = ResumeExtractor.extract_mobile_number(resume_text)
        email = ResumeExtractor.extract_email(resume_text)
        return {"Name": name, "Mobile": mobile_number, "Email": email, "Skills": skills}
    



    # @staticmethod
    # def split_into_sections(text):
    #     sections = {}
    #     section_pattern = re.compile(
    #         r"(education|experience|certifications?|skills|projects|achievements|courses?|awards?|summary|objective|work history)",
    #         re.IGNORECASE
    #     )
    #     current_section = None
    #     for line in text.splitlines():
    #         line = line.strip()
    #         if not line:
    #             continue
    #         match = section_pattern.match(line)
    #         if match:
    #             current_section = match.group(1).lower()
    #             sections[current_section] = []
    #         elif current_section:
    #             sections[current_section].append(line)
    #     return {k: "\n".join(v) for k, v in sections.items()}

    @staticmethod
    def split_into_sections(text):
        """
        Splits the given text into sections based on common resume headings.

        Args:
            text (str): The input text containing the resume content.

        Returns:
            dict: A dictionary with section names as keys and corresponding text as values.
        """
        section_aliases = {
            "education": "education",
            "experience": "experience",
            "work history": "experience",
            "work experience": "experience",
            "Employment History" : "experience",
            "employment history" : "experience",
            "professional experience": "experience",
            "certifications": "certifications",
            "certification": "certifications",
            "skills": "skills",
            "projects": "projects",
            "achievements": "achievements",
            "courses": "courses",
            "course": "courses",
            "awards": "awards",
            "summary": "summary",
            "objective": "objective"
        }

        section_pattern = re.compile(
            r"^(education|experience|work history|work experience|"
            r"professional experience|certifications|Employment History?|skills|projects|"
            r"achievements|courses?|awards?|summary|objective)$",
            re.IGNORECASE
        )

        sections = {}
        current_section = None
        buffer = []

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            
            match = section_pattern.match(line)
            if match:
                if current_section and buffer:
                    sections[current_section] = "\n".join(buffer).strip()
                
                current_section = section_aliases.get(match.group(1).lower(), match.group(1).lower())
                buffer = []
            elif current_section:
                buffer.append(line)
        
        if current_section and buffer:
            sections[current_section] = "\n".join(buffer).strip()


        print("section------------------------------------------")
        print("Sections====>",sections)

        print("section------------------------------------------")

        
        return sections
    
    @staticmethod
    def extract_certifications(sections):
        if "certifications" in sections or "courses" in sections:
            if sections.get("certifications"):
                return sections["certifications"]
            if sections.get("courses"):
                return sections["courses"]
        return "No certifications found"
    
    # @staticmethod
    # def extract_education(sections):
    #     if "education" in sections :
    #         return sections["education"]
    #     return "No education details found"

    @staticmethod
    def extract_education(education_text):
        """
        Extracts education details in a structured format.

        Args:
            education_text (str): The text under the 'education' section.

        Returns:
            list[dict]: A list of dictionaries containing education details.
        """
        education_details = []
        lines = education_text['education'].splitlines()
        education_entry_pattern = re.compile(
            r"^(.*?),?\s*(Bachelor|Master|Ph\.D|Diploma|Associate).*?in\s(.*?)(?:\s|$)",
            re.IGNORECASE
        )
        
        for line in lines:
            match = education_entry_pattern.match(line)
            if match:
                university = match.group(1).strip()
                degree = match.group(2).strip()
                specialization = match.group(3).strip()
                education_details.append({
                    "university": university,
                    "degree": degree,
                    "specialization": specialization,
                })
            else:
                education_details.append({"raw_entry": line.strip()})
        # print(education_details,"education_details")

        structured_education = []
        current_entry = {}

        degree_keywords = re.compile(r"(bachelor|master|ph\.d|diploma|associate|engineer|doctor|graduate|degree)", re.IGNORECASE)
        duration_pattern = re.compile(r"(\b\d{4}\b.*?—.*?\b\d{4}\b|\b\d{4}\b.*?present)", re.IGNORECASE)
        grade_pattern = re.compile(r"(cgpa|gpa|grade|percentage|marks?:?)\s*(\d+(\.\d+)?/(\d+(\.\d+)?))?", re.IGNORECASE)
        
        for item in education_details:
            text = item.get('raw_entry', '').strip()

            # Match patterns for specific fields
            if "linkedin" in text.lower() or "portfolio" in text.lower():
                # Skip irrelevant entries
                continue
            elif "college" in text.lower() or "university" in text.lower():
                if current_entry:  # Save the previous entry if it exists
                    structured_education.append(current_entry)
                current_entry = {"university": text}
            elif degree_keywords.search(text):
                current_entry["degree"] = text
            elif duration_pattern.search(text):
                current_entry["duration"] = duration_pattern.search(text).group()
            elif grade_pattern.search(text):
                grade_match = grade_pattern.search(text)
                current_entry["grade"] = grade_match.group().strip()
            else:
                # Add as additional information if not matching any pattern
                current_entry.setdefault("additional_info", []).append(text)
        
        # Append the last entry if present
        if current_entry:
            structured_education.append(current_entry)

        return structured_education

    @staticmethod
    def extract_projects(projects_text):
        """
        Extracts structured projects from the given text.

        Args:
            projects_text (str): The raw text from the 'projects' section.

        Returns:
            list[dict]: A list of structured projects with title, duration, technologies, and description.
        """
        projects = []
        project_pattern = re.compile(r"^\d+\.\s*(.*?)\s+\|")  # Matches project title (e.g., "1. Project Name | ...")
        tech_pattern = re.compile(r"\| (.*?)\.")  # Matches technologies (e.g., "| Python, Flask ...")
        duration_pattern = re.compile(r"(\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b)")  # Matches durations (e.g., "April 2023")
        
        current_project = {}
        buffer = []
        if projects_text.get('projects') is not None:
            for line in projects_text['projects'].splitlines():
                line = line.strip()
                if not line:
                    continue
                
                # Check for project title
                title_match = project_pattern.search(line)
                if title_match:
                    if current_project:  # Save the previous project
                        if buffer:
                            current_project['description'] = " ".join(buffer).strip()
                        projects.append(current_project)
                        current_project = {}
                        buffer = []

                    current_project['title'] = title_match.group(1).strip()
                    tech_match = tech_pattern.search(line)
                    if tech_match:
                        current_project['technologies'] = tech_match.group(1).strip()

                    duration_match = duration_pattern.search(line)
                    if duration_match:
                        current_project['duration'] = duration_match.group().strip()

                else:
                    buffer.append(line)

            # Save the last project
            if current_project:
                if buffer:
                    current_project['description'] = " ".join(buffer).strip()
                projects.append(current_project)

        return projects

    @staticmethod
    def extract_achievements(achievements_text):
        """
        Extracts structured achievements from the given text.

        Args:
            achievements_text (str): The raw text from the 'achievements' section.

        Returns:
            list[dict]: A list of structured achievements with title, date, and description.
        """
        achievements = []
    
        # Pattern to match achievements like "Rank", "Award", "Score", etc.
        achievement_pattern = re.compile(r"^(?:•\s*)?(.*?)(?:\s*(?:Rank|Award|Place|Score|Certification|Recognized|Won|Achieved|Top|Best|Named))?[\s]*([\d/]+)?(?:\s*(?:in|at|with))?\s*(.*)?$", re.IGNORECASE)
        
        # Match date patterns like "August 2023"
        date_pattern = re.compile(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b")
        
        current_achievement = {}
        buffer = []

        # Loop through each line of the achievements section
        if achievements_text.get('achievements') is not None:
            for line in achievements_text['achievements'].splitlines():
                line = line.strip()
                if not line:
                    continue
                
                # Match achievement patterns like rank, score, and award
                match = achievement_pattern.match(line)
                if match:
                    # Start a new achievement
                    title = match.group(1).strip()
                    rank_score = match.group(2) if match.group(2) else ''
                    details = match.group(3) if match.group(3) else ''
                    
                    # Check for a date (if present)
                    date_match = date_pattern.search(line)
                    date = date_match.group() if date_match else None
                    
                    current_achievement = {
                        "title": title,
                        "rank_score": rank_score,
                        "details": details,
                        "date": date
                    }
                    
                    # Add to achievements list
                    achievements.append(current_achievement)
                
                else:
                    # If line doesn't match, consider it a continuation of the current achievement
                    buffer.append(line)
        
        return achievements

    @staticmethod
    def extract_summary(sections):
        return sections.get("summary", "No summary found")
    
    @staticmethod
    def extract_location(text):
        """
        Extract the location from the resume text.
        
        :param text: Resume text to extract the location from.
        :return: Extracted location or 'Location not found'.
        """
        # Regex pattern for common location formats like "City, State" or "City, Country"
        location_patterns = [
            r'\b([A-Za-z]+(?: [A-Za-z]+)*)[,\s]+([A-Za-z]+(?: [A-Za-z]+)*)\b',  # City, State or City, Country
            r'\b([A-Za-z]+(?: [A-Za-z]+)*)\s*-\s*(?:[A-Za-z]+(?: [A-Za-z]+)*)\b',  # City - State or City - Country
            r'\b([A-Za-z]+(?: [A-Za-z]+)*)\b'  # Just the city or country
        ]
        
        # Try to match one of the patterns
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                location = match.group(0).strip()
                return location
        
        return "Location not found"
    
    @staticmethod
    def extract_core_location(location):
        """Extract core location (e.g., remove city qualifiers like 'India')"""
        cleaned_location = re.sub(r'[^a-zA-Z\s]', '', location)
        core_location = cleaned_location.strip().split()[0]
        return core_location.lower()
    
    @staticmethod
    def calculate_resume_score(resume_details, matched_skills, skill_set, experience_range_dict):
        
        # Resume Skills Score = 100 per skills

        #--------------------Skills Scores----------------#
        max_skill_score = 100

        skill_point = max_skill_score/len(skill_set)
        proportion_matched = len(matched_skills)  
        skill_score = skill_point*proportion_matched

        #--------------------Skills Scores----------------#

        

        # Resume Experience Score = 100 per 

        #--------------------Experience Scores----------------#
        
        max_experience_score = 100

        exp_point = max_experience_score/(int(experience_range_dict['max'])-int(experience_range_dict['min'])) 
        if resume_details['Experience_cal'] == "Fresher":
            resume_year = 0
        else:
           resume_year = resume_details['Experience_cal']['years']

        experience_score = exp_point*resume_year
        if experience_score > max_experience_score:
            experience_score = max_experience_score
    


        #--------------------Experience Scores----------------#
        

        # max_location_score = 10
        # preferred_location = 'mumbai'
        # resume_location = resume_details['Location']
        # preferred_location = preferred_location.strip()

        # resume_core_location = ResumeExtractor.extract_core_location(resume_location)
        # preferred_core_location = ResumeExtractor.extract_core_location(preferred_location)



        # location_score = 0
        # if resume_core_location == preferred_core_location:
        #     location_score = 10  
        
        total_score = (skill_score + experience_score )/(max_skill_score+max_experience_score)*100
        # print("skill_score : ",skill_score, "experience_score :", experience_score)
        # print("total score--->",total_score)
        
        return total_score
    

    # @staticmethod
    # def calculate_job_score(resume_text, job_description):
    #     # Combine resume and job description into a single corpus
    #     corpus = [resume_text, job_description]
        
    #     # Convert text to TF-IDF features
    #     vectorizer = TfidfVectorizer(stop_words='english')
    #     tfidf_matrix = vectorizer.fit_transform(corpus)
        
    #     # Calculate cosine similarity between resume and job description
    #     similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
    #     # Convert similarity score to percentage
    #     score = round(similarity * 100, 2)
    #     return score
    
    # @staticmethod
    # def extract_skills_from_resume(resume_text):
    #     doc = nlp(resume_text)
    #     # ner_skills = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']  # Organizations are often used as skills

    #     # Extract noun chunks and check if they might represent skills (you can refine this list)
    #     potential_skills = [chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) == 1]  # Only single words
        
    #     # Further filter the noun chunks based on a predefined skill list or patterns if needed
    #     # For example, filtering out common words like 'course', 'maintained', etc.
    #     filtered_skills = [skill for skill in potential_skills if skill.lower() not in ['course', 'maintained', 'event']]
    
    #     return filtered_skills

