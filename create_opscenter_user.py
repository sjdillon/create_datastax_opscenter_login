#!python
#==========================================================================#
# 1. Creates an OpsCenter login for monitoring Cassandra Clusters
# 2. Generates random password
# 3. Tests login
# python create_opscenter_user.py -U xxxx.xxx@xxxxx.com -M True -D True -S faustian
# resources:
# opscenter api - http://docs.datastax.com/en/opscenter/5.1/api/docs/
# python rest - http://docs.python-requests.org/en/latest/user/advanced/
#==========================================================================#
import argparse
import requests
import sys
from colorama import Fore, Back, Style
import string
import random
from colorama import Fore, Back, Style
import win32com.client
import ConfigParser

#parse arguments
parser = argparse.ArgumentParser(description='create opscenter users')
parser.add_argument('-U','--username', help='login to be created',required=False)
parser.add_argument('-D','--dropfirst', help='drop user if exists',required=False, default='False')
parser.add_argument('-R','--role', help='role of user being added',required=False, default='readonly')
parser.add_argument('-M','--send_email', help='send email with credentials',required=False, default='True')
parser.add_argument('-S','--server', help='opscenter host server',required=False, default='lv')
args = parser.parse_args()

if not args.username or "." not in args.username:
	print 'Error: username required - format username like first.last'
	sys.exit(1)

#get variables from config file
config = ConfigParser.ConfigParser()
config.readfp(open('opscenter.cfg'))
uname=config.get('default', 'uname')
pw=config.get('default', 'pw')
host=config.get(args.server, 'host')
url="http://%s:8888" % (host)

new_user=args.username[0].lower()+args.username.split('.')[1].lower().split('@')[0]
new_user_role=args.role

def create_random_pw():
	size=3
	dictionary_file='words.txt'
	#chars=string.ascii_uppercase + string.digits
	chars=string.digits
	num=''.join(random.choice(chars) for _ in range(size))
	pw=random.choice(open(dictionary_file).readlines()).rstrip('\n')
	return pw+num

def print_message(msg,status):
	if status in ('OK','PASS') :
		print '[%s]\t%s'  % (Fore.GREEN+status+Style.RESET_ALL,msg)
	else:
		print '[%s]\t%s'  % (Fore.RED+status+Style.RESET_ALL,msg)

def send_pw(to, login, pw, body):
	mail_item = 0x0
	obj = win32com.client.Dispatch("Outlook.Application")
	mail = obj.CreateItem(mail_item)
	mail.Subject = "OpsCenter credentials"
	mail.Body = 'Credentials: %s/%s\n%s\n' % (login,pw,body)
	mail.To = to #for testing, change to me"
	if pw:
		try:
			mail.Send()
		except Exception, e:
			print '[ERROR]: %s' % ( str(e) )
			print 'mail send failed'
	else:
		print 'missing pw, not sending email'		

def delete_login(login):
	session=get_session(uname, pw)
	result= session.delete("%s/users/%s" % (url,login))
	if result.status_code == requests.codes.ok:
		print_message( '%s deleted' % (login), 'OK')
	else:
		print_message( '%s deleted: (%s)' % (login,result.json()['message']), 'FAIL')

def create_login(new_user,new_user_role):
	new_user_pw=create_random_pw() 
	session=get_session(uname, pw)
	new_user_body_json = '{"password": "%s", "role": "%s"}' % (new_user_pw, new_user_role)
	result= session.post("%s/users/%s" % (url,new_user), data=new_user_body_json)
	if result.status_code == requests.codes.ok:
		print_message( '%s created: %s/%s' % (new_user,new_user,new_user_pw), 'OK')
		test_login(new_user,new_user_pw)
		return new_user_pw
	else:
		print_message( '%s created: (%s)' % (new_user,result.json()['message']), 'FAIL')

def get_session(uname, pw):
	session = requests.Session()
	login_body_json = '{"username": "%s", "password": "%s"}' % (uname, pw)
	login_response = session.post("%s/login" % (url), data=login_body_json).json()
	return session

def test_login(uname, pw):
	try:
		session=get_session(uname, pw)
		request=session.get("%s/permissions/user" % (url)).json()
		key, value = request.popitem()
		if key<>'message':
			print_message('%s test' % (uname), 'OK')
		else:
			print_message('%s test' % (uname), 'FAIL')
	except Exception, e:
		print_message('%s test: (%s)' % (uname, str(e)), 'FAIL')			


def add_new_user():
	if args.dropfirst=="True":
		delete_login(new_user)
	new_pw=create_login(new_user,new_user_role)
	if args.send_email=="True":
		to=args.username
		send_pw(to, new_user, new_pw, url) 

add_new_user()	
