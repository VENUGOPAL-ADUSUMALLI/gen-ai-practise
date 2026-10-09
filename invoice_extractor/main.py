import fitz
from openai import OpenAI
from dotenv import load_dotenv

from models import Invoice

load_dotenv()

client = OpenAI()


pdf_path = "/Users/venugopal/Documents/gen_ai_practise/acme_invoice.pdf"

document = fitz.open(pdf_path)

invoice_text = ""

for page in document:
    invoice_text += page.get_text()

document.close()


MAX_RETRIES = 3


messages = [
    {
        "role": "system",
        "content": """
Extract the invoice information from the user's invoice.

Only extract information that is explicitly present.
Do not guess or invent values.
If information is missing, use null where the schema allows it.
"""
    },
    {
        "role": "user",
        "content": invoice_text
    }
]


for attempt in range(1, MAX_RETRIES + 1):

    print(f"\n--- Attempt {attempt} ---")
    try:

        response = client.chat.completions.parse(
            model="gpt-4o-mini",
            messages=messages,
            response_format=Invoice
        )

        message = response.choices[0].message
        if message.refusal:
            raise ValueError(
                f"Model refused to extract invoice: {message.refusal}"
            )
        invoice = message.parsed
        if invoice.total < 0:
            raise ValueError("Invoice total cannot be negative.")
        print("\nStructured output successful!")
        print(invoice)
        print(type(invoice))
        print("\nVendor:", invoice.vendor)
        print("Date:", invoice.date)
        print("Total:", invoice.total)
        print("Currency:", invoice.currency)
        for item in invoice.line_items:
            print(
                item.description,
                item.quantity,
                item.unit_price
            )

        break

    except Exception as error:

        print("\nExtraction failed:")
        print(error)
        if attempt == MAX_RETRIES:
            print("\n❌ Failed after all retries.")
            break
        messages.append({
            "role": "user",
            "content": f"""
The previous extraction was not acceptable.

Problem:
{error}

Please extract the invoice again.
Do not guess missing information.
Return the structured invoice.
"""})