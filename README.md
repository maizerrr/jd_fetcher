# Job Fetcher

A Python/Flask web application that scrapes job listings from multiple sites, stores them in a SQLite database, and displays them with search and filter capabilities.

## Features

- Scrapes job listings from multiple job sites (LinkedIn, Indeed)
- Stores job data in a SQLite database
- Prevents duplicate job listings
- Provides a web interface to view and filter jobs
- Allows filtering by source site, search term, and date range
- Extensible architecture for adding new job sites

## Build

1. Clone the repository:
   ```
   git clone https://github.com/maizerrr/jd_fetcher.git
   cd jd_fetcher
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   pip install pyinstaller
   ```
3. Run build command:
   ```
   pyinstaller --name jd_fetcher \
   --add-data "templates/*:templates" \
   --add-data "fetchers/*:fetchers" \
   --add-data "services/*:services" \
   --hidden-import "models" \
   --hidden-import "routes" \
   --hidden-import "extensions" \
   --onefile \
   --noconfirm \
   app.py
   ```

## Usage

1. <a href="https://github.com/maizerrr/jd_fetcher/releases">Download</a> the execubale according to your system:
   - For Windows: `jd_fetcher_win_x86_64.exe`
   - For macOS: `jd_fetcher_darwin_x86_64`

2. Launch the application:
   ```
   ./jd_fetcher
   ```
   a new browser window should open with the application running.

3. Use the web interface to:
   - View existing job listings
   - Filter jobs by source site, search term, or date range
   - Fetch new job listings by clicking the "Fetch New Jobs" button

## Project Structure

```
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── extensions.py           # Flask extensions
├── models.py               # Database models
├── routes.py               # Application routes
├── requirements.txt        # Python dependencies
├── fetchers/               # Job fetcher modules
│   ├── __init__.py
│   ├── acadian_fetcher.py  # Acadian implementation
│   ├── base_fetcher.py     # Base fetcher class
│   ├── indeed_fetcher.py   # Indeed implementation
│   ├── linkedin_fetcher.py # LinkedIn implementation
│   └── qube_rt_fetcher.py  # QubeRT implementation
├── services/               # Application services
│   ├── __init__.py
│   └── fetcher_manager.py  # Manages job fetchers
└── templates/              # HTML templates
    ├── base.html           # Base template
    └── index.html          # Job listing page
```

## Adding New Job Sites

1. Create a new fetcher class in the `fetchers/` directory:
   ```python
   from .base_fetcher import BaseFetcher
   
   class NewSiteFetcher(BaseFetcher):
       def __init__(self):
           super().__init__(site_name="New Site", url="https://example.com/jobs")
       
       def parse_jobs(self, html: str):
           # Implement site-specific parsing logic
           # Return a list of job dictionaries
           pass
   ```

2. Register the new fetcher in `services/fetcher_manager.py`:
   ```python
   from fetchers.new_site_fetcher import NewSiteFetcher
   
   class FetcherManager:
       def __init__(self):
           self.fetchers = [
               LinkedInFetcher(),
               IndeedFetcher(),
               NewSiteFetcher()  # Add your new fetcher here
           ]
   ```

3. Add configuration for the new site in `config.py` (optional):
   ```python
   FETCHER_SETTINGS = {
       # Existing settings...
       'new_site': {
           'url': 'https://example.com/jobs',
           'timeout': 30,
           'max_retries': 3
       }
   }
   ```