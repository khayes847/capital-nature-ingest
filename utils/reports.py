import csv
from datetime import datetime
import os
import re

import boto3
import pandas as pd

from .event_source_map import event_source_map

def events_to_csv(events, is_local = True, bucket = None):
    '''
    Void function that writes events to csv, either locally or to an S3 bucket.

    Parameters:
        events (list): a list of dicts, with each dict representing a single event.
        is_local (bool): True if you want to write the csv locally. False if you want to
                         write the csv to S3 (must supply a valid bucket name as well)
        bucket (str or None): the name of the public S3 bucket. None by default.

    Returns:
        None
    '''
    now = datetime.now().strftime("%m-%d-%Y")
    filename = f'cap-nature-events-scraped-{now}.csv'
    fieldnames = {'Do Not Import','Event Name','Event Description','Event Excerpt',
                  'Event Start Date','Event Start Time','Event End Date',
                  'Event End Time','Timezone','All Day Event',
                  'Hide Event From Event Listings','Event Sticky in Month View',
                  'Feature Event','Event Venue Name',
                  'Event Organizers','Event Show Map Link','Event Show Map',
                  'Event Cost','Event Currency Symbol','Event Currency Position',
                  'Event Category','Event Tags','Event Website',
                  'Event Featured Image','Allow Comments',
                  'Event Allow Trackbacks and Pingbacks'}
    out_path = os.path.join(os.getcwd(), 'data', filename)
    if not os.path.exists(os.path.join(os.getcwd(), 'data')):
        os.mkdir(os.path.join(os.getcwd(), 'data'))
    with open(out_path, mode = 'w', encoding = 'utf-8', errors = 'ignore') as f:
        writer = csv.DictWriter(f, fieldnames = fieldnames)
        writer.writeheader()
        for event in events:
            writer.writerow(event)
    if not is_local and bucket:
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(out_path,
                                   bucket,
                                   'capital-nature/{0}'.format(filename))
    else:
        return out_path

def get_past_venues():
    '''
    Returns a set of event venues from current venue csv in temp/ (if it exists)
    and then deletes that file (if it exists) as it will soon be replaced by a new,
    more updated one.

    Parameters:
        None

    Returns:
        past_venues (set): a set of event venues, or an empty set if there are none
    '''
    data_path = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    data_files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]
    try:
        venue_file = [f for f in data_files if 'venues-' in f][0]
    except IndexError:
        #IndexError because there's no past file
        return set()
    venue_file = os.path.join(data_path, venue_file)
    venues = []
    with open(venue_file, errors = 'ignore') as f:
        reader = csv.reader(f)
        for i in reader:
            venue = i[0]
            venues.append(venue)
    past_venues = set(venues)
    past_venues.remove('VENUE NAME')
    os.remove(venue_file)

    return past_venues

def venues_to_csv(events, is_local = True, bucket = None):
    '''
    Void function that writes unique event venues to csv, either locally or to
    an S3 bucket.

    Parameters:
        events (list): a list of dicts, with each dict representing a single event.
        is_local (bool): True if you want to write the csv locally. False if you want to
                         write the csv to S3 (must supply a valid bucket name as well)
        bucket (str or None): the name of the public S3 bucket. None by default.

    Returns:
        None
    '''
    venues = []
    for event in events:
        event_venue = event['Event Venue Name']
        venues.append(event_venue)
    past_venues = get_past_venues()
    unique_venues = set(venues) | past_venues
    now = datetime.now().strftime("%m-%d-%Y")
    filename = f'cap-nature-venues-scraped-{now}.csv'
    out_path = os.path.join(os.getcwd(), 'data', filename)
    if not os.path.exists(os.path.join(os.getcwd(), 'data')):
        os.mkdir(os.path.join(os.getcwd(), 'data'))
    with open(out_path,
              mode = 'w',
              encoding = 'utf-8',
              errors = 'ignore') as f:
        writer = csv.writer(f)
        _venues = ['VENUE NAME']
        _venues.extend(list(unique_venues))
        venues_to_write = _venues
        for venue in venues_to_write:
            writer.writerow([venue])
    if not is_local and bucket:
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(out_path,
                                   bucket,
                                   'capital-nature/{0}'.format(filename)
                                    )

def get_past_organizers():
    '''
    Returns a set of event organizers from current organizer csv in temp/ (if it exists)
    and then deletes that file (if it exists) as it will soon be replaced by a new,
    more updated one.

    Parameters:
        None

    Returns:
        past_organizers (set): a set of event organizers, or an empty set if there are none
    '''
    data_path = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    data_files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path,f))]
    try:
        organizer_file = [f for f in data_files if 'organizers-' in f][0]
    except IndexError:
        #IndexError because there's no past file
        return set()
    organizer_file = os.path.join(data_path, organizer_file)
    organizers = []
    with open(organizer_file) as f:
        reader = csv.reader(f)
        for i in reader:
            organizer = i[0]
            organizers.append(organizer)
    past_organizers = set(organizers)
    past_organizers.remove('Event Organizer Name(s) or ID(s)')
    os.remove(organizer_file)

    return past_organizers

def organizers_to_csv(events, is_local = True, bucket = None):
    '''
    Void function that writes unique event organizers to csv, either locally or to
    an S3 bucket.

    Parameters:
        events (list): a list of dicts, with each dict representing a single event.
        is_local (bool): True if you want to write the csv locally. False if you want to
                         write the csv to S3 (must supply a valid bucket name as well)
        bucket (str or None): the name of the public S3 bucket. None by default.

    Returns:
        None
    '''
    organizers = []
    for event in events:
        event_organizer = event['Event Organizers']
        organizers.append(event_organizer)
    past_organizers = get_past_organizers()
    unique_organizers = set(organizers) | past_organizers
    now = datetime.now().strftime("%m-%d-%Y")
    filename = f'cap-nature-organizers-scraped-{now}.csv'
    out_path = os.path.join(os.getcwd(), 'data', filename)
    if not os.path.exists(os.path.join(os.getcwd(), 'data')):
        os.mkdir(os.path.join(os.getcwd(), 'data'))
    with open(out_path,
              mode = 'w',
              encoding = 'utf-8',
              errors = 'ignore') as f:
        writer = csv.writer(f)
        _organizers = ['Event Organizer Name(s) or ID(s)']
        _organizers.extend(list(unique_organizers))
        organizers_to_write = _organizers
        for org in organizers_to_write:
            writer.writerow([org])
    if not is_local and bucket:
        s3 = boto3.resource('s3')
        s3.meta.client.upload_file(out_path,
                                   bucket,
                                   'capital-nature/{0}'.format(filename)
                                    )

class ScrapeReport():
    
    def __init__(self, scrape_file):
        self.scrape_file = scrape_file
        log_file = ScrapeReport.get_log_file(scrape_file)
        self.log_df = pd.read_csv(log_file)
        self.scrape_df = pd.read_csv(scrape_file)
        reports_dir = os.path.join(os.getcwd(),'reports')
        if not os.path.exists(reports_dir):
            os.mkdir(reports_dir)
        now = datetime.now().strftime("%m-%d-%Y")
        self.report_path= os.path.join(reports_dir, f'scrape-report-{now}.csv')

    @staticmethod
    def get_log_file(scrape_file):
        base = os.path.basename(scrape_file)
        date_index = re.search(r'\d', base).start()
        scrape_date = base[date_index:]
        for f in os.listdir(os.path.join(os.getcwd(), 'logs')):
            if f.endswith('.csv'):
                f_base = os.path.basename(f)
                date_index = re.search(r'\d', f_base).start()
                log_date = f_base[date_index:]
                if log_date == scrape_date:
                    return os.path.join(os.getcwd(), 'logs', f)

    @staticmethod
    def prep_log_df(log_df):
        err_type_count_by_source = pd.DataFrame(log_df.groupby(
            by=['Event Source', 'Level'])['Time'].count()).reset_index()
        err_type_count_by_source.columns = ['Event Organizers', 'Error Level', 'Number of Errors']
        err_df = err_type_count_by_source.pivot(
            index='Event Organizers',columns='Error Level', values='Number of Errors').reset_index()
        
        return err_df   
    
    @staticmethod
    def prep_scrape_df(scrape_df):
        source_count = pd.DataFrame(scrape_df.groupby(
            by='Event Organizers')['Event Name'].count()).reset_index()
        source_count.columns = ['Event Organizers', 'Number of Events Scraped']
    
        return source_count

    @staticmethod
    def get_status(row):
        '''statuses can include
            # - broken
            #   - a single CRITICAL error
            #   - any presence in the logs AND no events found
            # - operational
            #   - events found and no errors
            # - operational but with errors
            #   - events found and at least one non-critical error
            # - operational but no events found
            #   - no errors and no events for the event source
        '''
        is_logged = row['Number of Errors']
        n_events = row['Number of Events Scraped']
        try:
            n_crit = row['CRITICAL']
        except KeyError:
            n_crit = 0
        if n_crit >= 1:
            return 'Broken'
        elif is_logged and not n_events:
            return 'Broken'
        elif not is_logged and n_events:
            return 'Operational'
        elif is_logged and n_events:
            return 'Operational, but with errors'
        else:
            raise Exception ("this shouldn't happen!")
    
    @staticmethod
    def append_nonevents(report_df):
        event_organizers = report_df['Event Organizers'].tolist()
        data = [report_df]
        n_err_cols = len(report_df.columns) - 4
        for _,v in event_source_map.items():
            if v not in event_organizers:
                new_row = [v, 0]
                for _ in range(n_err_cols):
                    new_row.append(0)
                new_row.extend([0, 'Operational, but no events found'])
                
                _df = pd.DataFrame(new_row).transpose()
                _df.columns = report_df.columns
                data.append(_df)

        df = pd.concat(data, axis=0).fillna(0)

        return df

    def make_scrape_report(self):
        '''Create an excel report based on data scraped and the logs'''
        err_df = ScrapeReport.prep_log_df(self.log_df)
        source_count = ScrapeReport.prep_scrape_df(self.scrape_df)
        report_df = pd.merge(source_count, err_df, how='outer')
        err_cols = [x for x in report_df.columns if x in ['CRITICAL', 'ERROR', 'WARNING']]
        if not err_cols:
            report_df['Number of Errors'] = 0
        else:
            report_df['Number of Errors'] = report_df[err_cols].sum(axis=1)
        report_df['Status'] = report_df.apply(ScrapeReport.get_status, axis=1)
        df = ScrapeReport.append_nonevents(report_df)
        df.to_csv(self.report_path, index=False)

        return df

def make_reports(events, is_local, bucket):
    scrape_file = events_to_csv(events, is_local, bucket)
    organizers_to_csv(events, is_local, bucket)
    venues_to_csv(events, is_local, bucket)
    sr = ScrapeReport(scrape_file)
    sr.make_scrape_report()
    