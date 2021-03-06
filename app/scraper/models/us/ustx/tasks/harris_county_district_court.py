"""Celery tasks for scraping data."""

import datetime
import requests

from app.scraper.models.us.ustx import HarrisCountyDistrictCourtScraper
from app.extensions import celery
from celery import chain
from dateutil.parser import parse


class ScrapeTaskBaseClass(celery.Task):
    """Scrape Task Base Class."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Error Handler."""
        # log the failure
        # use print(), as anything written to standard out/-err will be redirected to the logging system
        print('Task ID: {0} Error Type: {1} Error Message: {2} Error Traceback: {3}'.format(task_id,
                                                                                            exc.__class__.__name__,
                                                                                            str(exc),
                                                                                            einfo.traceback))


@celery.task(base=ScrapeTaskBaseClass)
def parse_disposition_data_by_date_task(isoformat_date):
    """Celery task to parse the downloaded disposition data file."""
    # convert isoformat_date back to datetime_obj
    datetime_obj = parse(isoformat_date)

    try:
        res = HarrisCountyDistrictCourtScraper().parse_disposition_data_by_date(datetime_obj)
        if res:
            date = datetime_obj.strftime('%Y-%m-%d')
            return date
    except EnvironmentError as err:
        # error reading the disposition data file or attribute names data file
        print("Error: Unable to read {} disposition data file".format(datetime_obj.strftime('%Y-%m-%d')))
    except Exception as err:
        # other error
        raise


@celery.task(base=ScrapeTaskBaseClass)
def download_disposition_report_by_date_task(isoformat_date):
    """Celery task to download the disposition data file."""
    # convert isoformat_date back to datetime_obj
    datetime_obj = parse(isoformat_date)

    try:
        res = HarrisCountyDistrictCourtScraper().download_disposition_report_by_date(datetime_obj)
        if res:
            date = datetime_obj.strftime('%Y-%m-%d')
            return date
    except requests.exceptions.HTTPError as err:
        # error requesting harris county website
        raise
    except requests.exceptions.RequestException as err:
        # error requesting harris county website
        raise
    except OSError as err:
        # file not found or error creating directory
        print("File Not Found: {} disposition data file".format(datetime_obj.strftime('%Y-%m-%d')))
    except Exception as err:
        # other error
        raise


@celery.task(base=ScrapeTaskBaseClass)
def delete_disposition_report_by_date_task(isoformat_date):
    """Celery task to delete the downloaded disposition data file."""
    # convert isoformat_date back to datetime_obj
    datetime_obj = parse(isoformat_date)

    try:
        res = HarrisCountyDistrictCourtScraper().delete_disposition_report_by_date(datetime_obj)
        if res:
            date = datetime_obj.strftime('%Y-%m-%d')
            return date
    except OSError as err:
        # unable to delete
        print("Error: Unable to delete {} disposition data file".format(datetime_obj.strftime('%Y-%m-%d')))
    except Exception as err:
        # other error
        raise


@celery.task(base=ScrapeTaskBaseClass)
def parse_filing_data_by_date_task(isoformat_date):
    """Celery task to parse the downloaded disposition data file."""
    # convert isoformat_date back to datetime_obj
    datetime_obj = parse(isoformat_date)

    try:
        res = HarrisCountyDistrictCourtScraper().parse_filing_data_by_date(datetime_obj)
        if res:
            date = datetime_obj.strftime('%Y-%m-%d')
            return date
    except EnvironmentError as err:
        # error reading the disposition data file or attribute names data file
        print("Error: Unable to read {} filing data file".format(datetime_obj.strftime('%Y-%m-%d')))
    except Exception as err:
        # other error
        raise


@celery.task(base=ScrapeTaskBaseClass)
def download_filing_report_by_date_task(isoformat_date):
    """Celery task to download the filing data file."""
    # convert isoformat_date back to datetime_obj
    datetime_obj = parse(isoformat_date)

    try:
        res = HarrisCountyDistrictCourtScraper().download_filing_report_by_date(datetime_obj)
        if res:
            date = datetime_obj.strftime('%Y-%m-%d')
            return date
    except requests.exceptions.HTTPError as err:
        # error requesting harris county website
        raise
    except requests.exceptions.RequestException as err:
        # error requesting harris county website
        raise
    except OSError as err:
        # file not found or error creating directory
        print("File Not Found: {} filing data file".format(datetime_obj.strftime('%Y-%m-%d')))
    except Exception as err:
        # other error
        raise


@celery.task(base=ScrapeTaskBaseClass)
def delete_filing_report_by_date_task(isoformat_date):
    """Celery task to delete the downloaded filing data file."""
    # convert isoformat_date back to datetime_obj
    datetime_obj = parse(isoformat_date)

    try:
        res = HarrisCountyDistrictCourtScraper().delete_filing_report_by_date(datetime_obj)
        if res:
            date = datetime_obj.strftime('%Y-%m-%d')
            return date
    except OSError as err:
        # unable to delete
        print("Error: Unable to delete {} filing data file".format(datetime_obj.strftime('%Y-%m-%d')))
    except Exception as err:
        # other error
        raise


def scrape_disposition_today_task():
    """Scrape today's disposition report."""
    today = datetime.datetime.today()

    task = chain(download_disposition_report_by_date_task.si(today),
                 parse_disposition_data_by_date_task.si(today),
                 delete_disposition_report_by_date_task.si(today)).apply_async()

    data = {
        "task_id": task.id,
        "date": today.strftime('%Y-%m-%d'),
        "msg": "Asynchronous task to scrape disposition report for today started with a task id of {}.".format(task.id)
    }
    return data


def scrape_filing_today_task():
    """Scrape today's filing report."""
    today = datetime.datetime.today()

    task = chain(download_filing_report_by_date_task.si(today),
                 parse_filing_data_by_date_task.si(today),
                 delete_filing_report_by_date_task.si(today)).apply_async()

    data = {
        "task_id": task.id,
        "date": today.strftime('%Y-%m-%d'),
        "msg": "Asynchronous task to scrape filing report for today started with a task id of {}.".format(task.id)
    }
    return data


def scrape_disposition_by_date_task(date='today'):
    """Scrape disposition report by date.

    date in format YYYY-MM-DD
    """
    if date == 'today':
        datetime_obj = datetime.datetime.today()
    else:
        datetime_obj = parse(date)

    task = chain(download_disposition_report_by_date_task.si(datetime_obj),
                 parse_disposition_data_by_date_task.si(datetime_obj),
                 delete_disposition_report_by_date_task.si(datetime_obj)).apply_async()

    data = {
        "task_id": task.id,
        "date": datetime_obj.strftime('%Y-%m-%d'),
        "msg": "Asynchronous task to scrape disposition report for today started with a task id of {}.".format(task.id)
    }
    return data


def scrape_filing_by_date_task(date='today'):
    """Scrape filing report by date.

    date in format YYYY-MM-DD
    """
    if date == 'today':
        datetime_obj = datetime.datetime.today()
    else:
        datetime_obj = parse(date)

    task = chain(download_filing_report_by_date_task.si(datetime_obj),
                 parse_filing_data_by_date_task.si(datetime_obj),
                 delete_filing_report_by_date_task.si(datetime_obj)).apply_async()

    data = {
        "task_id": task.id,
        "date": datetime_obj.strftime('%Y-%m-%d'),
        "msg": "Asynchronous task to scrape filing report for today started with a task id of {}.".format(task.id)
    }
    return data
