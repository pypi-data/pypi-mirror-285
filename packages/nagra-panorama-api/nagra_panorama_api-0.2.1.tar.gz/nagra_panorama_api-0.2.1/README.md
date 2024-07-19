# README

This repository contains a wrapper around Panorama/PaloAlto API.
It also provides a cli tool: `panorama_api`.

Read the corresponding documentations:
* [CLI documentation](./CLI.md)
* [Library documentation](./Library.md)


## Why the need for this library ?

For simple resource retrieval, the existing API is enough, but:

* The libraries available are not practical for it, the manual management of urls is easier
* For more complex operation, this does not suits well

The [official python SDK of PaloAltoNetworks](https://github.com/PaloAltoNetworks/pan-os-python) itself relies on a [third party wrapper](https://github.com/kevinsteves/pan-python) for their API.


This library takes a more popular approach when wrapping the API, making it easier to use. It also provides types' wrappers to simplify their usage or utility functions to re-structure the data we receive.
It provides a client for the REST API and for the XML API

* A simple client for the API (JSON and XML)
* ~~Tool to manage the xml configuration~~


## TODO

* Improve the documentation
  * Re-organize the methods
  * Add type hints
  * Find a place to publish it (move the whole project on a **public** repository on Github?)
* Provide wrapper classes for the resources.

  ```python
  nat = NatPolicy(...)
  tree.insert(nat)  # or nat.insertInto(tree)
  client.create(nat.insert_xpath, nat.xml)
  ```
* # Mix Rest API and XML API ?
  https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-panorama-api/get-started-with-the-pan-os-rest-api/create-security-policy-rule-rest-api


## Links
* [Official upgrade procedure on HA with API](https://docs.paloaltonetworks.com/pan-os/9-1/pan-os-panorama-api/pan-os-xml-api-use-cases/upgrade-pan-os-on-multiple-ha-firewalls-through-panorama-api)
