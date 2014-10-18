#!/usr/bin/env python

import datetime
import webapp2
import cgi
import os
import jinja2
import validator

from google.appengine.ext import ndb

chatterbox_key = ndb.Key('ChatterBox', 'default_chatterbox')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Message(ndb.Model):
    author = ndb.TextProperty()
    content = ndb.TextProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


def get_messages():
    return ndb.gql('SELECT * '
                    'FROM Message '
                    'WHERE ANCESTOR IS :1 '
                    'ORDER BY date DESC LIMIT 10',
                    chatterbox_key)


class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'messages': get_messages()
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class Messages(webapp2.RequestHandler):
    def get(self):
        self.redirect('/')

    def post(self):
        error_messages = []
        error_fields = []

        author = self.request.get('author')
        message = validator.author(author)
        if message:
            error_messages.append(message)
            error_fields.append('author')

        content = self.request.get('content')
        message = validator.content(content)
        if message:
            error_messages.append(message)
            error_fields.append('content')

        if len(error_messages):
            template_values = {
                'error_messages': error_messages,
                'error_fields': error_fields,
                'unsaved_message': {'author': author, 'content': content},
                'messages': get_messages()
            }

            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))
        else:
            message = Message(parent=chatterbox_key)
            message.author = author
            message.content = content
            message.put()
            self.redirect('/')



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/chat', Messages)
], debug=True)
