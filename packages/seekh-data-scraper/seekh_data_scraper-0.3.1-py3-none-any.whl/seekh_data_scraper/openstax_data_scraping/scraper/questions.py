# scraper/questions.py

import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_group_2_urls(url_list):
    question_data = []
    
    for url in url_list:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        os_problem_containers = soup.find_all("div", class_="os-problem-container")
        book_name = url.split("/")[-3]
        question_type_name = url.split("/")[-1]
        for container in os_problem_containers:
            # Find the question inside <div class="os-question-container">
            try:
                question_paragraphs = container.find_all("p")
                question_divs = container.find_all("div", {"data-type": "question-stem"})
                question_text = ""
                
                for paragraph in question_paragraphs:
                    question_text += paragraph.get_text(strip=True) + "\n"
                
                for div in question_divs:
                    question_text += div.get_text(strip=True) + "\n"
                
                question_text = question_text.strip()
                
            except AttributeError:
                question_text = None
            # Find the options if it's an MCQ type question
            options = []
            li_tags = container.find_all("li")
            for li_tag in li_tags:
                options.append(li_tag.text.strip())
            if options:  # MCQ type question
                question_type = "mcq"
                options.extend([None] * (4 - len(options)))  # Add None for missing options
                question_data.append((question_type_name, book_name, question_type, question_text, options[0], options[1], options[2], options[3]))
            else:  # General type question
                question_type = "general"
                question_data.append((question_type_name, book_name, question_type, question_text, None, None, None, None))
    df = pd.DataFrame(question_data, columns=["Question Type Name", "Book Name", "Question Type", "Question", "Option A", "Option B", "Option C", "Option D"])
    return df