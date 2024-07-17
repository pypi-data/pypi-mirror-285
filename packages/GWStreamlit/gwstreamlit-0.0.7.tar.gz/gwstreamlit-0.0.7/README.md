# GWStreamlit

## Overview

GWStreamlit is a Python package that provides a standardised streamlit interface for Guidewire applications. The user 
interface definition is defined in a yaml file and the package provides a streamlit interface to interact with 
the Guidewire application.

Use in other non Guidewire application is possible, but the package is designed to work with Guidewire applications and
any maintenance for Guidewire applications will be prioritised. This is not to say that any requests for enhancements 
will be ignored, quite the opposite.

## Installation

Installation is via pip, ensure that the latest version is installed. This requires Python 3.12 or later.

```bash
pip install gwstreamlit
```

## Usage

### GWStreamlit creation

GWStreamlit initalization requires an application name and either the name of the yaml file if the files are stored 
in resources/yaml_ui directory. Otherwise, the full path to the yaml file is required.

```python
def build():
    initalize(my_application, my_yaml_file_location)
```

Initialize creates an instance of the GWStreamlit class transferring the yaml file information to a pydantic model. The 
class instance is stored in the streamlit session state. This permits only a single instance of the GWStreamlit class to
exist at any one time. 

