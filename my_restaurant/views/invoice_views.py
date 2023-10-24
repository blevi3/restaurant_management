from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from django.core.mail import EmailMessage
from django.utils import timezone
from django.conf import settings



def generate_pdf_receipt(order_id, items, user, transaction_number):
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        normal_style = styles['Normal']

        title = Paragraph("Order Receipt", styles['Heading1'])
        elements.append(title)

        pub_info = [
            ("Legenda Pub",),
            ("Address: 123 Main Street, Cityville",),
            ("Phone: +1 (123) 456-7890",),
        ]
        for info in pub_info:
            elements.append(Paragraph(info[0], normal_style))
            elements.append(Spacer(1, 12)) 

        transaction = [
            ("Transaction Number:", transaction_number),
            ("Date:", timezone.now().strftime('%Y-%m-%d %H:%M:%S')),
            ("Cashier:", "John Doe"),
            ("Payment Method:", "Credit Card"),
        ]
        transaction_table = Table(transaction)
        transaction_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('SIZE', (0, 0), (-1, -1), 12),
        ]))
        elements.append(transaction_table)

        customer_info = [
            ("Customer Name:", user.username),
            ("Email:", user.email),
        ]
        customer_info_table = Table(customer_info)
        customer_info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('SIZE', (0, 0), (-1, -1), 12),
        ]))
        elements.append(customer_info_table)

        # Add a gap before the ordered items table
        elements.append(Spacer(1, 24))

        # Order Details
        data = [["Item", "Quantity", "Price", "Total"]]
        subtotal = 0
        for item in items:
            total_item_price = item.item.price * item.quantity
            data.append([item.item.name, item.quantity, f"{item.item.price} HUF", f"{total_item_price} HUF"])
            subtotal += total_item_price

        subtotal = 0.73 * subtotal 
        # Calculate VAT (27%)
        vat = 0.27 * subtotal

        table = Table(data)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), '#333333'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), '#EEEEEE'),
            ('GRID', (0, 0), (-1, -1), 1, '#CCCCCC')
        ]))
        elements.append(table)

        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Subtotal: {subtotal} HUF", normal_style))
        elements.append(Paragraph(f"VAT (27%): {vat:.2f} HUF", normal_style))
        total = subtotal + vat
        elements.append(Paragraph(f"Total: {total} HUF", normal_style))

        thank_you_message = "Thank you for your purchase!"
        elements.append(Spacer(1, 24))
        elements.append(Paragraph(thank_you_message, normal_style))

        doc.build(elements)

        buffer.seek(0)
    except Exception as e:
        print(f"Error generating PDF: {e}")
        buffer = None
    print("buffer: ",buffer)

    return buffer


def send_email_with_pdf(order_id, pdf_buffer, recipient_email):
    try:
        subject = 'Your Receipt'
        message = 'Thank you for your order. Here is your receipt.'
        from_email = settings.EMAIL_HOST_USER
        to_email = [recipient_email]

        email = EmailMessage(subject, message, from_email, to_email)
        pdf_buffer.seek(0)
        pdf_name = f'receipt_{order_id}.pdf'
        email.attach(pdf_name, pdf_buffer.read(), 'application/pdf')

        # Send the email
        email.send()
    except Exception as e:
        print(f"Error sending email: {e}")
