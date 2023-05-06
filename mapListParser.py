import json,sys
if len(sys.argv) >=2:
    print("Please select maplist type:")
    print("1[NL] - Newline(maps are splitted with newline)\n2[MC] - MapChooser(maps.ini, maps are formatted for MapChooser Lite plugin)\nMaplist type: ")
    mltype = input()
    if int(mltype) < 1 or int(mltype)> 2:
        print("Invalid input.")
        exit(0);
        pass
    elif(int(mltype) == 1):
        file = open(sys.argv[1], 'r+', encoding="utf-8")
        lines = file.readlines()

        maps = []

        for line in lines:
            if not(line.replace("\n","").replace("\r","").replace(" ","") == ""):
                maps.append(line.replace("\n","").replace("\r","").replace(" ",""))

        fileCommands = open('maps.json','w+', encoding="utf-8")
        fileCommands.write(json.dumps(maps))
        fileCommands.close();
        print("Done.")
    elif(int(mltype) == 2):
        file = open(sys.argv[1], 'r+', encoding="utf-8")
        lines = file.readlines()
        maps = []
        for line in lines:
            if not line.startswith(";"):
                if not line.replace("\n","").replace("\r","").split(" ")[0] == "":
                    maps.append(line.replace("\n","").replace("\r","").split(" ")[0])

        fileCommands = open('maps.json','w+', encoding="utf-8")
        fileCommands.write(json.dumps(maps))
        fileCommands.close();
        print("Done.")