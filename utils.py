import json
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import os
import glob
import re
from typing import List
from PyPDF2 import PdfReader


load_dotenv()


def count_pdf_files(directory_path):
    pdf_files = glob.glob(directory_path + "/*.pdf")
    return len(pdf_files)


def process_pdf_directory(input_directory: str) -> List[str]:
    """
    Process all PDF files in a given directory, extracting paragraphs from each file
    only if the paragraph contains a number.

    Parameters:
    directory (str): The path to the directory containing PDF files.

    Returns:
    list[str]: A list of strings, each containing the filename and its extracted text.
    """
    extracted_texts = []
    keywords = [
        "ISIN",
        "Issuer",
        "Currency",
        "Underlying",
        "Strike",
        "Launch Date",
        "Final Valuation",
        "Maturity",
        "Cap",
        "Barrier",
        "Final Redemption",
        "Initial",
        "Final",
        "Strike",
    ]

    for filename in os.listdir(input_directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(input_directory, filename)

            # Create a PDF file reader object
            pdf_reader = PdfReader(file_path)
            num_pages = len(pdf_reader.pages)
            text = f"Filename: {filename}\n"
            file_has_text = False

            for page in range(num_pages):
                page_text = pdf_reader.pages[page].extract_text()
                if page_text:  # Check if text was extracted
                    # Split text into paragraphs and check each one
                    paragraphs = page_text.split("\n")
                    for paragraph in paragraphs:
                        if re.search(r"\d", paragraph) or any(
                            keyword in paragraph for keyword in keywords
                        ):
                            text += paragraph + " "
                            file_has_text = True

            if file_has_text:
                extracted_texts.append(text)

    print("Extracted text\n")
    return extracted_texts


def extract_json_from_term_sheet(text: str) -> str | None:
    """
    Extracts information from a financial term sheet in PDF format and organizes it into a JSON file.

    Args:
        text (str): A string representing the input PDF file.

    Returns:
        str: A string representing the extracted information in JSON format (which is then appended to a list)
    """
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content":
                    """
                    Instructions for OCR Term Sheet Extraction and JSON Generation

- File name:
Example: XS2021832634.pdf (This value cannot be null)

- ISIN: (is the internationally recognized code for identifying financial instruments in the markets and in transactions.
Example: XS1878076543 (This value cannot be null)

- Issuer: Which is the bank that is issuing the sheet itself. (Note: This value cannot be null and make sure to use strictly Bloomberg Code Abbreviations):

Example: 
Citigroup Global Markets Funding Luxembourg S.C.A. (“CGMFL”)

Desired Output: Citi

Explanation (in steps):
Locate the Issuer Information:

Look for the section in the term sheet that provides information about the issuer of the financial instrument.
Read the Issuer Name:

Carefully read the full name of the issuer. In this case, it's "Citigroup Global Markets Funding Luxembourg S.C.A."

Identify the Bank Name:

Identify the specific name of the bank within the issuer's name. In this example, the bank name is "Citigroup."
Use Common Bank Abbreviation:

For large banks and financial institutions, common abbreviations are often used. In the case of Citigroup, the standard abbreviation is "Citi."

Consider Context and Style:

Pay attention to the context of the document and any specific abbreviations or naming conventions used. In financial contexts, banks may have standardized abbreviations, so use those in all cases.

Example #2: 
Issuer BNP Paribas Issuance B.V. (S&P's A+) (on an unsecured basis)

Desired Output: BNP

Explanation #2 (in steps):
Locate the Issuer Information:

Look for the section in the term sheet that provides information about the issuer of the financial instrument.
Read the Issuer Name:

Carefully read the full name of the issuer. In this case, it's "BNP Paribas Issuance B.V."

Identify the Bank Name:

Identify the specific name of the bank within the issuer's name. In this example, the bank name is "BNP Paribas."

Use Common Bank Abbreviation:

For large banks and financial institutions, common abbreviations are often used. In the case of Citigroup, the standard abbreviation is "BNP."

Consider Context and Style:

Pay attention to the context of the document and any specific abbreviations or naming conventions used. In financial contexts, banks have standardized abbreviations, so use those in all cases, with no exceptions.

- Ccy : Which is the currency in which the transaction that it has been done in. Use Standard National Currency abbreviations only.
Example: "USD" (Note: This value cannot be null)

- Underlying(s): List of underlying assets or indices associated with the product. Provide up to five valid tickers. Example: ['SX5E', 'UKX', 'SPX']." (Note: This value cannot be null and make sure to use strictly Bloomberg Code Abbreviations, but exclude the Location section of the abbreviation ex: "RNO FP" should be "RNO".)


Example:
18M Certificate Plus Worst-of on DAI GY, RNO FP, VOW3 GY,
PAH3 GY and GM UN with equally weighted performance on the 
upside in USD

Underlying Shares i Name of Underlying Sharei Bloomberg Code Sharei Initial wi
1 Renault SA RNO FP 34.3 20% 2 Volkswagen AG VOW3 GY 185.6 0% 3 Daimler AG DAI GY 88.09 20% Porsche Automobil Holding SE PAH3 GY 85.86 20% General Motors Co GM UN 59.27 20%

Desired Output: RNO, VOW3, DAI, PAH3, GM

Explanation (in steps):
Identify the Sections:

Look for sections in the term sheet that are labeled or separated with clear headings. Common sections include "Summary" and "Table." Summary normally follows a "sentence structured" pattern, while Table follows a more "quantitative structure".

Examine the "Summary" Section:

The "Summary" section often contains a concise summary or description of the financial instrument or transaction. It may include key details like the duration, structure, and involved assets. In this case, the "Summary" section includes the phrase "18M Certificate Plus Worst-of on DAI GY, RNO FP, VOW3 GY, PAH3 GY, and GM UN with equally weighted performance on the upside in USD." Never use the "Summary" Section for the Underlying(s) field.

Locate the "Table" Section:

The "Table" section typically presents detailed information in a tabular format. In this case, the "Underlying Shares" table provides details about the individual underlying shares, including their names and Bloomberg Codes.

Extract Bloomberg Abbreviations:

In the "Table" section, identify the Bloomberg Codes associated with each underlying share. Extract the Bloomberg abbreviations from these codes.
Renault SA: RNO
Volkswagen AG: VOW3
Daimler AG: DAI
Porsche Automobil Holding SE: PAH3
General Motors Co: GM
Desired Output Order:

Arrange the extracted abbreviations in the order in which they were read in the "Table" Section, with the first abbreviation being the first outputted. As such, the field here would result in:
RNO, VOW3, DAI, PAH3, GM

By following these steps, you can ensure that you extract Bloomberg abbreviations only from the relevant "Table" section, and you can clearly differentiate between the "Summary" and "Table" sections on other financial term sheets.

(Note: Output the values for the field in the order that they are read from the "Table" Section.)

- Strike: The strike price is the price at which the holder of the option can exercise the option to buy or sell an underlying security, depending on whether they hold a call option or put option. An option is a contract where the option buyer purchases the right to exercise the contract at a specific price, which is known as the strike price. It cannot be any letters, simply put strike is strictly numbers). If the same strike price is shown multiple times, just include it once. The sequence of the numbers does not have to be in ascending order, they need to be returned in the order that they are read.

Example: 4229.53 (This value cannot be null and cannot be a percentage value)

(Note: Underlyings and Strike are used in tables and are correlated. This means that they are tied to one another so make sure to keep them both in the order they are received.)


- Launch Date: This value is not the issue date, it is the date of the launch or initial valuation of the product, marking the start of its lifecycle (Which is in the format of dd/mm/yyyy)
Example: 10/03/2023 (Note: This value cannot be null)


- Final Val. Day: This is also called trade day and the day on which the Final Price in respect of such Defaulted Credit is determined in respect of an Event Determination Date. NOT TO BE CONFUSED WITH ANY OTHER DATE. (Which is in the format of dd/mm/yyyy)
Example: 11/07/2023 (Note: This value cannot be null)


- Maturity: This is the agreed-upon date on which the investment ends, often triggering the repayment of a loan or bond, the payment of a commodity or cash payment, or some other payment or settlement term.  (Which is in the format of dd/mm/yyyy)
Example: 18/07/2023 (Note: This value cannot be null)


- Cap: The upper limit/max or cap of the product's return, expressed as a percentage. It will always be over 100/100%, so exclude values that are under that baseline. (Note: This value can be null & have decimals.)

Example:
If IndexFinal is greater than or equal to 120.50% x IndexInitial: N x 120.50%

Desired Output: 120.50

Explanation: 
So, the value 120.50% (CAP) is acting as a threshold or cap, and if the final index exceeds this threshold compared to the initial index, it triggers a specific calculation involving the variable N. As such, the output field is 120.50

Example #2: 
If the Final Price is equal to or greater than the Put Barrier Price, the Final Redemption Amount shall be calculated in accordance with the following formula:
Calculation Amount × MAX[121.50%; MIN(130.00%; Final Price / Initial Price)

Desired Output #2: 130

Explanation #2:  
This formula sets up a mechanism for determining the Final Redemption Amount based on the Final Price compared to the Put Barrier Price. The Final Redemption Amount is adjusted within certain bounds,  with a maximum (cap) of 130.00%. 


- Barrier or Knock-in Option or Knock-Out Option: 
The barrier level of the product, specified in percentage terms. This represents a critical price level for features like knock-in. Example: 70 (indicating 70% of the initial price) (Note: This value cannot be null)

                Additional Considerations:
                
                Account for variations in document layout, text formatting, and OCR errors. Consider implementing a mechanism to handle missing values or multiple entries for Underlying(s) and Strike Prices. Prioritize precision in extracting numeric values, especially dates and financial figures. Implement these instructions to ensure accurate extraction and JSON formatting, adapting to the nuances of financial term sheets in PDF format.
                
                Organize the extracted information into a JSON file following this format (Do not add any extra fields):
                
                JSON
                {
                  "File Name": "Extracted File Name",
                  "ISIN": "Extracted ISIN",
                  "Issuer": "Extracted Issuer",
                  "Ccy": "Extracted Ccy",
                  "Underlying(s)": ["List of Extracted Underlying(s)"],
                  "Strike": ["List of Extracted Strike Prices"],
                  "Launch Date": "Extracted Launch Date",
                  "Final Val. Day": "Extracted Final Valuation Day",
                  "Maturity": "Extracted Maturity Date",
                  "Cap": "Extracted Cap",
                  "Barrier": "Extracted Barrier"
                }
                
                Ensure that dates are formatted as dd/mm/yyyy, and numerical values are appropriately formatted. The OCR tool should handle variations in document layout and text formatting. Provide the extracted information in a single JSON for each input 

The result has to be exclusively in JSON

We will give you a set of extremely long strings that we will process and if they do not contain any of the key fields that we are looking for exclude them. Make sure that the order of the fields is kept strictly as mentioned above.  Furthermore, the input will only accept characters from the English Alphabet and if you find a value in "Cap" that is not return the empty string instead of filling it in with "N/A" and/or "Not Specified".
                    """,
            },
            {"role": "user", "content": f"{text}, please wait for "},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
        max_tokens=4095,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    return response.choices[0].message.content


def json_list_to_csv(json_list: List[str], output_directory: str) -> None:
    """
    Convert a list of JSON strings to an Excel file with specified columns and save it
    in the specified directory with a timestamped filename. Each dictionary or JSON string corresponds to one row.

    Parameters:
        json_list (list[str]): List of JSON strings or dictionaries.
        output_directory (str): Directory path to store the CSV output file.

    Returns:
        None
    """

    df = pd.DataFrame()
    for data in json_list:
        # Check if the item is a string or a dictionary
        if isinstance(data, str):
            try:
                # Try to load the string as a dictionary
                data = json.loads(data)
            except json.JSONDecodeError:
                # Handle the case where the item is not a valid JSON string
                print(f"Skipping invalid JSON string in json_list: {data}")
                continue

        # Convert dictionary to DataFrame
        row_df = pd.json_normalize(data)
        df = pd.concat([df, row_df], ignore_index=True)

    timestamp = datetime.now().strftime("%d_%H:%M:%S")
    csv_file_name = f"shabab_output.csv"

    csv_file_path = os.path.join(output_directory, csv_file_name)
    df.to_csv(csv_file_path, index=False)
    print(f"CSV file '{csv_file_path}' created successfully")
