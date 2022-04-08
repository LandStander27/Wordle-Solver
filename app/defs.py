from time import sleep

def check(green, word):
	for i in green.keys():
		if (green[i] != None):
			if (green[i] != word[int(i)-1]):
				return False
	return True

def CheckYellow(word, yellow):
	for i in yellow:
		if (i not in word):
			return False
	return True

def CheckYellowNot(word, YellowNot):
	for x in list(YellowNot.keys()):
		if (YellowNot[x] != None):
			let = YellowNot[x].split(",")
			for y in let:
				if (x == word[int(y)-1]):
					
					return False
	return True

def Solve(q, words, green, gray, yellow, YellowNot):
	q.put(str(len(words)))
	while True:
		if (q.get() == "start"):
			break
	for word in words:
		
		if check(green, word):
			if CheckYellow(word, yellow):

				
				if (CheckYellowNot(word, YellowNot)):
					if (any(ele in word for ele in gray)) == False:
						q.put([word, True])
		q.put([word, False])
		#while q.get() != "next":
		#	sleep(0.1)
	q.put("done")