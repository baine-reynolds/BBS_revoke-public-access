__author__ = "Michael Walker"
__email__ = "michaelchwalker@gmail.com"

import requests   #Dependency  http://docs.python-requests.org/en/master/
import getpass, json
from optparse import OptionParser

class Vars():
	source_url=""
	admin_username=""
	admin_password=""
	headers={'X-Atlassian-Token': 'no-check', "Content-type": "application/json"}
	api_session=None

class ServerConnections:
	def get_api(Vars, endpoint_url, params):
		try:
			r = Vars.api_session.get(endpoint_url, params=params, headers=Vars.headers)
		except requests.exceptions.SSLError:
			r = Vars.api_session.get(endpoint_url, params=params, headers=Vars.headers, verify=False)
		return r

	def put_api(Vars, endpoint_url, payload=""):
		try:
			r = Vars.api_session.put(endpoint_url, headers=Vars.headers, json=payload)
		except requests.exceptions.SSLError:
			r = Vars.api_session.put(endpoint_url, headers=Vars.headers, json=payload, verify=False)
		return r


def parse_input():
    '''
    Reads in attributes during run time and sets usage flags appropriately.
    '''
    parser = OptionParser()
    parser.add_option('-a', '--all', dest='revoke_all', default=False, action="store_true", help="Revoke public access from all projects and repositories.")
    options, args = parser.parse_args()
    return options, args

def get_creds():
	Vars.source_url = input("Enter URL of Bitbucket instance:\n")
	Vars.admin_username = input("Enter admin username:\n")
	Vars.admin_password = getpass.getpass("Enter Admin password:\n")
	Vars.api_session = requests.Session()
	Vars.api_session.auth = (Vars.admin_username, Vars.admin_password)
	return Vars

def parse_input():
	#Example based on "input.in" input file
	with open("input.in","r") as infile:
		contents_list = infile.readlines()
		parsed_list = []
		for line in contents_list:
			# removes any whitespace or linebreaks
			cleaned_1 = line.strip()
			# removes space character if present. Example "project-key, repo-slug" to "project-key,repo-slug"
			cleaned_2 = cleaned_1.replace(" ","")
			# converts "projectkey-,repo-slug" to ["project", "repo"] 
			split = cleaned_2.split(',')
			parsed_list.append(split)
	print("Parsed input list to:\n")
	print(parsed_list)
	print("\n\n")
	return parsed_list

def test_project(input_line, Vars, paged_start=None, paged_limit=None):
	params = {'start': paged_start, 'limit': paged_limit}
	endpoint_url = Vars.source_url + '/rest/api/1.0/projects/' + input_line[0]
	r = ServerConnections.get_api(Vars, endpoint_url, params)
	r_data = r.json()
	return r_data['public'] # True if public, False if private

def switch_inherited_access_to_individual(input_line, Vars):
	# Marking this specific project as private and all sub-repos as public to mirror original config
	Vars.project_key = input_line[0]
	payload = {'public': 'False'}
	endpoint_url = Vars.source_url + '/rest/api/1.0/projects/' + Vars.project_key
	print("Setting project '"+Vars.project_key+"'' as private.")
	r = ServerConnections.put_api(Vars, endpoint_url, payload) # revoke project public access
	print("Status: " + str(r.status_code))
	for repo in get_repos(Vars):
		payload = {"public": "True"} # set public access on each repo, mimicing the original access patterns
		endpoint_url = Vars.source_url + '/rest/api/1.0/projects/' + Vars.project_key + "/repos/" + Vars.repo_slug
		print("Setting repo '"+Vars.repo_slug+"'' within project '"+Vars.project_key+"' as public to mimic original settings.")
		r = ServerConnections.put_api(Vars, endpoint_url, payload)
		print("Status: " + str(r.status_code))

def get_repos(Vars, paged_start=None, paged_limit=None):
	while True:
		params = {'start': paged_start, 'limit': paged_limit}
		endpoint_url = Vars.source_url + '/rest/api/1.0/projects/' + Vars.project_key + '/repos'
		r = ServerConnections.get_api(Vars, endpoint_url, params)
		r_data = r.json()
		for repo_json in r_data['values']:
			Vars.repo_name = repo_json['name']
			Vars.repo_slug = repo_json['slug']
			Vars.repo_public = repo_json['public']
			yield Vars
		if r_data['isLastPage'] == True:
			return
		paged_start = r_data['nextPageStart']

def revoke_public_access(input_line, Vars):
	project_key = input_line[0]
	repo_slug = input_line[1]
	headers = {'X-Atlassian-Token': 'no-check', "Content-type": "application/json"}
	payload = {"public": "False"}
	endpoint_url = Vars.source_url + "/rest/api/1.0/projects/" + project_key + "/repos/" + repo_slug
	print("Revoking public access to project '"+project_key+"', repo '"+repo_slug+"'")
	r = ServerConnections.put_api(Vars, endpoint_url, payload)
	print("Status: "+str(r.status_code))

def main():
	options, args = parse_input()
	get_creds()
	if options.revoke_all == True:
		
	else:
		input_list = parse_input()
		for input_line in input_list:
			if test_project(input_line, Vars) == True:  # True if public, False if private
				switch_inherited_access_to_individual(input_line, Vars)
			# after marking the project as private and the repos to public (if necessary), mark the inputed repos as private
			revoke_public_access(input_line, Vars)

if __name__ == "__main__":
	main()