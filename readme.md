## Dependency
* Python 3
* [Requests Package](http://docs.python-requests.org/en/master/)

`
pip3 install requests --user
`

## Background
This Tool is for bulk revoking public access from any number of project/repos. The "parse_input" method is blank, leaving it up to those who wish to use it to determine the best way to read in the data. The script expects that the data read in will result in a list, where each item is a list itself containing the project_key and repo_slug.

i.e. [ [ "project_key1", "repo_slug1" ] , [ "project_key2", "repo_slug2" ] , ... ]

## Usage
1. Run the public-access-config.py script - `
python3 public-access-config.py
`
2. Enter url of Bitbucket environment, followed by any admin username and it's respective password when prompted.
3. Review printed output for confirmation

## Results
All project "public" will be removed, and in turn, all repos that were originally public, will be set as public on an individual level. From there, *reads in list of repos to be revoked* (needs to be implemented by user), and then those repos will be marked as private.