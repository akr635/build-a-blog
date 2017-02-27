#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainPage(Handler):
    def render_front(self, posts=""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")

        self.render("main.html", posts = posts)

    def get(self):
        self.render_front("main.html")



class NewPost(Handler):
    def render_entry(self, title="", body="", error=""):
        self.render("post.html", title = title, body = body, error = error)

    def get(self):
        self.render("post.html")

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            p = Post(title = title, body = body)
            p.put()

            self.redirect("/")
        else:
            error = "Please enter both a Title and Body."
            self.render_entry(title, body, error)

class ViewPost(Handler):
    def get(self, id):
        id = int(id)
        post = Post.get_by_id(id)
        self.render("permalink.html", id = id, post = post)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/post/<id:\d+>', ViewPost)
], debug=True)
