import subprocess

# Call with exact 10 names
def genereateXml(names):
	n1 = names.pop(0)
	n2 = names.pop(0)
	n3 = names.pop(0)
	n4 = names.pop(0)
	n5 = names.pop(0)
	n6 = names.pop(0)
	n7 = names.pop(0)
	n8 = names.pop(0)
	n9 = names.pop(0)
	nA = names.pop(0)
	with open("Wish_Name.xml", "w+") as f_out:
		with open("Wish_Name_Template.xml") as f:
			for line in f:
				line = line.replace("%NAME1%", n1)
				line = line.replace("%NAME2%", n2)
				line = line.replace("%NAME3%", n3)
				line = line.replace("%NAME4%", n4)
				line = line.replace("%NAME5%", n5)
				line = line.replace("%NAME6%", n6)
				line = line.replace("%NAME7%", n7)
				line = line.replace("%NAME8%", n8)
				line = line.replace("%NAME9%", n9)
				line = line.replace("%NAMEA%", nA)
				f_out.write(line)
	print("XML Complete");

def generateSeq():
	subprocess.call(["xLights", "-r", "Wish_Name.xml"])
	print("SEQ Complete");

def sendSeq():
	subprocess.call(["rsync", "-av", "--bwlimit=1200", "Wish_Name.fseq", "fpp@192.168.1.150:/home/fpp/media/sequences"])
	print("Rsync complete")

if __name__ == "__main__":
        baseNames = ['BRODY', 'EMILY', 'MATT', 'WILL', 'JULIA', 'SOPHIE', 'LONDON', 'MAX', 'BENNY', 'LUIS', 'KORIE']
        genereateXml(baseNames)
        generateSeq()
        sendSeq()
