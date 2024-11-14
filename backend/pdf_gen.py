from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from io import BytesIO

def summarize_chat_history (chat_history):
    from groq import Groq
    from dotenv import load_dotenv
    import os
    load_dotenv()

    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

    token_summ = ""
    for i, chat in enumerate(chat_history):
        token_summ += f"{i}) " + chat['content'] + "\n"
        
    prompt = [
        {
            "role": "user",
            "content": f"Imagine you're a top-tier summarizer. I'll give you a list of final responses from a chat conversation, and I'd like you to summarize them thoroughly and concisely. Preferably, use bullet points. Some responses may include warnings that begin with the word 'please,' and those can be ignored. Only summarize the responses with valid information. Provide the final summary in double quotes without any introduction or conclusion statements. Ensure the summary is clear and detailed for the reader, not overly brief or condensed. Here are the responses: {token_summ}"
        },
    ]
    
    chat_completion = client.chat.completions.create(
    messages=prompt,
    model="llama3-8b-8192",
    )
    with open ("summ_chat_hist.txt", 'w') as sch:
        sch.write(chat_completion.choices[0].message.content.strip())




def write_pdf():

    template_pdf = PdfReader("template.pdf")
    template_page = template_pdf.pages[0]  # Assuming the template has only one page

    writer = PdfWriter()

    with open("summ_chat_hist.txt", 'r', encoding='ISO-8859-1') as f:
        text = f.read()

    def wrap_text(can, text, max_width):
        lines = []
        paragraphs = text.splitlines()  # Split by line breaks in the original text

        for paragraph in paragraphs:
            words = paragraph.split()
            if not words:  # If it's an empty line (paragraph break), keep it
                lines.append("")
                continue

            line = ""
            for word in words:
                if can.stringWidth(line + " " + word, "Helvetica", 12) <= max_width:
                    if line:
                        line += " " + word
                    else:
                        line = word
                else:
                    lines.append(line)
                    line = word
            lines.append(line)  # Append the last line of the paragraph

        return lines

    left_margin = 0.8*inch  # 1 inch left margin
    right_margin = inch  # 1 inch right margin
    max_text_width = A4[0] - left_margin - right_margin  # Maximum width for text
    top_margin = A4[1] - 3 * inch  # Leave 2.5 inches from the top
    bottom_margin = inch  # 1 inch bottom margin
    line_height = 14  # Line height (adjust as needed)

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    
    wrapped_lines = wrap_text(can, text, max_text_width)

    def write_page(can, page_lines, y_position):
        for line in page_lines:
            if y_position <= bottom_margin:  # Check if we reached the bottom margin
                can.showPage()  # Start a new page
                y_position = top_margin
            can.drawString(left_margin, y_position, line)
            y_position -= line_height
        return y_position

    y_position = top_margin

    while wrapped_lines:
        y_position = write_page(can, wrapped_lines[:int((top_margin - bottom_margin) / line_height)], y_position)
        wrapped_lines = wrapped_lines[int((top_margin - bottom_margin) / line_height):]

    can.save()

    packet.seek(0)

    overlay_pdf = PdfReader(packet)
    
    for i in range(len(overlay_pdf.pages)):
        new_template_page = template_pdf.pages[0]  # Using the same template for new pages
        overlay_page = overlay_pdf.pages[i]

        new_template_page.merge_page(overlay_page)

        writer.add_page(new_template_page)

    with open("final_output.pdf", 'wb') as f:
        writer.write(f)
