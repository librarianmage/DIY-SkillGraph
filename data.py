#!/usr/bin/env python
from __future__ import print_function
import requests, jq, json

# Filters used in jq

def ach(skill):
        return ".response | [.[] | {id, skill:{}, title, short, description, stats, meta, image: .image.web_460}]".format(skill)

FILTERS = {
    'skills': ".response|[.[]|{id, url, title, description, position, image: (\"https:\" + .images.medium), grammar, pole, color, notes}]",
    'combine': ".[0] + .[1]",
    'skillList': "[.[].url]",
    'challenge': ach
}

# Parameters for requests
PARAMS = {
    'skills': {
        'limit': 150,
        'offset': 0 },
    'challenges': {
        'limit': 20,
        'offset': 0 }
}

# URLs for requests
BASEURL = "https://api.diy.org/"
URLS = {
    'skills': 'skills/',
    'challenges': 'skills/{}/challenges/'
}

def diyUrl(skill = ''):
    if skill == '':
        return BASEURL + URLS['skills']
    else:
        return BASEURL + URLS['challenges'].format(skill)

data = {}

# Request Skill Data
print("Getting Skill Data...", end = ' ')
rawSkillsData = requests.get(diyUrl(), params=PARAMS['skills'])
print("Done.")

# Get Skill JSON and check length
rawSkillJSON = rawSkillsData.json()
if len(rawSkillJSON['response']) == PARAMS['skills']['limit']:
    print("WARN: JSON has length of {}, may want to increase?".format(PARAMS['skills']['limit']))
else:
    print("JSON items: {0} out of {1}, {2} left".format(len(rawSkillJSON['response']), PARAMS['skills']['limit'], PARAMS['skills']['limit']-len(rawSkillJSON['response'])))

# Filter Skill JSON (list) and add to data (dict)
print("Filtering Skill Data...", end = ' ')
skillData = jq.jq(FILTERS['skills']).transform(rawSkillJSON)
data['skills'] = skillData
print("Done.")

# Filter Skill JSON to get skill names
print("Getting list of Skills...", end = ' ')
skills = jq.jq(FILTERS['skillList']).transform(skillData)
print("Done.")

# For each skill, grab challenge list, check length, filter, add to data (dict)
print("Getting challenge data...")
data['challenges'] = {}
for skill in skills:
    # Get achievements
    print("\tSkill: {}...".format(skill), end=' ')
    rawChallengeData = requests.get(diyUrl(skill), params=PARAMS['challenges'])
    print("Done.")