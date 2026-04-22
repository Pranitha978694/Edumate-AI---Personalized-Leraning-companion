from reportlab.pdfgen import canvas
import sys

def create_pdf(filename="test.pdf"):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "Hello Edumate AI! This is a test PDF.")
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    create_pdf()
