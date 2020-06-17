## Dependency
* Python 3
* [Requests Package](http://docs.python-requests.org/en/master/)

`
pip3 install requests --user
`

## Background
This Tool is for bulk revoking public access from any number of project/repos. The "parse_input" method expects the url to each repo on a seperate line. Review the "example.in" text file for example. The URL should be the FQDN to the repo, however, you can use just the URI to the repo as the parser looks for the "projects" and "repos" section of the URI and then looks for the following path object for the respective key and slug.

## Usage
1. Update the "example.in" file with the URLs or URIs to each repo (on seperate lines) that you wish to revoke public access to.
2. Run the public-access-config.py script - 
    `
    python3 public-access-config.py
    `
3. Enter url of Bitbucket environment, followed by any admin username and it's respective password when prompted.
4. Review printed output for confirmation of changes made.

(Optional)
1. Run the tool with the "-a" or "--all" flag to revoke all public permissions across all projects and all repositories, leaving nothing public
    `
    python3 public-access-config.py -a
    `
## Results
All projects marked as "public" will be set to private, and in turn, all repos that were originally public because of the project inheritance, will be set as public on an individual level. Once a base-line is achieved, it will read in the "example.in" file and mark those repos as private.
