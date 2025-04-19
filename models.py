from datetime import datetime
from extensions import db

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    source_site = db.Column(db.String(50))
    url = db.Column(db.String(500), unique=True)
    location = db.Column(db.String(100))
    posted_date = db.Column(db.DateTime)
    updated_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Job {self.title} from {self.source_site}>'