import os, re, traceback
import feedparser, urllib2
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import sqlite3
import sys


class job_post(object):

    def __init__(self, link, title, description, date, summary):
        self.link = link
        self.title = title
        self.description = description
        self.date = date
        self.summary = summary
        
    
    # get return email address from current job post

    def get_post_body(self):

        url_page = urllib2.urlopen(self.link)
    
        url_data = url_page.read()
        url_page.close()
        
        html_to_parse = BeautifulSoup(url_data)
        
        body = html_to_parse.find(id="userbody")

        return body
    

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
                self.title, self.link, self.get_post_email(), self.date, self.get_post_body())
                
        else: 
            return "\r\nTitle: %s \nLink %s \nEmail: %s \nPost Date: %s \n Summary: %s \n\n Doesn't Display" % (
                self.title, self.link, "Email Not Displayed", self.date, self.get_post_body())
        

       
    def notify(self):

        try:
            msg = MIMEText(self.make_notification(), 'html')
        except:
            print "Can't encode [%s] into emil retrying..." % self.title
            utf_8_encoded_msg = self.make_notification().encode('UTF-8')
            msg = MIMEText(utf_8_encoded_msg, 'html')
            print "success"


        if self.get_post_email() != None:
            msg['Subject'] = "Job posting - Email sent to %s "% self.title
        else:
            msg['Subject'] = "Job posting - %s doesn't display email "% self.title
        
        msg['From'] = 'Dyrodesign <stan@dyrodesign.com>'
        msg['To'] = 'standyro@gmail.com'

        mailserver = smtplib.SMTP('mail.dyrodesign.com')
        mailserver.login('stan@dyrodesign.com','S2t0a1n2#')
        mailserver.sendmail('stan@dyrodesign.com',
			    'standyro@gmail.com',
                            msg.as_string())
        mailserver.close()

        

    def send_email(self, mime_text):

        msg = mime_text
        
        mailserver = smtplib.SMTP('mail.dyrodesign.com')
        mailserver.login('stan@dyrodesign.com','S2t0a1n2#')
        mailserver.sendmail('stan@dyrodesign.com',
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
        msg['From'] = 'stan@dyrodesign.com'
        
        
        mailserver = smtplib.SMTP('mail.dyrodesign.com')
        mailserver.login('stan@dyrodesign.com','S2t0a1n2#')
        mailserver.sendmail('stan@dyrodesign.com',
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
        
        for post in relevant_posts:
            if post.get_post_email() != None:
                if post.get_post_email() in self.sent_emails:
                    try:
                        print "[ %s ] has already recieved an email" % post.title
                    except:
                        title_enc = post.title.encode('UTF-8')
                        print "[ %s ] is trying utf-8" % title_enc

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
    rss_link = sys.argv[1]
    print rss_link
    print "Gig X has started ...\n"
    print "we are testing now!!"
    try:
    	print "Parsing %s feed" % rss_link 
        computer_gigs =  job_post_list(rss_link)
	computer = computer_gigs.find_keyword("")
        computer_gigs.send_emails(computer)

    except Exception,e:
        print traceback.format_exc()
        print str(e)
        
    print "Gig X has ended\n"
