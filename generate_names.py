import datetime
import subprocess

LOG_FILE="greg.log"
LOG= open(LOG_FILE, 'a+')

def logIt(msg):
	LOG.write(str(datetime.datetime.now()) + ": " + str(msg) + "\n")
	print(str(datetime.datetime.now()) + ": " + str(msg) )
	LOG.flush()

# Call with exact 10 names
def genereateXml(names):
	ts = datetime.datetime.today()
	g1 = "Merry"
	g2 = "Christmas"
	if ts.month == 1 or (ts.month == 12 and ts.day > 26):
		g1 = "Happy"
		g2 = "New Year"
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
	nB = names.pop(0)
	nC = names.pop(0)
	nD = names.pop(0)
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
				line = line.replace("%NAMEB%", nB)
				line = line.replace("%NAMEC%", nC)
				line = line.replace("%NAMED%", nD)
				line = line.replace("%GREET1%", g1)
				line = line.replace("%GREET2%", g2)
				f_out.write(line)
	logIt("XML Complete");

def generateSeq():
	subprocess.call(["xLights", "-r", "Wish_Name.xml"])
	logIt("SEQ Complete");

def sendSeq():
	subprocess.call(["rsync", "-av",  "Wish_Name.fseq", "fpp@192.168.1.150://mnt/greg/fpp/sequences"])
	logIt("Rsync complete")

if __name__ == "__main__":
        baseNames = ['BRODY', 'EMILY', 'MATT', 'WILL', 'JULIA', 'SOPHIE', 'LONDON', 'MAX', 'BENNY', 'LUIS', 'KORIE', 'MARY', 'GREG', 'NANCY', 'JERRY', 'JIM', 'JEFF', 'ANGIE', 'DON', 'MAGGIE']
        genereateXml(baseNames)
        generateSeq()
        sendSeq()
