from flask import Flask, render_template, request
import pandas as pd
import scrap


app = Flask(__name__)


def search_products(product_name):
    scrap.scrap_web(product_name)
    df = pd.read_excel("sorted_product.xlsx")
    matching_products = df[df['Name'].str.contains(product_name, case=False)]
    return matching_products.to_dict('records')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['search_query']
        result = search_products(user_input)
        return render_template('index.html', result=result)
    return render_template('index.html', result=None)


if __name__ == '__main__':
    app.run(debug=True)