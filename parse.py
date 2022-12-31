from enum import Enum

class CmdType(Enum):
	USER = 1
	NICK = 2
	QUIT = 3
	JOIN = 4
	PART = 5
	LIST = 6
	PRIVMSG = 7
	WHO = 8
	NUMERICAL = 9

def cmdTypeToString(cmdType: CmdType) -> str:
		result = {CmdType.USER:"USER", CmdType.NICK:"NICK", CmdType.QUIT:"QUIT", \
		CmdType.JOIN:"JOIN", CmdType.PART:"PART", CmdType.LIST:"LIST", CmdType.PRIVMSG: "PRIVMSG", \
		CmdType.WHO: "WHO", CmdType.NUMERICAL:"NUMERICAL"}
		return result[cmdType]

class Command:
	def __init__(self, cmdType: CmdType, params:"dict[str, str]"={}) -> None:
		self.cmdType = cmdType
		self.params = params

	def __repr__(self) -> str:
		return f"{cmdTypeToString(self.cmdType)} {str(self.params)}"

def parseUser(msg: str) -> Command:
	cmdType = CmdType.USER
	params = {}
	msg = msg.split(" ")
	params["username"] = msg[1]
	params["hostname"] = msg[2]
	params["servername"] = msg[3]
	params["realname"] = " ".join(msg[4:])[1:]

	return Command(cmdType, params)

def parseNick(msg: str) -> Command:
	cmdType = CmdType.NICK
	params = {"nickname": msg.split(" ")[1]}
	
	return Command(cmdType, params)

def parseQuit(msg: str) -> Command:
	cmdType = CmdType.QUIT
	msg = msg.split(" ")
	if len(msg) < 2: params = {"quitmessage":""}
	else: params = {"quitmessage": " ".join(msg[1:])[1:]}
	
	return Command(cmdType, params)

def parseJoin(msg: str) -> Command:
	cmdType = CmdType.JOIN
	params = {}
	msg = msg.split(" ")
	
	params["channel"] = msg[1]
	if len(msg) > 2: params["key"] = msg[2]
	else: params["key"] = ""

	return Command(cmdType, params)

def parsePart(msg: str) -> Command:
	cmdType = CmdType.PART
	params = {"channel": msg.split(" ")[1]}
	
	return Command(cmdType, params)

def parseList(msg: str) -> Command:
	cmdType = CmdType.LIST
	params = {}
	
	return Command(cmdType, params)

def parsePrivmsg(msg: str) -> Command:
	cmdType = CmdType.PRIVMSG
	params = {}

	msg = msg.split(" ")
	params["target"] = msg[1]
	params["text"] = " ".join(msg[2:])[1:]
	
	return Command(cmdType, params)

def parseWho(msg: str) -> Command:
	cmdType = CmdType.WHO
	params = {"name": msg.split(" ")[1]}
	
	return Command(cmdType, params)

def parseMessage(msg: str) -> Command:
	cmdName = msg.split(" ")[0].lower()

	if   cmdName == "USER": return parseUser(msg)
	elif cmdName == "NICK": return parseNick(msg)
	elif cmdName == "QUIT": return parseQuit(msg)
	elif cmdName == "JOIN": return parseJoin(msg)
	elif cmdName == "PART": return parsePart(msg)
	elif cmdName == "LIST": return parseList(msg)
	elif cmdName == "PRIVMSG": return parsePrivmsg(msg)
	elif cmdName == "WHO": return parseWho(msg)
	else: return Command(CmdType.NUMERICAL, {"num":421})