from flask import render_template, Flask, request, send_file
import os
from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator
from InvoiceGenerator.pdf import SimpleInvoice
import datetime

app = Flask(__name__)
app.secret_key = '1212121'

@app.route('/')
def index():
    return render_template('index.html')

os.environ["INVOICE_LANG"] = "en"

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    customer_name = request.form.get('customer_name')
    current_date = datetime.datetime.now()

    item_names = request.form.getlist('item_name')
    quantities = request.form.getlist('item_quantity')
    prices = request.form.getlist('item_price')

    client = Client(customer_name)
    provider = Provider("Gowtham's Electronics")
    creator = Creator('Gowtham Madhevasamy')
    invoice = Invoice(client, provider, creator)
    invoice.currency_locale = 'en_IN'
    
    for name, qty, price in zip(item_names, quantities, prices):
        qty = int(qty)
        price = float(price)
        invoice.add_item(Item(qty, price, description=name))

    filename = f'invoice_{current_date.strftime("%Y%m%d_%H%M%S")}.pdf'
    pdf = SimpleInvoice(invoice)
    pdf.gen(filename, generate_qr_code=False)

    return send_file(filename, as_attachment=True)



if __name__ == '__main__':
    app.run(debug=True)