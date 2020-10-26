#!/usr/bin/python3.7
from csv import reader
import argparse

parser = argparse.ArgumentParser(
    usage="Creates an HTML file from a .csv with 3 columns and the img in the 3rd"
    )
parser.add_argument('file',
                     help="""csv file must match the following layout:\n
                    ID | Organization | HQ_Country | HQ_City/State | LinkedIn | New Logo URL | Website | Bio
                    """)
parser.add_argument('file', help="csv file")



def html_from_data(filename, data=None):
    """
    Generate an html file from data
    data is list from appropriately formatted csv or None
    if data is None, filename should be the input csv, else it's the output file    
    """

    if not data:
        with open(filename) as f:
            lines = [x for x in reader(f)]
    else:
        lines = data
        
    html = """
    <html>
        <head>
        <style>
        table {
            border-collapse: collapse;
            
        }
        tr {
            height: 175px
        }
        th, td {
            border: 1px solid;
            padding: 3px 5px;
        }
        img {
            width: 175px;
            height: auto;
        }
        </style>
        </head>
        <body>
            <table>
                <thead>
                    <tr>
                        <th>ID</th><th>NAME</th><th>LOGO</th><th>LOCAL IMAGE LINK</th><th>URL</th>
                    </tr>
                </thead>
    """


    for line in lines:
        if line[0].lower() == 'id':
            continue
        
        try:
            html += f"""
            <tr>
                <td>{line[0]}</td><td>{line[1]}</td><td><img src='{line[-1]}'/></td><td>{line[-1]}</td><td>{line[5]}</td>
            </tr>
            
            """
        except IndexError:
            pass
        
        except Exception as e:
            print(e)

    html += """
            </table>
        </body>
    </html>
    """

    if not data:
        outfile = filename.split('.')[0] + '.html'
    else:
        outfile = filename
    with open(outfile, 'w') as f:
        f.write(html)
    print(f'file saved to: {outfile}')
    

if __name__ == '__main__':
    args = parser.parse_args()
    html_from_data(args.file)
    
    

    


