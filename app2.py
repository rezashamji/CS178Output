from flask import Flask
from models import db, Agency, Stops

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gtfs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

# Example route to add an agency
@app.route('/add_agency', methods=['POST'])
def add_agency():
    # Example data, you would get this from request.form or request.json in a real application
    agency_data = {
        'agency_id': '1',
        'agency_name': 'Example Agency',
        'agency_url': 'http://example.com',
        'agency_timezone': 'Europe/London'
    }
    agency = Agency(**agency_data)
    db.session.add(agency)
    db.session.commit()
    return "Agency added successfully!"

if __name__ == '__main__':
    app.run(debug=True)