from flask import render_template, request, redirect, url_for, flash, send_file
from models import Job
from extensions import db

def register_routes(app):
    @app.route('/export-jobs')
    def export_jobs():
        source_site = request.args.get('source_site', '')
        search_term = request.args.get('search_term', '')
        location = request.args.get('location', '')

        query = Job.query
        
        if source_site:
            query = query.filter(Job.source_site == source_site)
        if search_term:
            query = query.filter(Job.title.contains(search_term) | Job.description.contains(search_term))
        if location:
            query = query.filter(Job.location.contains(location))

        jobs = query.order_by(Job.updated_time.desc()).all()

        if not jobs:
            flash('No jobs to export', 'warning')
            return redirect(url_for('index'))

        try:
            import pandas as pd
            from io import BytesIO

            df = pd.DataFrame([{
                'Title': job.title,
                'Description': job.description,
                'Source Site': job.source_site,
                'Posted Date': job.posted_date.strftime('%Y-%m-%d') if job.posted_date else '',
                'Last Updated': job.updated_time.strftime('%Y-%m-%d %H:%M'),
                'URL': job.url,
                'Location': job.location
            } for job in jobs])

            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)

            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                download_name='jobs_export.xlsx',
                as_attachment=True
            )
        except Exception as e:
            app.logger.error(f"Export failed: {str(e)}")
            flash(f'Export failed: {str(e)}', 'error')
            return redirect(url_for('index'))

    @app.route('/')
    def index():
        source_site = request.args.get('source_site', '')
        search_term = request.args.get('search_term', '')
        location = request.args.get('location', '')
        
        query = Job.query
        
        if source_site:
            query = query.filter(Job.source_site == source_site)
            
        if search_term:
            query = query.filter(Job.title.contains(search_term) | Job.description.contains(search_term))
        if location:
            query = query.filter(Job.location.contains(location))
        
        jobs = query.order_by(Job.updated_time.desc()).all()
        source_sites = [site[0] for site in db.session.query(Job.source_site).distinct().all() if site[0]]
        
        return render_template('index.html', 
                             jobs=jobs, 
                             source_sites=source_sites,
                             filters={
                                  'source_site': source_site,
                                  'search_term': search_term,
                                  'date_from': '',
                                  'date_to': ''
                              })
    
    @app.route('/fetch-jobs', methods=['POST'])
    def fetch_jobs():
        try:
            from services.fetcher_manager import FetcherManager
            
            fetcher_manager = FetcherManager(app)
            result = fetcher_manager.fetch_all_jobs()
            
            # Display success/failure messages
            if result['success']:
                flash(f"Successfully fetched jobs from: {', '.join(result['success'])}", 'success')
            
            if result['failed']:
                for site, error in result['failed'].items():
                    flash(f"Failed to fetch from {site}: {error}", 'error')
                    
        except Exception as e:
            # Add missing logger reference
            app.logger.error(f"Error in fetch_jobs route: {str(e)}")
            flash(f"An error occurred: {str(e)}", 'error')
            
        return redirect(url_for('index'))
    
    @app.route('/delete-jobs', methods=['POST'])
    def delete_jobs():
        try:
            # Delete all jobs
            rows_deleted = Job.query.delete()
            db.session.commit()
            
            if rows_deleted > 0:
                flash(f'Successfully deleted {rows_deleted} jobs', 'success')
            else:
                flash('No jobs to delete', 'info')
                
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting jobs: {str(e)}")
            flash(f'Error deleting jobs: {str(e)}', 'error')
            
        return redirect(url_for('index'))