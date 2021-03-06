LawDigger
=========

Github for the legal world (at least, that was the idea).

The stack: MongoDB, Python, AngularJS, Zurb/Compass.

This project is tentatively abandoned.

The goal was to provide pleasant, Github-esque browsing of statutory changes over time.

The process, which is more or less implemented:

1. Scrape the web for the bodies of law in html (or PDF, depending on the version).
1. Parse the html/PDFs in Python, splitting up all the individual statutes.
1. Store each body of law in its own git repo, tagged (or possibly branched—I hadn't decided yet) by version (e.g., 2005, 2007, etc.), with each law in its own file in the repo.
1. Let the user diff arbitrary laws and versions, pulling the diffs from git and presenting them nicely.

The law-parsing logic is based on a series of regular expressions tailored to each body of law. [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) and [PDFBox](http://pdfbox.apache.org/) are used to extract text from html and PDFs.

Though I met with some initial success while testing and presenting the first few chapters of [Oregon Revised Statutes](http://www.leg.state.or.us/ors/), I got bogged down when trying to fine-tune the regexes to account for all the inconsistencies in the subsequent chapters' formatting.

Ultimately, due to the number of those inconsistencies, I decided that I could not guarantee the accuracy that legal professionals would require when reading the law.

(Plus, it just became a huge headache.)

I don't intend to finish this project, though I'd like to get it back to screenshot-worthy status.
