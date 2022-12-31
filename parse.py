from typing import Generic, TypeVar, Callable

A = TypeVar("A")
B = TypeVar("B")
T = TypeVar("T")

class Unit:
	def __init__(self) -> None:
		pass

	def __repr__(self) -> str:
		return "()"

class Maybe(Generic[T]):
	pass

class Nothing(Maybe[T]):
	def __init__(self) -> None:
		super().__init__()
	
	def __repr__(self) -> str:
		return "Nothing"
	
	def isJust(self) -> bool: return False

class Just(Maybe[T]):
	def __init__(self, x: T) -> None:
		self.x = x
		super().__init__()

	def __repr__(self) -> str:
		return f"Just({self.x.__repr__()})"

	def isJust(self) -> bool: return True

class Message:
	def __init__(self, prefix: Maybe[str], command: str, params: "list[str]"=[]) -> None:
		self.prefix = prefix
		self.command = command
		self.params = params

	def __repr__(self) -> str:
		return f"Message({self.prefix.__repr__()}, {self.command.__repr__()}, {self.params.__repr__()})"

class Parser(Generic[A]):
	def __init__(self, parse: "Callable[[str], Maybe[(str, A)]]") -> None:
		self.parse = parse
		super().__init__()

	def map(self, f:"Callable[[A], B]") -> "Parser[B]":
		def parse(str0: str) -> "Maybe[(str, B)]":
			res = self.parse(str0)
			if not res.isJust(): return Nothing()
			str1, res1 = res.x

			return Just((str1, f(res1)))

		return Parser(parse)

	def prod(self, other: "Parser[B]") -> "Parser[(A, B)]":
		def parse(str0: str) -> "Maybe[(str, (A, B))]":
			res = self.parse(str0)
			if not res.isJust(): return Nothing()
			str1, res1 = res.x

			res = other.parse(str1)
			if not res.isJust(): return Nothing()
			str2, res2 = res.x

			return Just((str2, (res1, res2)))

		return Parser(parse)

	def ignoreL(self, other: "Parser[B]") -> "Parser[B]":
		def parse(str0: str) -> "Maybe[(str, B)]":
			res = self.parse(str0)
			if not res.isJust(): return Nothing()
			str1, _ = res.x
			res = other.parse(str1)
			if not res.isJust(): return Nothing()
			str2, res2 = res.x
			return Just((str2, res2))

		return Parser(parse)

	def ignoreR(self, other: "Parser[B]") -> "Parser[A]":
		def parse(str0: str) -> "Maybe[(str, A)]":
			res = self.parse(str0)
			if not res.isJust(): return Nothing()
			str1, res1 = res.x
			res = other.parse(str1)
			if not res.isJust(): return Nothing()
			str2, res2 = res.x
			return Just((str2, res1))

		return Parser(parse)

	def rep0(self) -> "Parser[list[A]]":
		def parse(str0: str) -> "Maybe[(str, list[A])]":
			result: "list[A]" = []
			while True:
				res = self.parse(str0)
				if not res.isJust(): return Just((str0, result))
				str1, res1 = res.x
				str0 = str1
				result.append(res1)

		return Parser(parse)

	def rep(self) -> "Parser[list[A]]":
		return self.prod(self.rep0()).map(lambda x: x[0] + "".join(x[1]))

	def __or__(self, other: "Parser[A]") -> "Parser[A]":
		def parse(str0: str) -> "Maybe[(str, A)]":
			res = self.parse(str0)
			if res.isJust(): return res
			
			return other.parse(str0)
		
		return Parser(parse)

def stringP(s: str) -> Parser[Unit]:
	def parse(str0: str) -> "Maybe[(str, Unit)]":
		if len(str0) < len(s): return Nothing()
		for i in range(len(s)):
			if s[i] != str0[i]: return Nothing()
		
		return Just((str0[len(s):], Unit()))
	
	return Parser(parse)

def sstringP(s: str) -> Parser[str]:
	return stringP(s).map(lambda _: s)

def charPredP(pred: "Callable[[str], bool]") -> Parser[str]:
	def parse(str0: str) -> "Maybe[(str, str)]":
		if len(str0) == 0: return Nothing()
		if not pred(str0[0]): return Nothing()

		return Just((str0[1:], str0[0]))

	return Parser(parse)

def spanPredP(pred: "Callable[[str], bool]") -> Parser[str]:
	def parse(str0: str) -> "Maybe[(str, str)]":
		for i in range(len(str0)):
			if not pred(str0[i]):
				return Just((str0[i:], str0[0:i]))
		
		return Just(("", str0))

	return Parser(parse)

def concatP(*args) -> Parser[str]:
	def parse(str0: str) -> "Maybe[(str, str)]":
		result = ""
		for arg in args:
			res = arg.parse(str0)
			if not res.isJust(): return Nothing()
			str1, res1 = res.x

			result += res1
			str0 = str1
		
		return Just((str0, result))

	return Parser(parse)


spaceP: Parser[Unit] = stringP(" ").ignoreR(stringP(" ").rep0())

letterP: Parser[str] = \
Parser(lambda str0: Just((str0[1:], str0[0])) if len(str0) > 0 and str0[0].isalpha() else Nothing())

digitP: Parser[str] = \
Parser(lambda str0: Just((str0[1:], str0[0])) if len(str0) > 0 and str0[0].isdigit() else Nothing())

hostP: Parser[str] = \
letterP.prod((letterP | digitP | sstringP("-")) .rep0()).map(lambda x: x[0] + ''.join(x[1]))

specialP: Parser[str] = sstringP('-') | sstringP('[') | sstringP(']') | sstringP('\\') | \
sstringP('`') | sstringP('^') | sstringP('{') | sstringP('}')

nickP: Parser[str] = \
letterP.prod((letterP | digitP | specialP) .rep0()).map(lambda x: x[0] + ''.join(x[1]))

chstringP: Parser[str] = \
charPredP(lambda char: not (ord(char) in [0x7, 0x20, 0x0, 0xa, 0xd, 0x2c]))

maskP: Parser[str] = (stringP("#") | sstringP("$")).prod(chstringP).map(lambda x: "".join(x))

channelP: Parser[str] = (stringP("#") | sstringP("&")).prod(chstringP).map(lambda x: "".join(x))

nonwhitePred = lambda char: not (ord(char) in [0x20, 0x0, 0xa, 0xd])

nonwhiteP: Parser[str] = charPredP(nonwhitePred)

userP: Parser[str] = nonwhiteP.rep()

toP: Parser[str] = \
concatP(spanPredP(lambda x: nonwhitePred(x) and x != "@"), sstringP("@"), hostP) | channelP | maskP

def parseMessage(msg: str) -> Message:
	msg: "list[str]" = msg.split(" ")
	prefix: Nothing[str] = Nothing()
	if msg[0][0] == ":": 
		prefix = msg[0][1:]
		msg = msg[1:]
	
	command = msg[0]
	params = msg[1:]

	return Message(prefix, command, params)

print(toP.parse("asdas@ab3cdef123-asdsd"))