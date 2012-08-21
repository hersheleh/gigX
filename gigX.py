import feedparser, urllib2
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText


class job_post(object):

    def __init__(self, link, title, description, date, summary):
        self.link = link
        self.title = title
        self.description = description
        self.date = date
        self.summary = summary

    
    # get return email address from current job post
    def get_post_email(self):
        url_page = urllib2.urlopen(self.link)
        url_data = url_page.read()
        url_page.close()
        
        html_to_parse = BeautifulSoup(url_data)

        returnemail = html_to_parse.find(id="returnemail")
        email = returnemail.a.contents

        return email[0]
    
    def make_notification(self):
        
        return "\r\nTitle: "+self.title+"\nLink: "+self.link+"\nEmail: "+self.get_post_email()+"\nPost Date: "+self.date+"\n\n"
    
        
        
        



        


class job_post_list(object):
    
    def __init__(self, rss_link):
        self.posts = self.set_posts_from_feed(rss_link)


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
     
        



if __name__ == '__main__':
    
    rss_link = "http://losangeles.craigslist.org/cpg/index.rss"

    la_computer_gigs = job_post_list(rss_link)

    website_posts = la_computer_gigs.find_keyword("website")
    
    la_computer_gigs.send_notification(website_posts)

