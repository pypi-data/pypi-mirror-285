import spacy
import dateparser
from datetime import datetime
import re

class YearExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")

    def extract_and_convert(self, text):
        # Check for specific phrases that should return an empty array
        if self.check_for_null_phrases(text):
            print(f"Detected null phrase in text: {text}")
            return []

        doc = self.nlp(text)
        date_entities = [ent for ent in doc.ents if ent.label_ == "DATE"]
        print("Extracted date entities:", date_entities)
        years = []

        for ent in date_entities:
            print("Processing entity:", ent.text)
            
            # Check if the entity contains a range of years
            range_match = re.search(r'\b(\d{4})\b.*?\b(\d{4})\b', ent.text)
            if range_match:
                start_year, end_year = map(int, range_match.groups())
                print(f"Identified year range: {start_year} to {end_year}")
                years.extend(range(start_year, end_year + 1))
            else:
                date = dateparser.parse(ent.text, settings={'PREFER_DATES_FROM': 'past'})
                print("Parsed date:", date)
                if date:
                    years.append(date.year)
                else:
                    relative_years = self.handle_relative_dates(ent.text)
                    if relative_years is not None:
                        print(f"Interpreted relative years: {relative_years}")
                        years.extend(relative_years)

        if not years:
            current_year = datetime.now().year
            print("No valid date found, returning current year:", current_year)
            years.append(current_year)
          
        return sorted(set(years))  # Return sorted unique years

    def handle_relative_dates(self, text):
        current_year = datetime.now().year
        text = text.lower()
        years = []

        if "previous year" in text:
            years.append(current_year - 1)
        elif "next year" in text:
            years.append(current_year + 1)
        elif "from" in text and "to" in text:
            range_match = re.search(r'from (\d{4}) to (\d{4})', text)
            if range_match:
                start_year, end_year = map(int, range_match.groups())
                years.extend(range(start_year, end_year + 1))
        elif "past" in text:
            past_years_match = re.search(r'past (\d+) years', text)
            if past_years_match:
                number_of_years = int(past_years_match.group(1))
                years.extend(range(current_year - number_of_years, current_year))
        elif "next" in text:
            next_years_match = re.search(r'next (\d+) years', text)
            if next_years_match:
                number_of_years = int(next_years_match.group(1))
                years.extend(range(current_year + 1, current_year + number_of_years + 1))

        return years if years else None

    def check_for_null_phrases(self, text):
        null_phrases = [
            "when",
            "in which year",
            "what is the year"
        ]
        text = text.lower()
        return any(phrase in text for phrase in null_phrases)