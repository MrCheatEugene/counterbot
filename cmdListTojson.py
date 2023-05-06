import json,sys

file = open(sys.argv[1], 'r+', encoding="utf-8")
lines = file.readlines()

commands = {}

for line in lines:
    decodedline = line.strip().split("-")
    commands[decodedline[0].replace(' ','').strip()] = [decodedline[1],decodedline[2].replace(' ','').strip()];

fileCommands = open('commands.json','w+', encoding="utf-8")
fileCommands.write(json.dumps(commands))
fileCommands.close()
