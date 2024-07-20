# Versions
![project](https://github.com/kaneryu/versions/actions/workflows/python-app.yml/badge.svg) [![codecov](https://codecov.io/github/KaneryU/versions/graph/badge.svg?token=YHXU7KB3PK)](https://codecov.io/github/KaneryU/versions)
### Don't use this, There's probably better solutions out there.

This is a simple class I use that stores a version number.

It can compare to other versions, and supports different release channels (alpha, beta, release). Alphas and Betas can have a number attached to them, for example 0.5.6-alpha2, or 1.6.0-beta3. Releases are indicated by a *lack* of a channel, and therefore can't have a number attached to them (1.0.0 is a Release).


It can also create "warnings" for versions that are too old, or too new. This is useful for when you want to warn users that they are using an old version of your software, or that they are using a version that is too new for the server to support.

The full list of features are avalable by reading the code. Trust me, it's simple.

I'm putting this into a package because I use it in multiple projects.