## How to define difficulty ?
## Factors considered
## Home : 50% increase over base case
## Away : 50% decrease over base case


import sys
from BeautifulSoup import BeautifulSoup
import urllib2
import re

class Team:

	homeDiffiPercent = 0.5
	awayDiffiPercent = -0.5

	def __init__(self, name, baseDiffi):
		self.name = name
		self.baseDiffi = baseDiffi
		self.homeDiffi = baseDiffi*(1+0.5)
		self.awayDiffi = baseDiffi*(1-0.5)

def getDiffiDict(prev_table_file):
	diffiDict = {}
	numTeams = 20
	for line in prev_table_file:
		if line == '\n':
			return diffiDict

		parts = line.split('\n')[0].split('.')
		teamName = parts[1]
		teamFinish = int(parts[0])

		baseDiffi = numTeams + 1 - teamFinish
		diffiDict[teamName] = Team(teamName,baseDiffi)
	return diffiDict

class TeamPosition:
	def __init__(self,name, position, played, won, draw, lost, goalsScored, goalsGiven, points):
			self.name = name
			self.position = position
			self.played = played
			self.won = won
			self.draw = draw
			self.lost = lost
			self.goalsScored = goalsScored
			self.goalsGiven = goalsGiven
			self.points = points

def getTeamPosition(line):

		namePart = line[0:26]
		statPart = line[26:len(line)]

		position,name = namePart.split('.')

		statPart1,statPart2 = statPart.split('-')
		played,won,draw,lost,goalsScored = statPart1.split()
		goalsGiven, points= statPart2.split()

		return TeamPosition(name.strip(), position.strip(), played.strip(), won.strip(), draw.strip(), lost.strip(), goalsScored.strip(), goalsGiven.strip(), points.strip())

def getCurrentDifficultyAndTable(diffi_dict):
		currentDifficultyDict = {}

		url = 'http://www.rsssf.com/tablese/eng2014.html'
		response = urllib2.urlopen(url)
		html = response.read()

		soup = BeautifulSoup(html)
		content = soup.pre.contents[0]

		lines = content.split('\n')
		table = []

		tableFilled = 0
		for line in lines:
			line = line.strip()
			if(line.startswith('Table:') or len(line) < 1 or line.startswith('-') or line.startswith('Round') or line.startswith('[')):
				if(len(table) > 0 and line.startswith('Round')):
					tableFilled = 1
				continue
			else:
				if (re.search('^[1-9]',line) is not None):
					#print(line)
					if tableFilled == 0:
						table.append(getTeamPosition(line))
				else:
					homeTeamName = line[0:14]
					homeTeamName = homeTeamName.strip()

					awayTeamName = line.split('-')[1][2:]
					awayTeamName = awayTeamName.strip()

					keys = diffi_dict.keys()
					awayTeam = None
					homeTeam = None
					for key in keys:
						if key.startswith(homeTeamName):
							homeTeam = diffi_dict[key]
						if key.startswith(awayTeamName):
							awayTeam = diffi_dict[key]

					if homeTeam.name in currentDifficultyDict:
						currentDifficultyDict[homeTeam.name] = currentDifficultyDict[homeTeam.name] + awayTeam.awayDiffi
					else:
						currentDifficultyDict[homeTeam.name] = awayTeam.awayDiffi

					if awayTeam.name in currentDifficultyDict:
						currentDifficultyDict[awayTeam.name] = currentDifficultyDict[awayTeam.name] + homeTeam.homeDiffi
					else:
						currentDifficultyDict[awayTeam.name] = homeTeam.homeDiffi

		return currentDifficultyDict,table



def main():
	prev_table_file = open(sys.argv[1])

	diffi_dict = getDiffiDict(prev_table_file)

	currentDiffi,table = getCurrentDifficultyAndTable(diffi_dict)

	final_table = ()
	perfIndex_file = open('perf_index.txt','w+')
	perfIndex_file.write('Position,Name,Points,PerformanceIndex\n')
	for teamPos in table:
		teamName = teamPos.name
		points = teamPos.points
		played = teamPos.played
		difficulty = currentDiffi[teamName]
		perfIndex = float(points)*float(difficulty)/float(played)
		perfIndex = "{:4.1f}".format(perfIndex)
		final_table = final_table + ((teamPos.position, teamName, points, perfIndex),)
		perfIndex_file.write(str(teamPos.position)+','+ str(teamName)+','+ str(points)+','+ str(perfIndex)+'\n')

if __name__ == '__main__':
    main()
