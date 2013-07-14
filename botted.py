# -*- coding: utf-8 -*-
from twisted.words.protocols import irc
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

import shlex
import random
from command_modules.command import Command
import upsidedown
import urllib

import socket
import urlparse
import requests
import traceback,sys
from dns import resolver,reversename

import requests
import json
from pprint import pprint
    
import HTMLParser
import urllib
import json
import pygeoip
from time import gmtime, strftime, time
        
import sys
    
import time,calendar

import requests
import json
import re
from bs4 import BeautifulSoup
import yaml

"""
from https://gist.github.com/1595135

Written by Christian Stigen Larsen, http://csl.sublevel3.org
Placed in the public domain by the author, 2012-01-11
"""
def ip_int_from_string(s):
    "Convert dotted IPv4 address to integer."
    return reduce(lambda a,b: a<<8 | b, map(int, s.split(".")))

def ip_int_to_string(ip):
    "Convert 32-bit integer to dotted IPv4 address."
    return ".".join(map(lambda n: str(ip>>n & 0xFF), [24,16,8,0]))

def shorten_url(long_url):
    long_url = long_url.encode('utf-8')
    
    
    parameters = {"longUrl": long_url}
    
    
    
    headers = {'Content-Type':'application/json'}
    api_url = 'https://www.googleapis.com/urlshortener/v1/url'
    r = requests.post(api_url,data=json.dumps(parameters),headers=headers)
    
    
    j = json.loads(r.text)
    
    if 'id' not in j or 'longUrl' not in j or j['longUrl'].encode('utf-8') != long_url:
        return long_url
    
    return j['id'].encode('utf-8')
    

def unescape_entities(html):
    return HTMLParser.HTMLParser().unescape(html)
    


def obtain_address_info(host,config):
    
    results = {}
    

    ip = None
    print 'host:',host
    try:
        data = socket.gethostbyname(host)
        #ip = repr(data)
        ip = data
        
        print 'ip:',ip
    except Exception:
        raise
    
    results['ip'] = ip
    results['iplocations'] = {}

    try:
        
        #FIXME: does this need to be cleaned up??
        rresponse = urllib.urlopen('http://api.hostip.info/get_json.php?ip={ip}&position=true'.format(ip=ip)).read()
            
        
        rresponse_json = json.loads(rresponse)
        print 'rresponse_json:',rresponse_json
        
        response = (
            '|hostip| country: "{country}" city: "{city}" longitude: {longitude} latitude: {latitude}'.format(
                country=rresponse_json['country_name'],
                city=rresponse_json['city'],
                longitude=rresponse_json['lng'],
                latitude=rresponse_json['lat']))
        results['iplocations']['hostip'] = response
        
        
    except Exception as e:
        print 'hostip error:',e
        results['iplocations']['hostip'] = '|hostip| error'
        
    
    try:
        gic = pygeoip.GeoIP(config['geoipcityip4_path'])
        
        record = gic.record_by_addr(ip)
        
                
        response = ('|geoipcityip4| ' + str(record))
        
        results['iplocations']['geoipcityip4'] = response
    except Exception as e:
        print 'pygeoip error',e
        results['iplocations']['geoipcityip4'] = '|geoipcityip4| error'
    
    try:
        ip_int = ip_int_from_string(ip)
        
        #print 'ip_int:',ip_int

        with open(config['IpToCountry_csv']) as ip2country:
            for line in ip2country:
                line = line.strip()
                line_data = line.split(',')
                if len(line) == 0:
                    continue
                if line[0] == '#':
                    continue
                
                """
                print 'line:',line
                print 'line_data:',line_data
                print 'len(line_data):',len(line_data)
                """
                start_str = line_data[0].strip()[1:-1]
                end_str = line_data[1].strip()[1:-1]
                """
                print 'start_str:',start_str
                print 'end_str:',end_str
                print
                """
                ip_first_int = int(start_str)
                ip_last_int = int(end_str)
                if ip_first_int <= ip_int and ip_int <= ip_last_int:
                    
                    #print line_data
                    registry = line_data[2].strip()[1:-1]
                    country = line_data[6].strip()[1:-1]
                    ip_first = ip_int_to_string(ip_first_int)
                    ip_last = ip_int_to_string(ip_last_int)
                    
                    response = ('|IpToCountry| range:[{ip_first}-{ip_last}], registry: {registry}, country: {country}'.format(
                            ip_first=ip_first,ip_last=ip_last,registry=registry,country=country))
                    
                    results['iplocations']['IpToCountry'] = response
                    
                    break
            results['iplocations']['IpToCountry'] = '|IpToCountry| error, no results'
    except Exception as e:
        print 'IpToCountry error:',e
        results['iplocations']['IpToCountry'] = '|IpToCountry| error'
        
    
    
    
    results['domains'] = []
    try:
        addr=reversename.from_address(ip)
        print addr
        
        for hmm in resolver.query(addr,"PTR"):
            results['domains'] += [str(hmm)]
    except Exception as e:
        
        print 'Reverse DNS error:',e
    
    return results

class ActionCommand(Command):
    def __init__(self,bot,cmd,action,has_target):
        Command.__init__(self,bot)
        self.cmd = cmd
        self.action = action
        self.has_target = has_target
    def run(self,cmd,args,variables):
        if self.has_target:
            nick = args[0]
            self.bot.describe(variables['response_channel'], self.action.format(nick=nick))
        else:
            self.bot.describe(variables['response_channel'], self.action)
            
    
    def name(self):
        return '!{cmd}'.format(cmd=self.cmd)
    
    def usage(self):
        if self.has_target:
            return '!{cmd} <nick>'.format(cmd=self.cmd)
        return '!{cmd}'.format(cmd=self.cmd)
        
class ArtCommand(Command):
    def __init__(self,bot,cmd,response):
        Command.__init__(self,bot)
        
        self.cmd = cmd
        self.response = response
        
    def run(self,cmd,args,variables):
        self.bot.msg(variables['response_channel'], self.response)
    def name(self):
        return '!{cmd}'.format(cmd=self.cmd)
    
    def usage(self):
        return '!{cmd}'.format(cmd=self.cmd)

class IpLocateCommand(Command):
    

    def run(self,cmd,args,variables):
        
        nick = args[0]
        
        print 'ping:',self.bot.ping(nick)
        
        host = args[0]
        results = obtain_address_info(host,self.bot.config)
        print 'results:',results
        
        if results['ip'] != host:
            self.bot.msg(variables['response_channel'], variables['response_prefix'] + 'IP:' + results['ip'])

        
        for iplocation_service,iplocation_info in results['iplocations'].iteritems():
            self.bot.msg(variables['response_channel'], variables['response_prefix'] + iplocation_info)
        
        if len(results['domains']) != 0:
            self.bot.msg(variables['response_channel'], variables['response_prefix'] + 'domains: {' + ','.join(results['domains']) + '}')
            
    
                
        

    def name(self):
        return '!iplocate'
    
    def usage(self):
        return '!iplocate <host>    Gives location data about the host address'

class UserLocateCommand(Command):
    

    def name(self):
        return '!userlocate'
    
    def usage(self):
        return '!userlocate <nick>    Gives location data about the user\'s hostmask'

class TimeCommand(Command):
    
    def run(self,cmd,args,variables):
        
        t= strftime("%a, %d %b %Y %H:%M:%S", gmtime(time.time()+3600*2) )
        
        self.bot.msg(variables['response_channel'], 'Time is now {time}'.format(time=t))

    def name(self):
        return '!time'
    
    def usage(self):
        return '!time    Gives the time, in Jerusalem'

class HelpCommand(Command):
    
    def run(self,cmd,args,variables):
        
        if len(args) == 0:
        
            self.bot.print_usage(variables,None)
            return
            
        
        if len(args) != 1:
            
            self.bot.msg(variables['response_channel'],variables['response_prefix'] + 'Wrong usage.' + self.usage)
            return
            
        command = args[0]
        
        if command not in self.bot.command_modules:
            self.bot.print_usage(variables,extra_msg='Cannot find help on a non-existant command.')
            return
        
        command_module = self.bot.command_modules[command]
        
        self.bot.msg(variables['response_channel'],variables['response_prefix'] + command_module.usage())
        
        
    def name(self):
        return '!help'
    
    def usage(self):
        return '!help [command]'

class TellCommand(Command):
    
    def run(self,cmd,args,variables):
        
        if not len(args) == 2:
            self.bot.msg(variables['response_channel'], variables['response_prefix'] + '!tell usage> ' + self.usage())
            return
        
        nick = args[0]
        message = args[1]
        
        if nick.lower() == self.bot.nickname.lower():
            self.bot.msg(variables['response_channel'], variables['response_prefix'] + 'Wow, a sense of humor')
            return
            
        self.bot.msg(self.bot.factory.channel, '{nick}: {message}'.format(nick=args[0],message=args[1]))
        
    def name(self):
        return '!tell'
    
    def usage(self):
        return '!tell <nick> <message>\n           Gives (publicly) over <message> to user specified by <nick>'

class LastSubRedditPostCommand(Command):
    
    def run(self,cmd,args,variables):
        pprint(self.bot.channel_nicks)
        
        if not len(args) == 0:
            self.bot.msg(variables['response_channel'], variables['response_prefix'] + '!last usage> ' + self.usage())
            return
        
        
        reddit_querier = self.bot.factory.main_context['reddit_querier']
        config = self.bot.factory.main_context['config']
        
        client = reddit_querier.session
        
        parameters = {'limit':1}
        url = r'http://www.reddit.com/r/{sr}/{top}.json'.format(sr=config['subreddit'],top='new')
        #r = client.get(url,params=parameters)
        r = requests.get(url,params=parameters)
        
        j = json.loads(r.text)
        
        if j['kind'] != 'Listing':
            print "j['kind']:",j['kind']
            return
        
        if len(j['data']['children']) == 0:
            raise Exception('Reddit API returned 0 posts for !last')
        
        jpost = j['data']['children'][0]
        
        
        #print "jpost['data']:"
        #pprint.pprint(jpost['data'])
        
        permalink = 'http://www.reddit.com/{permalink}'.format(permalink=jpost['data']['permalink'].encode('utf-8'))
        
        
        permalink = shorten_url(unescape_entities(permalink)).encode('utf-8')
        domain = unescape_entities(jpost['data']['domain']).encode('utf-8')
        url = unescape_entities(jpost['data']['url']).encode('utf-8')
                                
        title = unescape_entities(jpost['data']['title']).encode('utf-8')
        
        author = unescape_entities(jpost['data']['author']).encode('utf-8')
        
        
        if not jpost['data']['is_self'] and len(url) < 100:
            self.bot.msg(self.bot.factory.channel, 'LAST POST: "{title}" ({permalink} | {url}) by {author}'.format(
                author=author,title=title,permalink=permalink,url=url))
        else:
            self.bot.msg(self.bot.factory.channel, 'LAST POST: "{title}" ({permalink} | {domain}) by {author}'.format(
                author=author,title=title,permalink=permalink,domain=domain))

    def name(self):
        return '!last'
    
    def usage(self):
        return '!last    Displays (publicly) the last post on the subreddit'



class Bot(irc.IRCClient):
    def __init__(self):
        pass
    
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def signedOn(self):
        
        if 'nickserv_password' in self.config:
            self.msg('NickServ', 'identify {password}'.format(password=self.config['nickserv_password']))
        
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)
        
        
        
        self.command_modules = {}
        
        self.command_modules['time']=TimeCommand(self)
        self.command_modules['tell']=TellCommand(self)
        self.command_modules['help']=HelpCommand(self)
        self.command_modules['last']=LastSubRedditPostCommand(self)
        self.command_modules['iplocate']=IpLocateCommand(self)
        
    
        self.command_modules['shoot']=ActionCommand(self,'shoot','︻デ═一 {nick}', has_target=True)
        self.command_modules['tableflip']=ActionCommand(self,'tableflip','（╯°□°）╯︵ ┻━┻', has_target=False)
        self.command_modules['stab']=ActionCommand(self,'stab','stabs {nick}', has_target=True)
        self.command_modules['wave']=ActionCommand(self,'wave','waves at {nick}', has_target=True)
        self.command_modules['stakeburn']=ActionCommand(self,'stakeburn','burns {nick} on a stake', has_target=True)
        self.command_modules['slap']=ActionCommand(self,'slap','slaps {nick} around a bit with a large ><((((\'>', has_target=True)
        self.command_modules['ucrazy']=ActionCommand(self,'ucrazy','ლ(ಠ益ಠლ) ?', has_target=False)
        self.command_modules['eat']=ActionCommand(self,'eat','eats {nick}', has_target=True)
        self.command_modules['cry']=ActionCommand(self,'cry','┗[© ♒ ©]┛ ROBOT HAS NO USE FOR FEELINGS', has_target=False)
        
        
        soup =  r"""
               ) (
              (    ) 
             ____(___
          _|`--------`|
         (C|          |__
       /` `\          /  `\
    jgs\    `========`    /
        `'--------------'`
"""
        self.command_modules['soup'] = ArtCommand(self,'soup',soup)
        
        
        feedme = r'''
       __
      /
   .-/-.
   |'-'|
   |   |
   |   |   .-""""-.
   \___/  /' .  '. \   \|/\//
         (`-..:...-')  |`""`|
          ;-......-;   |    |
     jgs   '------'    \____/
'''
        
        self.command_modules['feedme'] = ArtCommand(self,'feedme',feedme)

        
        cake = r"""
                 66666
               __|||||__   H A P P Y
              {._._._._.}     B I R T H D A Y  !
       jgs  __{._._._._.}__
           `~~~~~~~~~~~~~~~`
"""
        
        self.command_modules['bday'] = ArtCommand(self,'bday',cake)
        
        fuse = r"""
                        (
       __________       )\
      /         /\______{,}
 jgs  \_________\/
 
"""

        self.command_modules['fuse'] = ArtCommand(self,'fuse',fuse)

        tanks = r"""
        _          _          _          _          _     
      _[_]===    _[_]===    _[_]===    _[_]===    _[_]=== 
 jgs (_____)    (_____)    (_____)    (_____)    (_____)
"""
        self.command_modules['tanks'] = ArtCommand(self,'tanks',tanks)

        eek = r"""
             \\\
      .---.  /// 
     (:::::)(_)():
      `---'  \\\
      jgs    ///
"""
        
        self.command_modules['eek'] = ArtCommand(self,'eek',eek)


        jahanum = r"""
          (       ..:::[=--.  /o\             _
            )   .:::''      \ (")\           /_\
           (,`):::,(.        `/:\            I I
           ) (. )' ('         |:|`\       ,={_O_}
      jgs (,)' ). (' ),)     _/^|_  -.__.'   | |
"""
        

        self.command_modules['jahanum'] = ArtCommand(self,'jahanum',jahanum)
        
        cuptea = r"""
               ) (
              (    ) 
             ____(___
          _|`--------`|
         (C|          |__
       /` `\          /  `\
    jgs\    `========`    /
        `'--------------'`
"""
        

        self.command_modules['cuptea'] = ArtCommand(self,'cuptea',cuptea[1:])
        hearts = r"""
     _  _              _  _              _  _              _  _ 
   /` \/ `\   _  _   /` \/ `\   _  _   /` \/ `\   _  _   /` \/ `\   _  _ 
   \      / /` \/ `\ \      / /` \/ `\ \      / /` \/ `\ \      / /` \/ `\
    '.  .'  \      /  '.  .'  \      /  '.  .'  \      /  '.  .'  \      /
      \/     '.  .'     \/     '.  .'     \/     '.  .'     \/     '.  .'
    jgs        \/                \/                \/                \/
"""
        

        self.command_modules['hearts'] = ArtCommand(self,'hearts',hearts[1:])

        plane = r'''
                _
              -=\`\
          |\ ____\_\__
        -=\c`""""""" "`)
     jgs   `~~~~~/ /~~`
             -==/ /
               '-'
'''
        

        self.command_modules['plane'] = ArtCommand(self,'plane',plane[1:])

        """
        for command_module in self.command_modules:
            command_module.config = self.main_context['config']
            command_module.main_context = self.main_context
        """
        
        
        """
        {channel => {nick => host}}
        """
        self.channel_nicks = {}

    """
    def names(self, channel):
        "List the users in 'channel', usage: client.who('#testroom')"
        #self.sendLine('NAMES %s' % channel)
        self.channel_nicks[channel] = {}
        pass
    def irc_RPL_NAMREPLY(self, prefix, params):
        print 'irc_RPL_NAMREPLY({prefix},{params})'.format(prefix=prefix,params=params)
        
        channel = params[2]
        nicks = params[3].strip().split(' ')
        
        
        this_channel_nicks = self.channel_nicks[channel]
        for nick in nicks:
            this_channel_nicks.add(nick)
        
        print 'self.channel_nicks:',self.channel_nicks
    def irc_RPL_ENDOFNAMES(self, prefix, params):
        print 'irc_RPL_ENDOFNAMES({prefix},{params})'.format(prefix=prefix,params=params)

    def joined(self, channel):
        #print "Joined %s." % (channel,)
        self.names(channel)
        pass

    def remember_user(self,user,channel):
        channel_nicks = self.channel_nicks
        if channel not in channel_nicks:
            channel_nicks[channel] = set()
        
        nick,_,_ = user.partition('!')
        channel_nicks[channel] |= set([nick])
        
    def forget_user(self,user, channel):
        channel_nicks = self.channel_nicks
        if channel not in channel_nicks:
            print "WARNING, SOMETHING WRONG IN forget_user(): channel not in channel_nicks"
            return
        
        nick,_,_ = user.partition('!')
        if nick not in channel_nicks[channel]:
            print "WARNING, SOMETHING WRONG IN forget_user(): nick not in channel_nicks[channel]"
            return
        
        channel_nicks[channel].discard(nick)
    
    """
    def userJoined(self,user, channel):
        print 'userJoined({user},{channel})'.format(user=user,channel=channel)
        
        #if channel in self.channel_nicks:
        #    print 'WARNING: userJoined(), channel in self.channel_nicks'
        
        #self.channel_nicks[channel] = set()
        
        #self.remember_user(user,channel)
    """
    def userLeft(self,user, channel):
        print 'userLeft({user},{channel})'.format(user=user,channel=channel)
        self.forget_user(user,channel)
    def userQuit(self,user, channel):
        print 'userQuit({user},{channel})'.format(user=user,channel=channel)
        self.forget_user(user,channel)
    def userKicked(self,user, channel):
        print 'userKicked({user},{channel})'.format(user=user,channel=channel)
        self.forget_user(user,channel)
    def userRenamed(self,oldname, newname):
        channel_nicks = self.channel_nicks
        
        print 'userKicked({oldname},{newname})'.format(newname=newname,oldname=oldname)
        
        
        for channel,nicks in channel_nicks.iteritems():
            
            if oldname in nicks:
                nicks.discard(oldname)
                nicks.add(newname)
        
    """
        

    def print_usage(self,variables,extra_msg=None):
        
        
        usage = ''
        
        
        cmds = []
        #usage_list = []
        for cmd_name,cmd_module in self.command_modules.iteritems():
            cmds += [cmd_name]
            #usage_list += [cmd_module.usage()]
        
        
        #usage += '\n\n' + 'Available commands: ' + ' '.join(cmds)
        #usage += '\n\n' + 'Usage: \n  ' + '\n  '.join(usage_list) + '\n\n'


        if extra_msg is None:
            extra_msg = ''
        else:
            extra_msg += ' '
        
        self.msg(variables['response_channel'],
                 '''{msg}Available commands: {cmds}\nUse !help COMMAND for more help.'''.format(msg=extra_msg, cmds=' '.join(cmds)))
        
       

        """
        self.msg(variables['user_nick'],usage)
        
        if variables['in_channel']:
            if wrong_usage:
                self.msg(variables['response_channel'], variables['response_prefix'] + 'umm ... wrong usage ... I pm\'d you proper usage!')
            else:
                self.msg(variables['response_channel'], variables['response_prefix'] + 'I pm\'d you the proper usage.')
        """

    def run_command(self,full_cmd,variables):

        args = shlex.split(full_cmd)
        cmd = args[0]
        args = args[1:]
        
        
        if cmd not in self.command_modules:
            self.print_usage(variables,extra_msg='No such command.')
            return
        
        try:
            self.command_modules[cmd].run(cmd,args,variables)
        except Exception as e:
            print e
            
            self.msg(variables['response_channel'], variables['response_prefix'] + 'Error running command, see bot logs')
            raise
        
    def privmsg(self, user, channel, msg):
        
                
        
        
        
        
        try:
            print channel+'>',user+':',msg
            user_nick,_,_ = user.partition('!')
            
            variables = {'nick':self.nickname,'user_nick':user_nick,'response_channel':channel,'channel':channel}
            variables['response_prefix'] = user_nick + ': '
            
            """
            #if this is not a pm
            if channel != self.nickname:
                if msg.startswith(self.nickname + ":"):
                    self.msg(channel, user_nick+': '+ '/msg me, or pm me, I cannot do business in an open channel.')
                    return
                return
            """
            
            full_cmd = ''
            
            variables['in_channel'] = True
            
            #if this is a pm
            if channel == self.nickname:
                
                
                variables['response_channel'] = user_nick
                variables['response_prefix'] = ''
                variables['in_channel'] = False
                full_cmd = msg
                
                
                if msg.startswith(self.nickname + ":"):
                    self.msg(variables['response_channel'], variables['response_prefix']+ 'This is a PM, Don\'t prefix your commands with "{botnick}:".'.format(botnick=self.nickname))
                    return
                
            elif msg.startswith(self.nickname + ":"):
                full_cmd = msg[ len(self.nickname + ":"): ].strip()
                
            else:
                #not directed at the bot
                
                if msg.lower().find("sholom") != -1:
                
                    dweed_exasperated_msgs = ['Oh Dweed ...', 'JeNug SHoiN!','Oy. Do you even lift??!', 'Come at me bro', 'Ain\'t nobody got time for that.']
                    self.msg(channel, dweed_exasperated_msgs[random.randint(0,len(dweed_exasperated_msgs)-1)])
                    
                    return
                
                if msg.find("sS") != -1 or msg.find("hH") != -1:# or msg.find(u'Hɥ') != -1 or msg.find(u'Ss') != -1:
                    self.msg(channel, upsidedown.transform(msg).encode('utf-8'))
                    
                    return
                
                
                if msg.lower().find('come at me') != -1:
                    rurls = [
                                'http://img.pr0gramm.com/2013/04/ggpkbtv.gif', #pool table nut
                                'http://i.imgur.com/Zm8WxSG.gif', #Yoda
                                'http://i.imgur.com/m4fOtwE.gif', #sith
                                'http://i.imgur.com/uktLLMF.gif', #mighty spider
                                'http://i.imgur.com/F0ja0Y2.gif', #matrix guy
                                'http://i.imgur.com/aB7Ujnl.gif', #dean supernatural
                                'http://i.imgur.com/iBA9903.gif', #stick figures playing game
                            ]
                    
                    rurl = random.choice(rurls)
                    
                    self.msg(channel, variables['response_prefix'] \
                        + shorten_url(rurl).encode('utf-8'))
                
                #print 'self.factory.non_cmd_privmsg_monitors:',self.factory.non_cmd_privmsg_monitors
                for cb in self.factory.non_cmd_privmsg_monitors:
                    try:
                        cb(self,variables,user,channel,msg)
                    except Exception as e:
                        print 'exception in Bot.privmsg(), privmsg_cb (',cb,') e:',e
                        traceback.print_exc(file=sys.stdout)
                return
            
            
            
            if len(full_cmd) == 0:
                self.msg(channel, 'shhh'.format(**variables))
                return
            
            if full_cmd[0] == '!':
                self.run_command(full_cmd[1:],variables)
                return
            
            
            full_cmd = full_cmd.lower()
            
            d = {'shalom':'shalom {user_nick}, my name is {nick}',
                 'sholom':'Oh Dweed ...'}
            
            
            if full_cmd not in d:
                self.msg(variables['response_channel'], 'Odd, I thought I heard something.'.format(**variables))
                return
            
            self.msg(channel, d[full_cmd].format(**variables))
            
            return
            
                

            pass
        except Exception as e:
            traceback.print_exc(file=sys.stdout)

            
            print 'Exception:',e




class BotFactory(protocol.ClientFactory):
    protocol = Bot
    
    def buildProtocol(self, addr):
        bot = protocol.ClientFactory.buildProtocol(self,addr)
        self.bots.append(bot)
        bot.main_context = self.main_context
        bot.config = self.config
        
        return bot

    def __init__(self, channel, nickname,main_context):
        self.channel = channel
        self.nickname = nickname
        self.bots = []
        self.main_context = main_context
        self.config = main_context['config']
        self.non_cmd_privmsg_monitors = []

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)



class SefiraService:
    
    def __init__(self,bot_factory):
        self.bot_factory = bot_factory
        self.last_run = 0
    def run(self):
        
        
        
        t0 = (2013, 3, 26, 23, 0, 0, 0, 1, -1)
        t0 = calendar.timegm(t0)
        
        
        t1 = time.time()
        
        announcement_frequency = 60*60
        
        if t1 - self.last_run < announcement_frequency:
            return
        print 't1 - self.last_run:',t1 - self.last_run
        print 'self.last_run:',self.last_run
        
        
        
        self.last_run = int(t1- (int(t1) % announcement_frequency))
        
        
        
        
        
        t = int(t1 - t0)
        
        days = t // (3600 * 24)
        
        #move it back one day
        days -= 1
        
        
        date = time.gmtime(t0 + (days * (3600 * 24)))
        next_date = time.gmtime(t0 + ((days+1) * (3600 * 24)))
        response = 'NOTICE: Sefira for \x031,9YESTERDAY\x03, {date}: *{count}* Days of the omer.' \
            + ' You can count until sunset on {next_date}.' \
            + ' WARNING: THIS IS ALPHA, DOUBLE CHECK THIS YOURSELF (http://goo.gl/hzY2v)'
        
        response = response.format(date=time.strftime("%a NIGHT, %d %b %I:%M %p",date),
                                   next_date=time.strftime("%a",next_date),
                                   count=(days+1))
        
        
        for bot in self.bot_factory.bots:
            bot.msg(bot.factory.channel, response)

        
        
        
    
class RedditService:
    def __init__(self,bot_factory,subreddit):
        self.bot_factory = bot_factory
        self.before = None
        self.subreddit = subreddit
    
    def run(self):
        
        
        
        
        client = requests.session()
        
        try:
            parameters={'limit':1}
            
            if self.before != None:
                parameters['before'] = self.before
                parameters['limit'] = 3
            
            
            url = r'http://www.reddit.com/r/{sr}/{top}.json'.format(sr=self.subreddit,top='new')
            r = client.get(url,params=parameters)
            #print 'sent URL is', r.url
            #j = r.json
            j = json.loads(r.text)
            #pprint(j)
            
            if j['kind'] != 'Listing':
                print "j['kind']:",j['kind']
                return
            
            def set_before():
                if len(j['data']['children']) != 0:
                    first_post_kind = j['data']['children'][0]['kind']
                    first_post_id = j['data']['children'][0]['data']['id']
                
                    self.before = '{kind}_{post_id}'.format(kind=first_post_kind,post_id=first_post_id)
            
            if self.before == None:
                set_before()
                return
            
            set_before()
            
            
            for jpost in  j['data']['children']:
                
                
                permalink = 'http://www.reddit.com/{permalink}'.format(permalink=jpost['data']['permalink'].encode('utf-8'))
                
                
                permalink = shorten_url(unescape_entities(permalink)).encode('utf-8')
                domain = unescape_entities(jpost['data']['domain']).encode('utf-8')
                url = unescape_entities(jpost['data']['url'].encode('utf-8'))
                
                title = unescape_entities(jpost['data']['title']).encode('utf-8')
                author = unescape_entities(jpost['data']['author']).encode('utf-8')
                
                
                for bot in self.bot_factory.bots:
                    
                    if not jpost['data']['is_self'] and len(url) < 100:
                        bot.msg(bot.factory.channel, 'NEW POST: "{title}" ({permalink} | {url}) by {author}'.format(
                            author=author,title=title,permalink=permalink,url=url))
                    else:
                        bot.msg(bot.factory.channel, 'NEW POST: "{title}" ({permalink} | {domain}) by {author}'.format(
                            author=author,title=title,permalink=permalink,domain=domain))
            
            
        finally:
            client.close()


class RedditNewCommentService:
    def __init__(self,bot_factory,main_context):
        self.bot_factory = bot_factory
        self.main_context = main_context
    
    def run(self):
        pass
        
        
    pass

class RedditQuerier:
    def __init__(self):
        self._session = requests.session()
    
    def _get_session(self):
        return self._session
    
    session = property(_get_session)

class TitleGrabber:
    def __init__(self):
        pass
    def monitor_privmsg(self,bot,variables,user,channel,msg):
        
        if channel != bot.factory.channel:
            return
        
        #from https://gist.github.com/uogbuji/705383
        GRUBER_URLINTEXT_PAT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
        
        for mgroups in GRUBER_URLINTEXT_PAT.findall(msg):
            url = mgroups[0]
            
            html = urllib.urlopen(url).read()
            
            
            break
        
        

def main():

    config_file = open('config.yml')

    config = None

    try:
        config = yaml.load(config_file)
    except:
        print
        print "ERROR: parsing configuration"
        print
        
        raise

    


    #import sqlite3
    
    #db_conn = sqlite3.connect(config['db_path'])

    main_context = {}
    
    #main_context['db_conn'] = db_conn
    main_context['reddit_querier'] = RedditQuerier()
    main_context['config'] = config
    
    bot_factory = BotFactory(config['channel'],config['nick'],main_context)

    reactor.connectTCP(config['server_host'], config['server_port'], bot_factory)
    
    
    bot_factory.non_cmd_privmsg_monitors = [
        TitleGrabber().monitor_privmsg
    ]
    
    
    services = [
        RedditService(bot_factory,config['subreddit']).run,
        #SefiraService(bot_factory).run,
        RedditNewCommentService(bot_factory, main_context).run
        ]
    
    def run_services():
        for service in services:
            
            try:
                service()
            except Exception as e:
                print 'Exception running service (',service,') e:',e
                traceback.print_exc(file=sys.stdout)
        
    
    lc2 = LoopingCall(run_services)
    
    lc2.start(10)
    
    reactor.run()



if __name__ == "__main__":
    main()
