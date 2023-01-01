from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from collections import Counter
from PyPDF2 import PdfFileReader
import csv
import codecs
import plotly.express as px
from plotly.offline import plot


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the selected prefix
        prefix = request.form['prefix']

        # Get the uploaded files
        pdf_files = request.files.getlist('pdf_files')

        # Check if no files were selected
        if not pdf_files:
            return render_template('index.html', error='Please select at least one PDF file')

        # Check if no prefix was selected
        if not prefix:
            return render_template('index.html', error='Please select a prefix')

        # Create a list to store the extracted codes
        codes = []

        # Loop through the selected files
        for file in pdf_files:
            # Save the file to a temporary location
            filename = secure_filename(file.filename)
            file.save(filename)

            # Open the PDF file using PyPDF2
            pdf = PdfFileReader(filename)
            

            # Loop through the pages of the PDF
            for page_num in range(pdf.getNumPages()):
                # Get the page
                page = pdf.getPage(page_num)

                # Extract the text from the page
                text = page.extractText()

                # Split the text into words
                for word in text.split():
                    # Check if the word starts with the selected prefix
                    if word.startswith(prefix):
                        # Add the word to the list of codes
                        codes.append(word)

        # Check if no codes were found
        if not codes:
            return render_template('index.html', error='No codes were found in the selected PDF files')
        
        # Create a dictionary to map codes to their names
        code_names = {}

        # Open the TSV file using the codecs module
        with codecs.open('commercial.tsv', 'r', encoding='utf-8') as tsv_file:
            # Read the TSV file
            reader = csv.reader(tsv_file, delimiter='\t')

            # Skip the header row
            next(reader)

            # Create a dictionary to map codes to their names
            code_names = {}

            # Loop through the rows in the TSV file
            for row in reader:
                # Get the code and name from the row
                code = row[0]
                name = row[1]
                
                # Add the code and name to the dictionary
                code_names[code] = name
                
        # Create a list to store the code names
        names = []

        # Loop through the extracted codes
        for code in codes:
            # Look up the name for the code in the dictionary
            name = code_names.get(code, 'Unknown')
            
            if name != 'Unknown':
                # Add the code and name to the list
                names.append((code, name))
        
        # Create a list of dictionaries containing the code and name for each code
        code_data = [{'code': code, 'name': name} for code, name in names]

        # Count the occurrences of each code and name
        code_counts = Counter([d['code'] for d in code_data])
        
        # Create a set to store the unique codes and names
        unique_codes_names = set()
        
        # Loop through the codes and names
        for code, name in names:
            # Add the code and name to the set
            unique_codes_names.add((code, name))

        # Create a list of tuples containing the unique codes and names
        codes_names = list(unique_codes_names)

        # Get the labels and values for the pie chart
        labels = [d['name'] for d in code_data]
        values = [code_counts[d['code']] for d in code_data]

        # Create the pie chart
        fig = px.pie(names=labels, values=values)

        # Show the pie chart
        fig.show()
        
        # Convert the figure to HTML
        plot_html = plot(fig, include_plotlyjs=True, output_type='div')

        # Render the template and pass the list of codes to it
        return render_template('index.html', names=codes_names, plot_html=plot_html, code_counts=code_counts)
    else:
        # Render the template with the form
        return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
