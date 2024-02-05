# AI Hackathon 2023

## Organized by Foqum Analytics and IE University
In this competition, contestants were required to use an LLM to extract financial data from various term sheets which had very different layouts.
This solution created by Zaid Alsaheb, Sebastian Perilla, Alberto Puliga, Ahmad Albaba and Naji Danial won the **runner-up position** yielding an accuracy score of **96%**.

## How?
Our solution was very simple:
1. Extract all the text from the PDF files, and make it into a really long string.
2. Use regular expression to process the long string, removing all paragraphs without certain keywords or numbers in them.
3. Put the long string through the LLM which is provided with a very detailed prompt using RAGS. The LLM returns a JSON.
4. Turn the returned JSON into a CSV file
   
## Setup:
1. Create a venv and install dependencies from requirements.txt
2. Run main.py
