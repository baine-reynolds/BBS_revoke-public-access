__author__ = "Michael Walker"

import requests   #Dependency  http://docs.python-requests.org/en/master/
import getpass, json

class Vars():
	source_url=""
	admin_username=""
	admin_password=""
	headers={'X-Atlassian-Token': 'no-check', "Content-type": "application/json"}
	api_session=None

def get_projects(Vars, paged_start=None, paged_limit=None):
	while True:
		params = {'start': paged_start, 'limit': paged_limit}
		endpoint_url = Vars.source_url + '/rest/api/1.0/projects'
		r = ServerConnections.get_api(Vars, endpoint_url, params)
		r_data = r.json()
		for project_json in r_data['values']:
			Vars.project_name = project_json['name']
			Vars.project_key = project_json['key']
			Vars.project_public = project_json['public']
			yield Vars
		if r_data['isLastPage'] == True:
			return
		paged_start = r_data['nextPageStart']

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
	#Needs to read in the file with the project/repo data of what needs to be revoked. See revoke_public_access() for example
	pass

def get_creds():
	Vars.source_url = input("Enter URL of Bitbucket instance:\n")
	Vars.admin_username = input("Enter admin username:\n")
	Vars.admin_password = getpass.getpass("Enter Admin password:\n")
	Vars.api_session = requests.Session()
	Vars.api_session.auth = (Vars.admin_username, Vars.admin_password)
	return Vars

def switch_inherited_access_to_individual(Vars):
	# when a project is public, revoke the public setting but set all repos to public to match same results
	# later we'll revoke public from the individual repos as necessary
	for project in get_projects(Vars):
		if Vars.project_public == True: # Set all sub repos as public, excluding the intended private repos
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

def revoke_public_access(Vars):
	# parse list of repos that need to have public access revoked
	list_of_repos = parse_input()
	# example:
	#list_of_repos = [["main", "primary"], ["fec", "repo1"], ["fec", "repo2"]] 
	for repo in list_of_repos:
		project_key = repo[0]
		repo_slug = repo[1]
		headers = {'X-Atlassian-Token': 'no-check', "Content-type": "application/json"}
		payload = {"public": "False"}
		endpoint_url = Vars.source_url + "/rest/api/1.0/projects/" + project_key + "/repos/" + repo_slug
		print("Revoking public access to project '"+project_key+"', repo '"+repo_slug+"'")
		r = ServerConnections.put_api(Vars, endpoint_url, payload)
		print("Status: "+str(r.status_code))

def main():
	get_creds()
	switch_inherited_access_to_individual(Vars)
	revoke_public_access(Vars)

if __name__ == "__main__":
	main()