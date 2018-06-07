# GTK Tag Manager
A tag manager application written in GTK.

## Requirements
- Python 3
- Gtk 3
- Python-SQLAlchemy
- xdg-utils
- Python-Flask (only for the webserver)

## Usage

To start the browser use
```sh
./browser.py
``` 

To tag a file use:
```sh
./tag-file.py path/to/file
``` 

## REST API

The application includes a server with a REST API.
Start the server with
```sh
./server.py
``` 

## REST Documentation

### Get

To get the list of metatags, tags and files use
```sh
curl localhost:44659/api/1.0/metatags
curl localhost:44659/api/1.0/tags
curl localhost:44659/api/1.0/files
```


To get the tags associated with a file use
```sh
curl localhost:44659/api/1.0/files/1
```

To get the files associated with a tag use
```sh
curl localhost:44659/api/1.0/tags/1
```

### Insert

To insert a metatag execute a POST request
```sh
curl -X POST localhost:44659/api/1.0/metatags --data '{"name": "Content"}' --header 'Content-Type:application/json'
```
Response:
```sh
{"id": 1, "name": "Content"}
```

Same for tags:
```sh
curl -X POST localhost:44659/api/1.0/tags --data '{"name": "Useful", "metatag" : {"id": 1} }' --header 'Content-Type:application/json'
```
Response:
```sh
{"id": 1, "name": "Useful", "metatag": {"id": 1, "name": "Content"}}
```

And files:
```sh
curl -X POST localhost:44659/api/1.0/files --data '{"name": "Documents/dictionary.txt", "mime" : "plain/text" }' --header 'Content-Type:application/json'
```
Response:
```sh
{"id": 1, "mime": "plain/text", "name": "Documents/dictionary.txt"}
```

### Remove

To remove an entity execute a DELETE request
```sh
curl -X DELETE localhost:44659/api/1.0/metatags/1
curl -X DELETE localhost:44659/api/1.0/tags/1
curl -X DELETE localhost:44659/api/1.0/files/1
```

### Edit

To edit an entity execute a PUT request
```sh
curl -X PUT localhost:44659/api/1.0/tag/1 --data '{"name": "ContentRenamed"}' --header 'Content-Type:application/json'
```

### Add/Remove tag
To add a tag to a file execute a POST request
```sh
curl localhost:44659/api/1.0/files/1/tags --data '{"id": 2}' --header 'Content-Type:application/json'
```
To remove a tag to a file execute a DELETE request
```sh
curl -X DELETE localhost:44659/api/1.0/files/1/tags/2 --header 'Content-Type:application/json'
```
