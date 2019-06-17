# Item-Catalog
In this project WE create a flask web application that provides a list of items within a variety of categories. We use **Google Sign-In** and **OATH** for user registration and authentication. Registered users will have the ability to post, edit and delete items owned by them.

## Installing the Virtual Machine
 The required steps to setup the virtual machine can be in vm_setup.md

## Getting Started

1. Clone this repository by executing ``git clone https://github.com/binstub/item_catalog`` in your terminal window.
2. Obtain a Google CLIENT ID by following [this guide](https://developers.google.com/identity/sign-in/web/devconsole-project). Add ``https://localhost:5000`` to the javascript origins
3. Download the client secrets file from console and rename the file to ``client_secrets.json``. Copy this into same folder as Project(/vagrant)
4. I have hardcoded the client id in the HTML login page because of some problems I faced.
5. cd to /catalog directory or to the one where you have cloned the project
5. Run ``python database_setup.py`` to create an empty database with the name _itemcatelog.db_.
6. Run ``python populatedb.py`` to populate categories into db. You can add Items from the web page of the project.
7. Type ``application.py`` to start the server at [https://localhost:5000](https://localhost:5000)

## Usage

#### API End Points

1. View JSON of entire catalog: _/catalog/JSON_
2. View JSON of all categories: _/categories/JSON_
3. View JSON of particular item within a category: _/category/<int:category_id>/<int:item_id>/JSON_
4. View JSON of a single category: _/category/<int:category_id>/JSON_

#### HTML End Points

1. Landing Page, Show all Categories: _/_, _/catalog_
2. Show all Items within a Category: _/catalog/<category_name>/items_
2. Login Page: _/login_
4. Show detail page of an item: _/catalog/<category_name>/<item_name>_

## Authors

Bindu Govindaiah
