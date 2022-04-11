import requests
import argparse
import sys
from multiprocessing import Process, Queue
from time import sleep
from tqdm import tqdm
import defs
from colorama import Fore as f
from random import randint as rand
from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from datetime import datetime
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from random import randint as rand
import string
import os
from PIL import Image

def logger(func):
    def out(msg):
        print(f"{f.GREEN}[{datetime.now().strftime('%H:%M:%S')}]{f.RESET} {msg}")

    def wrapper(*args, **kwargs):
        print(f"{f.GREEN}[{datetime.now().strftime('%H:%M:%S')}]{f.RESET} {f.LIGHTBLUE_EX}{func.__name__}{f.RESET}")
        start = time.time()
        val = func(*args, **kwargs, out=out)
        end = time.time()
        print(f"{f.GREEN}[{datetime.now().strftime('%H:%M:%S')}]{f.RESET} {f.LIGHTBLUE_EX}{func.__name__}{f.RESET} {f.LIGHTGREEN_EX}Completed in {round(end-start, 2)}s{f.RESET}")
        return val


    return wrapper

@logger
def DownloadData(out=None):
	link = "https://raw.githubusercontent.com/tabatkins/wordle-list/main/words"

	try:
		words = requests.get(link, timeout=5)
	except requests.Timeout or ConnectionRefusedError or ConnectionError or ConnectionResetError or ConnectionAbortedError:
		sys.exit("Unstable internet")

	return words.text.split("\n")

letters = "q w e r t y u i o p a s d f g h j k l z x c v b n m".split(" ")

@logger
def ArgParser(args, out=None):
	out("Parsing arguments.")
	parser = argparse.ArgumentParser(description="Wordle solver")
	parser.add_argument("-s", "--solve", help="Start solving todays wordle", action="store_true")
	parser.add_argument("-wa", "--wordle-archive", help="Start solving a wordle archive (https://wordlearchive.com/{argument})", type=int)
	parser.add_argument("-sb", "--show-browser", help="Show the browser window", action="store_false", default=True)
	parser.add_argument("-ss", "--save-screenshot", help="Save a screenshot of the wordle once the right answer is found", type=str)
	parser.add_argument("--hint", help="Pass a number and you will get the letter that is in that place in the word, if this is not passed the wordle/wordle archive is solved regularly. --show-browser is ignored and logs are suppressed", type=int, default=None)

	return parser.parse_args(args)

@logger
def main(out=None):

	if (len(sys.argv) == 1):
		out("No arguments given")
		return

	words = DownloadData()
	args = ArgParser(sys.argv[1:])

	#if (args.save_screenshot != None):
	#	if (os.path.exists(args.save_screenshot)):
	#		out("Screenshot file already exists.")
	#		sys.exit()

	if (args.solve):
		if (args.save_screenshot != None):
			StartBrowser(words, solvetype="wordle", headless=args.show_browser, ss=os.path.abspath(args.save_screenshot), hint=args.hint)
		else:
			StartBrowser(words, solvetype="wordle", headless=args.show_browser, hint=args.hint)
		return
	if (args.wordle_archive != None):
		if (args.save_screenshot != None):
			StartBrowser(words, solvetype=args.wordle_archive, headless=args.show_browser, ss=os.path.abspath(args.save_screenshot), hint=args.hint)
		else:
			StartBrowser(words, solvetype=args.wordle_archive, headless=args.show_browser, hint=args.hint)
		
		return

@logger
def StartSolveProcess(words, green, gray, yellow, YellowNot, out=None):

	q = Queue()
	arg = (q, words, green, gray, yellow, YellowNot)





	out("Checking possibilities...")
	possibilities = []
	bar = tqdm(total=len(words), desc="", unit="Word", colour="green", leave=False)
	sleep(rand(1, 15)/10)
	p = Process(target=defs.Solve, args=arg)
	p.start()
	try:
		size = q.get(timeout=5)
	except queue.Empty:
		out("Process could not start")
		sys.exit()
	amount = 0
	q.put("start")
	while True:
		try:
			#q.put("next")
			data = q.get(timeout=5)
			
			if (data == "done"):
				break
			possibilities.append(data)
			if (len(data) == 2) and amount != len(words):
				amount += 1
				bar.update(1)
		except queue.Empty:
			try:
				#q.put("next")
				data = q.get(timeout=5)
				
				if (data == "done"):
					break
				possibilities.append(data)
				if (len(data) == 2) and amount != len(words):
					amount += 1
					bar.update(1)
			except queue.Empty:
				break

	bar.close()
	p.terminate()

	right = []
	for i in possibilities:
		if (i[1] == True):
			right.append(i[0])

	right.sort()
	return right

@logger
def Type(word, buttons, out=None):
	out("Sending data to wordle.")
	for i in word:
		buttons[i].click()
	time.sleep(0.1)
	buttons["enter"].click()

@logger
def RemoveCopy(result, out=None):

	for i in range(len(result["absent"])):
		if (result["absent"][i] in string.ascii_lowercase):
			if (result["absent"][i] in result["correct"] or result["absent"][i] in result["present"]):
				result["absent"] = result["absent"][:i] + result["absent"][i+3:]
				result = RemoveCopy(result)
				break

	return result

@logger
def StartBrowser(words, solvetype="wordle", headless=True, ss=None, out=None, hint=None):
	out("Creating webdriver.")

	option = webdriver.ChromeOptions()

	option.binary_location = os.path.dirname(__file__) + "\\..\\chrome-win\\chrome.exe"
	if (headless or hint != None):
		option.headless = True
		option.add_argument('--disable-gpu')
	option.add_experimental_option('excludeSwitches', ['enable-logging'])
	option.add_argument('--log-level=OFF')
	option.add_argument("--window-size=1920x1080")
	option.add_argument("--start-maximized")

	br = webdriver.Chrome(options=option, service=Service(os.path.dirname(__file__) + "\\..\\chromedriver.exe"))

	
	if (solvetype == "wordle"):
		out("Loading https://www.nytimes.com/games/wordle/index.html.")
		br.get("https://www.nytimes.com/games/wordle/index.html")
	else:
		out("Loading https://wordlearchive.com/" + str(solvetype))
		br.get("https://wordlearchive.com/" + str(solvetype))

	out("Parsing HTML.")
	if (solvetype == "wordle"):
		try:
			row = br.find_element(By.CLASS_NAME, "nightmode")
			out("Dark mode detected.")
		except selenium.common.exceptions.NoSuchElementException:
			row = br.find_element(By.XPATH, "/html/body")
			out("Light mode detected.")
	else:
		try:
			row = br.find_element(By.CLASS_NAME, "page-home nightmode")
			out("Dark mode detected.")
		except selenium.common.exceptions.NoSuchElementException:
			row = br.find_element(By.CLASS_NAME, "page-home")
			out("Light mode detected.")
	#row.find_element(By.XPATH, "game-app").find_element(By.XPATH, "//game-theme-manager").find_element(By.XPATH, "div").find_element(By.XPATH, "game-keyboard")
	game = row.find_element(By.XPATH, "game-app")
	#root = test.shadow_root
	root = br.execute_script("return arguments[0].shadowRoot", game)
	
	if (solvetype == "wordle"):
		out("Closing help menu.")
		close = root.find_element(by = By.TAG_NAME, value = "game-theme-manager").find_element(By.TAG_NAME, "header").find_element(By.CLASS_NAME, "menu-left").find_element(By.ID, "nav-button")
		ac = ActionChains(br)
		ac.move_to_element(close).click().perform()

	keyboard = root.find_element(by = By.TAG_NAME, value = "game-theme-manager").find_element(By.ID, "game").find_element(By.TAG_NAME, "game-keyboard")

	game = root.find_element(by = By.TAG_NAME, value = "game-theme-manager").find_element(By.ID, "game")

	out("Finding button elements.")

	board = game.find_element(By.ID, "board-container").find_element(By.ID, "board").find_elements(By.TAG_NAME, "game-row")



	shadow = br.execute_script("return arguments[0].shadowRoot", keyboard)
	rows = shadow.find_element(By.ID, "keyboard").find_elements(By.CLASS_NAME, "row")
	buttons = {}
	for row in rows:
		for button in row.find_elements(By.XPATH, "*"):
			buttons[button.get_attribute("data-key")] = button
	
	if (solvetype == "wordle"):
		buttons["enter"] = buttons["↵"]
		buttons.pop("↵")
	else:

		buttons["enter"] = buttons["â†µ"]
		buttons.pop("â†µ")

	out("Solving.")
	row = 0
	result = {'present': "", "absent": "", "correct": ""}
	temp = []
	for i in words:
		if (i not in temp):
			temp.append(i)
	words = temp
	Type(words[rand(0, len(words)-1)], buttons)
	out("Finding result.")
	time.sleep(1)
	letters = br.execute_script("return arguments[0].shadowRoot", board[row]).find_element(By.CLASS_NAME, "row").find_elements(By.TAG_NAME, "game-tile")
	for letter in range(len(letters)):
		result[letters[letter].get_attribute("evaluation")] += letters[letter].get_attribute("letter") + str(letter) + ","
		if (hint == None):
			out(letters[letter].get_attribute("letter") + ": " + letters[letter].get_attribute("evaluation"))

	result = RemoveCopy(result)

	if (len(result["correct"]) == 15):
		if (ss != None):
			out("Taking screenshot.")
			time.sleep(2)
			br.save_screenshot(ss)
			#img = Image.open(ss)
			#img.crop((785, 204, 1118, 607)).save(ss)
			out(f"Screenshot saved to {ss}.")
		if (hint == None):
			out(f"Answer found! {f.LIGHTYELLOW_EX}{board[row].get_attribute('letters')}")
		else:
			out(f"The letter at the {hint} position is {board[row].get_attribute('letters')[int(hint-1)]}.")
		br.close()
		return

	if (hint != None):
		if (str(hint-1) in result["correct"]):
			for let in range(len(result["correct"])):
				if (result["correct"][let] == str(hint-1)):
					letterhint = result["correct"][let-1]
					if (ss != None):
						out("Taking screenshot.")
						time.sleep(2)
						br.save_screenshot(ss)
						#img = Image.open(ss)
						#img.crop((785, 204, 1118, 607)).save(ss)
						out(f"Screenshot saved to {ss}.")
					out(f"The letter at the {hint} position is {letterhint}.")
					br.close()
					return

	time.sleep(1)

	newwords = []

	for i in words:
		rightorwrong = True
		for letter in result["correct"].split(",")[:-1]:
			if (i[int(letter[1])] != letter[0]):
				rightorwrong = False
				break
		for letter in result["present"].split(",")[:-1]:
			if (letter[0] not in i):
				rightorwrong = False
				break
			if (i[int(letter[1])] == letter[0]):
				rightorwrong = False
				break
		for letter in result["absent"].split(",")[:-1]:
			if (letter[0] in i):
				rightorwrong = False
				break
		if (rightorwrong):
			newwords.append(i)
	
		words = newwords

	row += 1

	for _ in range(5):
		result = {'present': "", "absent": "", "correct": ""}
		temp = []
		for i in words:
			if (i not in temp):
				temp.append(i)
		words = temp

		Type(words[rand(0, len(words)-1)], buttons)
		out("Finding result.")
		time.sleep(1)
		game = root.find_element(by = By.TAG_NAME, value = "game-theme-manager").find_element(By.ID, "game")
		board = game.find_element(By.ID, "board-container").find_element(By.ID, "board").find_elements(By.TAG_NAME, "game-row")
		#br.execute_script("return arguments[0].shadowRoot", board[row])
		letters = br.execute_script("return arguments[0].shadowRoot", board[row]).find_element(By.CLASS_NAME, "row").find_elements(By.XPATH, "*")
		for letter in range(len(letters)):
			result[letters[letter].get_attribute("evaluation")] += letters[letter].get_attribute("letter") + str(letter) + ','
			if (hint == None):
				out(letters[letter].get_attribute("letter") + ": " + letters[letter].get_attribute("evaluation"))


		result = RemoveCopy(result)

		if (len(result["correct"]) == 15):
			if (ss != None):
				out("Taking screenshot.")
				time.sleep(2)
				br.save_screenshot(ss)
				#img = Image.open(ss)
				#img.crop((785, 204, 1118, 607)).save(ss)
				out(f"Screenshot saved to {ss}.")
			if (hint == None):
				out(f"Answer found! {f.LIGHTYELLOW_EX}{board[row].get_attribute('letters')}")
			else:
				out(f"The letter at the {hint} position is {board[row].get_attribute('letters')[int(hint-1)]}.")
			br.close()
			return

		time.sleep(1)

		if (hint != None):
			if (str(hint-1) in result["correct"]):
				for let in range(len(result["correct"])):
					if (result["correct"][let] == str(hint-1)):
						letterhint = result["correct"][let-1]
						if (ss != None):
							out("Taking screenshot.")
							time.sleep(2)
							br.save_screenshot(ss)
							#img = Image.open(ss)
							#img.crop((785, 204, 1118, 607)).save(ss)
							out(f"Screenshot saved to {ss}.")
						out(f"The letter at the {hint} position is {letterhint}.")
						br.close()
						return

		if (row >= 5):
			out(f"No answer found, restarting...")
			br.close()
			StartBrowser(words, solvetype=solvetype, headless=headless, ss=ss)
			sys.exit()

		newwords = []

		for i in words:
			rightorwrong = True
			for letter in result["correct"].split(",")[:-1]:
				if (i[int(letter[1])] != letter[0]):
					rightorwrong = False
					break
			for letter in result["present"].split(",")[:-1]:
				if (letter[0] not in i):
					rightorwrong = False
					break
				if (i[int(letter[1])] == letter[0]):
					rightorwrong = False
					break
			for letter in result["absent"].split(",")[:-1]:
				if (letter[0] in i):
					rightorwrong = False
					break
			if (rightorwrong):
				newwords.append(i)

			words = newwords

		row += 1
	
if (__name__ == "__main__"):
	main()

