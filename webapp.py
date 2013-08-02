#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lawdiffs import webapp
from lawdiffs.data.client import mongoengine_connect
app = webapp.app


def main():
    mongoengine_connect()
    app.run(port=webapp.PORT, host=webapp.HOST)


if __name__ == "__main__":
    main()
