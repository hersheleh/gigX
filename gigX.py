import os
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

            returnemail = html_to_parse.find(id="returnemail")

            email = returnemail.a.contents
        except:
            print "Post [%s] doesn't display e-mail" % self.title
            return None

        return email[0]
    
    def make_notification(self):
        
        return "\r\nTitle: "+self.title+"\nLink: "+self.link+"\nEmail: "+self.get_post_email()+"\nPost Date: "+self.date+"\n\n"
    

    def send_email(self):

        raw_text = self.make_notification()

        msg = MIMEText(raw_text)
        msg['Subject'] = "Craigslist notification"
        msg['From'] = 'grisha@dyrodesign.com'
        msg['To'] = 'standyro@gmail.com, hersheleh@gmail.com'
        
        
        mailserver = smtplib.SMTP('mail.dyrodesign.com')
        mailserver.login('grisha@dyrodesign.com','ttywXdOPd7gxa0HIzgJA')
        mailserver.sendmail('grisha@dyrodesign.com',
                            ['standyro@gmail.com',
                             'hersheleh@gmail.com'],
                            msg.as_string())

    

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
        msg['Subject'] = "These people want websites"
        msg['From'] = 'grisha@dyrodesign.com'
        msg['To'] = 'standyro@gmail.com, hersheleh@gmail.com'
        
        
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

        raw = db.execute("select emails from job_data")

        data = raw.fetchall()
        emails = []
        for item in data:
            emails.append(item[0])
            
        return emails

        
    def send_email(self, relevant_posts):
        self.sent_emails = self.fetch_emails()

        for post in relevant_posts:
            if post.get_post_email() != None:
                if post.get_post_email() in self.sent_emails:
                    print post.get_post_email()+" has recieved an email"
                    pass
                else:
                    post.send_email()
                    print "Sent email to %s" % post.get_post_email()

                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    conn = sqlite3.connect(os.path.join(current_dir, 'gigX.db'))

                    db = conn.cursor()
                    db.execute("insert into job_data(emails) values(?)", [post.get_post_email()])
                    conn.commit()



if __name__ == '__main__':

    print "Gig X has started ...\n"
    rss_link = "http://losangeles.craigslist.org/cpg/index.rss"


    la_computer_gigs = job_post_list(rss_link)

    website_posts = la_computer_gigs.find_keyword("website")
    webdesigner = la_computer_gigs.find_keyword("web designer")

    la_computer_gigs.send_email(webdesigner)
    la_computer_gigs.send_email(website_posts)
    print "Gig X has ended\n"
