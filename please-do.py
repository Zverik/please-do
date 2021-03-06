#!/usr/bin/env python
import sys, os, json, urllib2, smtplib
from email.mime.text import MIMEText
import config

STATE_FILE = os.path.join(os.path.dirname(__file__), 'last_date.txt')


def filter_issue(issue, last_date):
        if 'pull_request' in issue:
            return False
        if issue['created_at'] <= last_date:
            return False
        if issue['comments'] > 0:
            return False
        return True


def prepare_message(issue):
    return '{0}\n\n--\n{1}\nForwarded with please-do.py'.format(issue['body'].encode('utf-8'), issue['html_url'])


def notify(issue):
    msg = MIMEText(prepare_message(issue), _charset='utf-8')
    msg['To'] = '{0} <{1}>'.format(config.GITHUB_PROJECT, config.EMAIL_TO)
    msg['From'] = '{0} <{1}>'.format(issue['user']['login'], config.EMAIL_FROM)
    msg['Subject'] = '{0} (#{1})'.format(issue['title'].encode('utf-8'), issue['number'])

    s = smtplib.SMTP(config.SMTP_SERVER)
    if config.SMTP_TLS:
        s.starttls()
    if config.SMTP_LOGIN:
        s.login(config.SMTP_LOGIN, config.SMTP_PASSWORD)
    s.sendmail(config.EMAIL_FROM, config.EMAIL_TO, msg.as_string())
    s.quit()


if __name__ == '__main__':
    try:
        with open(STATE_FILE, 'r') as f:
            last_date = f.read()
    except:
        last_date = None

    try:
        since_attr = '' if not last_date else 'since={0}'.format(last_date)
        resp = urllib2.urlopen('https://api.github.com/repos/{0}/issues?{1}'.format(config.GITHUB_PROJECT, since_attr))
        data = json.load(resp)
    except urllib2.HTTPError as e:
        print 'Fail:', e
        sys.exit(1)

    if not data:
        print 'No new data'
        sys.exit(0)

    max_date = ''
    for issue in data:
        if max_date < issue['updated_at']:
            max_date = issue['updated_at']
        if not filter_issue(issue, last_date):
            continue
        # Do not notify on the first run
        if last_date is not None:
            notify(issue)

    with open(STATE_FILE, 'w') as f:
        f.write(max_date)
