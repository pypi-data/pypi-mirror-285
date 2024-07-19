Take the Text And Retrieve the Year That Mention

How To Install

!pip install spacy
!python -m spacy download en_core_web_lg
!pip install year-extractor

Usage

from year_extractor.converter import YearExtractor

# Initialize the YearExtractor
extractor = YearExtractor()

# Define your text
text = "I graduated in last year."

# Extract the year
year = extractor.extract_and_convert(text)

# Print the result
print("Extracted year:", year)
