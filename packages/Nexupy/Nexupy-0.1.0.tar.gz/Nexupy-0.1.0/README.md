# Nexufy
A simple Object Oriented Program to work with Sonatype Nexus REST API, planning to soon be turning into a py library.


# How To Use

```python
from nexupy.assets import Assets

# initialize the class
obj = Assets(base_url="nexus_url", repo_names=["npm-group", "docker-proxy"])

# authenticate into Nexus
obj.auth(username="nexus_username", password="nexus_password")

# choose what you want from the repositories. e.g last_downloaded of the packages
r = obj.last_downloaded()

# use write_to_file method to write the data to file
obj.write_to_file(data=str(r))

```
By default `write_to_file` method, creates a file called `data.txt` inside the directory that the gather.py is located in, so change it as you wish, by using `set_file_path` method or simply providing the path to your desired file using the `path` argument to the `write_to_file` method. 


# Contributions
All sorts of contributions are welcomed.

# TO-DO
- [ ] Implement Deletion

Copyright © 2024 Shayan Ghani shayanghani1384@gmail.com
