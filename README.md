<p align="center">
  <img alt="Sevilla" src="https://user-images.githubusercontent.com/6868935/63655563-a5f11d00-c789-11e9-9e4c-225312a9d598.png" width="50%">
  <br/>
  <a href="https://travis-ci.org/federicotdn/sevilla"><img alt="Build status" src="https://travis-ci.org/federicotdn/sevilla.svg?branch=master"></a>
  <a href="https://heroku.com/deploy"><img alt="Heroku Deploy" src="https://img.shields.io/static/v1?label=heroku&message=deploy&color=blueviolet"></a>
  <a href="https://github.com/federicotdn/sevilla/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/federicotdn/sevilla"></a>
  <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

Sevilla is a self-hosted server application, which allows you to quickly write down notes on your mobile phone's (or desktop's) web browser to read them at another time.

Sevilla tries to be as lightweight as possible, and avoids adding any unecessary steps between having an idea or thought and writing it down. As a note is written, it is automatically sent to the server and persisted.

Sevilla doesn't aim to be a full-fledged notes management system, and therefore has a very limited set of features. The general idea is to use it as an "input" for new notes, and then later copy those notes to another place like [Org mode](https://orgmode.org/).

Other properties of the project include:

- Uses SQLite or PostgreSQL to store notes.
- Can be accessed from a mobile or desktop web browser.
- Works pretty well on slow connections (tested on EDGE).
- Can be used as a clipboard between devices.
- Has an option to hide notes (this acts as a soft delete).

## Screenshots
<p align="center">
  <img alt="Sevilla" src="https://user-images.githubusercontent.com/6868935/64915149-ef1d0700-d760-11e9-9c7d-8ee9c3bee664.gif" width="40%">
</p>

## License
Copyright © 2020 Federico Tedin.

Distributed under the GNU General Public License, version 3.
