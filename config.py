# Configuration settings for the Job Fetcher application

# Fetcher settings
FETCHER_SETTINGS = {
    'linkedin': {
        'url': 'https://www.linkedin.com/jobs/search/',
        'timeout': 30,
        'max_retries': 3
    },
    'indeed': {
        'url': 'https://www.indeed.com/jobs',
        'timeout': 30,
        'max_retries': 3
    }
    # Add more job sites here
}

# Database settings
DATABASE_URI = 'sqlite:///jobs.db'

# Application settings
DEBUG = True
SECRET_KEY = 'dev-key-for-flash-messages'  # Change in production

# Logging settings
LOG_FILE = 'app.log'
LOG_LEVEL = 'INFO'  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'