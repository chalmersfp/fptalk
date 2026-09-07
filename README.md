# FP Talk Webpage Generator

This project contains definitions of FP talks and the FP seminar talk website.
The website is generated using [Hugo](https://gohugo.io/), which creates static HTML and ICS files.
The process is entirely data driven, based on files in [talks/](talks).

## How to Add a Talk

A talk is added by creating a Markdown file in [talks/](talks).
A template for the expected file structure is available in [template.md](template.md).
The file's content is rendered as the talk abstract on the website.
Additionally, there is a header with metadata, which is used to additional information about the talk.
The header is written using the YAML configuration format and accepts the following fields:
- `speaker` - the name of the speaker.
  Markdown markup can be used to link to a speakers homepage or institution.
- `title` - the title of the talk. This field also supports Markdown.
- `place` - the room name.
  This is supposed to be a string field.
  If the room is just given as a number, quotes may need to be added.
- `date` - the date (and time) when the talk is happening.
  Suggested format is `yyyy-MM-dd HH:mm:ss`.
- `online` (optional) - a link to a zoom meeting. The default password is displayed automatically.
- `recording` (optional) - a link to a recording made of the talk.
- `duration` (optional) - the duration of the talk, which is used for the calendar entries.
  If no duration is given, generated calendar event will last 60 minutes.
- `links` (optional) - more data can be linked here, such as presentation slides, source code repositories or related papers.

The `links` attribute is supposed to contain a list of objects, 
each of which has its own attributes.
- `title` is used to set the display name for the link. This is what's displayed on the page.
- `url` is used to set an url to which the entry points to.
- `file` is an alternative to `url` for files that are hosted on this server.
  Here, just the filename has to be given, which must be the same as in the `static/files/` directory.

## How to Add Resources

Resources for a talk can either be hosted externally and referenced via the `url` attribute of a `link` object.
Or they can refer to locally hosted files.
These files have to be placed in the [static/files/](static/files) directory.
Every file in this directory will be served by the server (without the `static` prefix in the url).

## General Structure

The general structure is based on [Hugo](https://gohugo.io/), which is used to compile or host the server.
There is a docker image `hugomods/hugo:exts` available, which provides Hugo and required commands.

For a development environment, you can use the following command, to host a server locally on http://localhost:1313/ with live-reloading and a file watcher enabled.
This way, any changes to templates, talks or configurations will immediately be visible on the local server.

```sh
docker run --rm -it -p 1313:1313 -v "$PWD:/src" hugomods/hugo:exts server --source /src --bind 0.0.0.0 --buildFuture
```

To generate the static files only, the following command suffices.
It simply drops the expected file structure into the [public/](public) directory.

```sh
docker run --rm -it -v "$PWD:/src" hugomods/hugo:exts hugo --buildFuture --minify
```

Generally, this project follows the Hugo structure:
- `layouts/` contains templates which are applied to each Markdown file in the `talks` directory.
- Templates named `page` are a template that is applied to each talk file.
  There is one template to create the HTML website and one for the ICS calendar event definition.
- `baseof.html` contains the header and supporting HTML structure displayed on every site of this server.
- Templates named `home` are for the landing page.
  They are not applied to any data, but have access to all the talk pages.
  This is used to generate the list of upcoming and recent talks, as well as the main calendar which contains all talk events.
- `layouts/partials/` contains re-useable templates
  - [talk-row.html](layouts/partials/talk-row.html) contains HTML code to describe the representation of talks on the landing page or the archive view.
  - [talk-event.ics](layouts/partials/talk-event.ics) contains the ICS template used to represent talks in ICS files.
  - [ics-format](layouts/partials/ics-format) acts as a "function", and is applied to sanitize fields when creating ICS files, escaping special characters and stripping Markdown markup characters.
- `assets/` contains the SCSS files defining the page style.
- `talks/` contains all talk files.
  Each file is a Markdown file containing an abstract and metadata.
  These files are converted into HTML and ICS using templates.
- `hugo.toml` configures the server.

## Calendar Files

The talk descriptions are automatically converted into ICS files.
This makes it possible to simply import individual events into a calendar.
The homepage also provides a single ICS file over all talks, which can be subscribed to get all events.
This requires, however, that all talks get a unique id.
We use the **talk title as a unique id**.

Conversion happens automatically.
On the Hugo side, it requires some adaptations however:
- The ICS media type has to be registered, so that the files are correctly served in a test environment.
- `calendar` and `event` are registered as an output type, which makes it so that the `page.event` and `home.calendar` templates are instantiated.
  The `event` template is instantiated per individual talk.
  The `calendar` template is instantiated for all talks.
