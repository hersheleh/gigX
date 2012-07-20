import feedparser, urllib2
from bs4 import BeautifulSoup


class job_post(object):

    def __init__(self, link, title, description, date, summary):
        self.link = link
        self.title = title
        self.description = description
        self.date = date
        self.summary = summary


    def get_post_email(self):
        url_page = urllib2.urlopen(self.link)
        url_data = url_page.read()
        url_page.close()
        
        html_to_parse = BeautifulSoup(url_data)

        returnemail = html_to_parse.find("span","returnemail")
        email = returnemail.a.contents

        return email


    

        


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
        

    
