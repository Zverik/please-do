#!/usr/bin/env python
import sys, os, json, urllib2, smtplib
from email.mime.text import MIMEText
import config

STATE_FILE = os.path.join(os.path.dirname(__file__), 'last_date.txt')


def filter_issue(issue):
        if 'pull_request' in issue:
            return False
        if issue['created_at'] < last_date:
            return False
        if issue['comments'] > 0:
            return False
        return True


def prepare_message(issue):
    return '{0}\n\n--\n{1}'.format(issue['body'].encode('utf-8'), issue['url'])


def notify(issue):
    msg = MIMEText(prepare_message(issue), _charset='utf-8')
    msg['To'] = config.EMAIL_TO
    msg['From'] = config.EMAIL_FROM
    msg['Subject'] = 'New {0} issue: {1} (#{2})'.format(config.GITHUB_PROJECT, issue['title'].encode('utf-8'), issue['number'])

    print msg.as_string().decode('utf-8')
    return
    s = smtplib.SMTP(config.SMTP_SERVER)
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
        if not filter_issue(issue):
            continue
        notify(issue)

    with open(STATE_FILE, 'w') as f:
        f.write(max_date)
