#Silvr
[![Build Status](https://travis-ci.org/SilverWingedSeraph/silvr.svg?branch=master)](https://travis-ci.org/SilverWingedSeraph/silvr)

Silvr is a simple but powerful Python/Flask blogging platform designed for developers to customize for their customers.
It allows users to write posts and store them in a SQLite3 database, and display them to the web at large. You, as a
developer, can quickly edit the theme, add functionality, or even entirely change

Planned features include a simple setup script, multiple users, and themeing.

### How to Use:

Currently, setting up a Silvr site requires running this in a Python 3 console in the silvr directory:

```
>>> import silvr
>>> silvr.init_db()
```

Then, go ahead and copy config.py.example into config.py and set up your config. Remember to CHANGE THE PASSWORD.