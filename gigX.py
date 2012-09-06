
# This module contains two classes. job_post and job_post list.
# They are meant to parse craigslist. posts



import os, re
import feedparser, urllib2
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import sqlite3


class job_post(object):

    def __init__(self, link, title, description, date, summary):
        self.link = link
        self.title = title
        self.description = description
        self.date = date
        self.summary = summary
        
    
    # get return email address from current job post
    def get_post_email(self):
        
        try:
            url_page = urllib2.urlopen(self.link)
            url_data = url_page.read()
            url_page.close()
            
            html_to_parse = BeautifulSoup(url_data)

            mail = html_to_parse.find(href=re.compile("mailto*"))

            email = mail.contents
            
        except:
            print "Post [%s] doesn't display e-mail" % self.title
            return None

        return email[0]
    
    def make_notification(self):
        
        if self.get_post_email() != None:
            return "\r\nTitle: %s \nLink %s \nEmail: %s \nPost Date: %s \n Summary: %s \n\n Email has been sent" % (
                self.title, self.link, self.get_post_email(), self.date, self.summary)
                
        else: 
            return "\r\nTitle: %s \nLink %s \nEmail: %s \nPost Date: %s \n Summary: %s \n\n Doesn't Display" % (
                self.title, self.link, "Email Not Displayed", self.date, self.summary)
        

       
    def notify(self):
        try:
            msg = MIMEText(self.make_notification())
        except:
            print "Can't encode [%s] into emil retrying..." % self.title
            utf_8_encoded_msg = self.make_notification().encode('UTF-8')
            msg = MIMEText(utf_8_encoded_msg)
            print "success"


        if self.get_post_email() != None:
            msg['Subject'] = "Email sent to %s "% self.title
        else:
            msg['Subject'] = "%s doesn't display email "% self.title
        
        msg['From'] = 'Dyrodesign <contact@dyrodesign.com>'
        msg['To'] = 'hersheleh@gmail.com'

        mailserver = smtplib.SMTP('mail.dyrodesign.com')
        mailserver.login('contact@dyrodesign.com','6WAnKzsdE4w4Y2R4ng9p')
        mailserver.sendmail('contact@dyrodesign.com',
                            ['standyro@gmail.com',
                             'hersheleh@gmail.com'],
                            msg.as_string())
        mailserver.close()

        

    def send_email(self, mime_text):

        msg = mime_text
        
        mailserver = smtplib.SMTP('mail.dyrodesign.com')
        mailserver.login('contact@dyrodesign.com','6WAnKzsdE4w4Y2R4ng9p')
        mailserver.sendmail('contact@dyrodesign.com',
                            [self.get_post_email()],
                            msg.as_string())
        mailserver.close()

    

class job_post_list(object):
    
    def __init__(self, rss_link):
        self.posts = self.set_posts_from_feed(rss_link)
        self.sent_emails = []
        
    def set_posts_from_feed(self, link):
        feed = feedparser.parse(link)
        feed_items = []
        for item in feed["items"]:
            feed_items.append(
                job_post(
                    item["link"],
                    item["title"],
                    item["description"],
                    item["date"],
                    item["summary"]))
                
        return feed_items
        
    
    def find_keyword(self, keyword):
        
        matches = []

        for post in self.posts:
            if keyword.lower() in post.title.lower():
                matches.append(post)
                
        return matches
           
    
    def send_notification(self, relevant_posts):
        
        raw_text = ""
        for post in relevant_posts:
            raw_text = raw_text +"\n" + post.make_notification()
        
        
        msg = MIMEText(raw_text)
        msg['Subject'] = "Just a Test"
        msg['From'] = 'grisha@dyrodesign.com'
        
        
        mailserver = smtplib.SMTP('mail.dyrodesign.com')
        mailserver.login('grisha@dyrodesign.com','ttywXdOPd7gxa0HIzgJA')
        mailserver.sendmail('grisha@dyrodesign.com',
                            ['standyro@gmail.com',
                             'hersheleh@gmail.com'],
                            msg.as_string())
     

    def fetch_emails(self):

        current_dir = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(os.path.join(current_dir, 'gigX.db'))

        db = conn.cursor()

        raw = db.execute("select email from job_data")

        data = raw.fetchall()
        emails = []
        for item in data:
            emails.append(item[0])
            
        return emails

        
    def send_emails(self, relevant_posts):
        self.sent_emails = self.fetch_emails()
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html = open(os.path.join(current_dir,'dyrodesign-email.html'))
        html_email = html.read()
        html.close()

        msg = MIMEText(html_email, 'html')

        msg['From'] = "Dyrodesign <contact@dyrodesign.com>"
        msg['Bcc'] = 'standyro@gmail.com, hersheleh@gmail.com'
        
        for post in relevant_posts:
            if post.get_post_email() != None:
                if post.get_post_email() in self.sent_emails:
                    print "[%s] has already recieved an email" % post.title
                    pass
                else:
                    del msg['To']
                    del msg['Subject']
                    msg['To'] = post.get_post_email()
                    msg['Subject'] ="%s %s" % (u"\u2605" , post.title) 
                    post.send_email(msg)
                    post.notify()
                    print "Sent email to [%s]" % post.title
                    
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    conn = sqlite3.connect(os.path.join(current_dir, 'gigX.db'))

                    db = conn.cursor()
                    db.execute("insert into job_data(title, email, date) values(?,?,?)", 
                               [post.title, post.get_post_email(), post.date])
                    conn.commit()



if __name__ == '__main__':

    print "Gig X has started ...\n"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    raw = open(os.path.join(current_dir,'craigslist-california-list.txt'))
    california_str = raw.read()
    
    california_list = california_str.split("\n")
    
    for city in california_list:
        print "Parsing %s feed" % city
        rss_link = "http://%s.craigslist.org/cpg/index.rss" % city
        computer_gigs =  job_post_list(rss_link)
    
        website_posts = computer_gigs.find_keyword("website")
        webdesigner = computer_gigs.find_keyword("web designer")

        computer_gigs.send_emails(webdesigner)
        computer_gigs.send_emails(website_posts)
    
        
    print "Gig X has ended\n"
