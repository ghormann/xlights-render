import datetime
import subprocess

LOG_FILE="greg.log"
LOG= open(LOG_FILE, 'a+')

def logIt(msg):
	LOG.write(str(datetime.datetime.now()) + ": " + str(msg) + "\n")
	print(str(datetime.datetime.now()) + ": " + str(msg) )
	LOG.flush()

def generateBirthday(nameString):
	filename = "Happy_Birthday_name.xsq"
	seqName = "Happy_Birthday_name.fseq"
	g1="Happy Birthday"
	g2="Happy Birthday"
	with open("name_list.txt", "w") as f_out:
        	f_out.write(nameString)

	with open(filename, "w+") as f_out:
		with open("Happy_Birthday_Name_Template.xsq") as f:
			for line in f:
				line = line.replace("%GREET1%", g1)
				line = line.replace("%GREET2%", g2)
				f_out.write(line)
	# Run xLights
	subprocess.call(["xLights", "-r", filename])
	sendSeqName(seqName)

# Call with a long string of names
def genereateMidnightXml(nameString):
	ts = datetime.datetime.today()
	g1 = "Merry"
	g2 = "Christmas"
	if ts.month == 1 or (ts.month == 12 and ts.day > 26):
		g1 = "Happy"
		g2 = "New Year"
	logIt(f"Genereating Midnight with {g1} {g2}")
	with open("name_list.txt", "w") as f_out:
        	f_out.write(nameString)

	with open("wish_long_name.xsq", "w+") as f_out:
		with open("wish_long_template.xsq") as f:
			for line in f:
				line = line.replace("%GREET1%", g1)
				line = line.replace("%GREET2%", g2)
				f_out.write(line)

	logIt("Midnight XML Complete");

# Call with exact 13 names
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
	with open("Wish_Name.xsq", "w+") as f_out:
		with open("Wish_Name_Template.xsq") as f:
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

def getFileName(midnight, isSeq):
	name = "Wish_Name.xsq"
	if midnight:
		name = "wish_long_name.xsq"

	if isSeq:
		name = name.replace(".xsq", ".fseq")
	return name

def generateSeq(midnight = False):
	name = getFileName(midnight, False)
	subprocess.call(["xLights", "-r", name])
	logIt("SEQ Complete " + name);

def sendSeqName(name):
	for ip in ["192.168.1.150", "192.168.1.156"]:
		url = f"http://{ip}/api/sequence/{name}"
		localname = "@" + name;
		parts = ["/usr/bin/curl", "-X", "POST", "--data-binary",  localname, url]
		logIt(" ".join(parts))
		subprocess.call(parts)
		logIt(f"Upload complete - {ip}")

def sendSeq(midnight = False):
	name = getFileName(midnight, True)
	sendSeqName(name)

if __name__ == "__main__":
        baseNames = ['BRODY', 'EMILY', 'MATT', 'WILL', 'JULIA', 'SOPHIE', 'LONDON', 'MAX', 'BENNY', 'LUIS', 'KORIE', 'MARY', 'GREG', 'NANCY', 'JERRY', 'JIM', 'JEFF', 'ANGIE', 'DON', 'MAGGIE']
        #genereateXml(baseNames)
        genereateMidnightXml("This is a test.   It is only a test")
        generateSeq(True)
        sendSeq(True)
