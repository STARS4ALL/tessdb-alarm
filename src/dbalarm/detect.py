#--------------------
# System wide imports
# -------------------
import re
import ssl
import email
import logging
import smtplib
import datetime
import traceback

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ---------------------
# Thrid-party libraries
# ---------------------

import decouple

# -----------------------
# Module global variables
# -----------------------

TSTAMP_SESSION_FMT = '%Y-%m-%dT%H:%M:%S%z'

log = logging.getLogger(__name__)

RE = re.compile( r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{4}) \[dbase#info\] DB Stats Readings \[Total, OK, NOK\] = \(0, 0, 0\)$" )

# ------------------
# Auxiliar functions
# ------------------

# Adapted From https://realpython.com/python-send-email/
def email_send(subject, body, sender, receivers, host, port, password, confidential=False):
    msg_receivers = receivers
    receivers = receivers.split(sep=',')
    message = MIMEMultipart()
    message["Subject"] = subject
    # Create a multipart message and set headers
    if confidential:
        message["From"] = sender
        message["To"]   = sender
        message["Bcc"]  = msg_receivers
    else:
        message["From"] = sender
        message["To"]   = msg_receivers

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender, password)
        server.sendmail(sender, receivers, message.as_string())


def existing_detections(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT detected_at FROM alarms_t")
    return set([item[0] for item in cursor.fetchall()])

def insert_detections(connection, sequence):
    rows = [ {"detected_at": item} for item in sequence]
    cursor = connection.cursor()
    cursor.executemany("INSERT INTO alarms_t (detected_at) VALUES (:detected_at)",rows)
    connection.commit()

def update_alarms_state(connection):
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).strftime(TSTAMP_SESSION_FMT)
    row = {"notified_at": now}
    cursor = connection.cursor()
    cursor.execute("UPDATE alarms_t SET notified_at = :notified_at WHERE notified_at IS NULL",row)
    connection.commit()

def count_not_notified(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT count(*) FROM alarms_t WHERE notified_at IS NULL")
    return cursor.fetchone()[0]

def not_notified(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT detected_at FROM alarms_t WHERE notified_at IS NULL ORDER BY detected_at ASC")
    return [item[0] for item in cursor.fetchall()]


def handle_new_detections(connection, detections):
    existing = existing_detections(connection)
    difference = detections.difference(existing)
    if len(difference) > 0:
        log.info("Candidate detections: %d, In database already: %d", len(detections), len(existing))
        insert_detections(connection, difference)
        try:
            email_send(
                subject    = "[STARS4ALL] TESS Database Alarm !", 
                body       = "tessdb stopped writting measurements at:\n{}".format('\n'.join(sorted(difference))), 
                sender     = decouple.config("SMTP_SENDER"),
                receivers  = decouple.config("SMTP_RECEIVERS"),
                host       = decouple.config("SMTP_HOST"), 
                port       = int(decouple.config("SMTP_PORT")),
                password   = decouple.config("SMTP_PASSWORD"),
            )
        except Exception as e:
            log.error(f"Exception while sending email: {e}")
            log.critical(traceback.format_exc())
        else:
            # Mark success in database
            update_alarms_state(connection)
            log.info("Warning e-mail succesfully sent.")
    else:
        log.info("No new alarms to handle")

def handle_unsent_email(connection):
    if count_not_notified(connection) > 0:
        pending = not_notified(connection)
        try:
            email_send(
                subject    = "[STARS4ALL] TESS Database Alarm !", 
                body       = "tessdb stopped writting measurements at:\n{}".format('\n'.join(pending)), 
                sender     = decouple.config("SMTP_SENDER"),
                receivers  = decouple.config("SMTP_RECEIVERS"),
                host       = decouple.config("SMTP_HOST"), 
                port       = int(decouple.config("SMTP_PORT")),
                password   = decouple.config("SMTP_PASSWORD"),
            )
        except Exception as e:
            log.error(f"Exception while sending email: {e}")
            log.critical(traceback.format_exc())
        else:
            # Mark success in database
            update_alarms_state(connection)
            log.info("Pending e-mails succesfully sent.")


# ===================
# Module entry points
# ===================

def run(connection, options):
    log.debug("Executing command %s, subcomand %s with options %s", __name__, run.__name__, options)
    handle_unsent_email(connection)
    with open(options.file) as fd:
        lines = fd.readlines()
    detections = set()
    for line in lines:
        matchobj = re.match(RE, line)
        if matchobj:
            detections.add(matchobj.group(1))
    if detections:
        handle_new_detections(connection, detections)

   



