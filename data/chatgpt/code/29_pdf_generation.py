# create python code to take a document written in Markdown and render it as a PDF, with an image for the header.   please use argparse for the input values
# error using reportlab, it decided to recode using pdfkit
# deprecation error regarding pypdf2, asked me to switch to pypdf4

import argparse
import markdown2
import pdfkit
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from tempfile import NamedTemporaryFile
from PyPDF4 import PdfFileWriter, PdfFileReader


def create_pdf(html_content, output_file, header_image):
    # Create a temporary PDF with the content
    content_pdf = NamedTemporaryFile(delete=False, suffix=".pdf")
    pdfkit.from_string(html_content, content_pdf.name)

    # Create the final PDF with the header image
    header_pdf = BytesIO()
    c = canvas.Canvas(header_pdf, pagesize=letter)
    c.drawImage(header_image, 0, 750, 612, 100)
    c.showPage()
    c.save()

    # Combine the header and content PDFs
    header_pdf.seek(0)
    header_reader = PdfFileReader(header_pdf)
    content_reader = PdfFileReader(content_pdf.name)

    output_writer = PdfFileWriter()
    for i in range(header_reader.getNumPages()):
        output_writer.addPage(header_reader.getPage(i))
    for i in range(content_reader.getNumPages()):
        output_writer.addPage(content_reader.getPage(i))

    with open(output_file, "wb") as file:
        output_writer.write(file)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert a Markdown document to a PDF with an image header.")
    parser.add_argument("input_file", help="The Markdown input file")
    parser.add_argument("output_file", help="The PDF output file")
    parser.add_argument("header_image", help="The header image file")
    return parser.parse_args()

def convert_markdown_to_html(input_file):
    with open(input_file, "r") as file:
        markdown_content = file.read()
    return markdown2.markdown(markdown_content)


def main():
    args = parse_arguments()
    html_content = convert_markdown_to_html(args.input_file)
    create_pdf(html_content, args.output_file, args.header_image)

if __name__ == "__main__":
    main()
