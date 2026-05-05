from reportlab.pdfgen import canvas

def generate_pdf(file_name, stats):

    pdf = canvas.Canvas("report.pdf")

    pdf.drawString(100, 750, "WhatsApp Chat Analysis Report")
    pdf.drawString(100, 720, f"File Name: {file_name}")

    pdf.drawString(100, 680, f"Total Messages: {stats[0]}")
    pdf.drawString(100, 660, f"Total Words: {stats[1]}")
    pdf.drawString(100, 640, f"Media Messages: {stats[2]}")
    pdf.drawString(100, 620, f"Links Shared: {stats[3]}")

    pdf.save()

    return "report.pdf"
