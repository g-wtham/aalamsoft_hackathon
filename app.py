from flask import render_template, Flask, request, send_file, session
import os
from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator
from InvoiceGenerator.pdf import SimpleInvoice
import datetime 
import random

app = Flask(__name__)
app.secret_key = '1212121'

@app.route('/')
def index():
    return render_template('index.html')

os.environ["INVOICE_LANG"] = "en"

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        try:
            customer_name = request.form.get('customer_name')
            customer_email = request.form.get('customer_email')
            customer_invoice_date = request.form.get('customer_invoice_date')

            item_names = request.form.getlist('item_name')
            quantities = request.form.getlist('item_quantity')
            prices = request.form.getlist('item_price')

            client = Client(customer_name, email=customer_email)
            provider = Provider("Gowtham's Electronics", address="22, Ritchie Street", city="Chennai", email="curiousgowtham@gmail.com", country="India")
            creator = Creator('Gowtham Madhevasamy')
            invoice = Invoice(client, provider, creator)
            invoice.currency = 'Rs'
            invoice.paytype = "Credit Card"
            invoice.number = random.randint(90000000000000, 100000000000000)
            invoice_number_copy = invoice.number
            invoice.date = datetime.datetime.strptime(customer_invoice_date, '%Y-%m-%d').date()

            subtotal = 0.0

            for name, qty, price in zip(item_names, quantities, prices):
                qty = int(qty)
                price = float(price)
                subtotal += qty * price
                invoice.add_item(Item(qty, price, name))
                
            tax = 0.10 * subtotal
            after_taxation = subtotal + tax
            
            invoice.add_item(Item(0, subtotal, description="SUBTOTAL"))
            invoice.add_item(Item(0, tax, description="TAX"))
            invoice.add_item(Item(0, after_taxation, description="TOTAL (+10% tax)"))
            
            current_date = datetime.datetime.now()
            filename = f'invoice_{invoice_number_copy}_{current_date.strftime("%Y%m%d_%H%M%S")}.pdf'
            pdf = SimpleInvoice(invoice)    
            pdf.gen(filename, generate_qr_code=False)

            session['pdf_filename'] = filename
        except Exception as e:
            return f"Error: {e}"
        
        return send_file(filename, as_attachment=True)


@app.route('/preview', methods=['GET', 'POST'])
def preview_file():
    try:
        return send_file(session['pdf_filename'], as_attachment=False)
    except Exception as e:
        return f"File Preview Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)