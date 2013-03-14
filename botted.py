from twisted.words.protocols import irc
from twisted.internet import protocol
import shlex
import random



class Command:
    def __init__(self,bot):
        self.bot = bot
    
    def run(self,cmd,args,variables):
        raise Exception('Implement this')

    def name(self):
        raise Exception('Implement this')
    
    def usage(self):
        raise Exception('Implement this')

class TimeCommand(Command):
    
    def run(self,cmd,args,variables):
        from time import gmtime, strftime, time
        
        t= strftime("%a, %d %b %Y %H:%M:%S", gmtime(time()+3600*2) )
        
        self.bot.msg(variables['response_channel'], 'Time is now {time}'.format(time=t))

    def name(self):
        return '!time'
    
    def usage(self):
        return '!time    Gives the time, in Jerusalem'

class HelpCommand(Command):
    
    def run(self,cmd,args,variables):
        
        
        self.bot.print_usage(variables,wrong_usage=False)

    def name(self):
        return '!help'
    
    def usage(self):
        return '!help    You have to know what this does'

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
        return '!tell <nick> <message>\n        Gives over <message> to user specified by <nick>'

class LastSubRedditPostCommand(Command):
    
    def run(self,cmd,args,variables):
        if not len(args) == 0:
            self.bot.msg(variables['response_channel'], variables['response_prefix'] + '!last usage> ' + self.usage())
            return
        
        
        reddit_querier = self.bot.factory.main_context['reddit_querier']
        config = self.bot.factory.main_context['config']
        
        client = reddit_querier.session
        
        parameters = {'limit':1}
        url = r'http://www.reddit.com/r/{sr}/{top}.json'.format(sr=config['subreddit'],top='new')
        r = client.get(url,params=parameters)
        
        import json
        j = json.loads(r.text)
        
        if j['kind'] != 'Listing':
            print "j['kind']:",j['kind']
            return
        
        title = j['data']['children'][0]['data']['title'].encode('utf-8')
        
        
        self.bot.msg(self.bot.factory.channel, 'LAST POST: {title}'.format(title=title))

    def name(self):
        return '!last'
    
    def usage(self):
        return '!last    Displays the last post on the subreddit'

class Bot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)
        
        
        
        self.command_modules = {}
        
        self.command_modules['time']=TimeCommand(self)
        self.command_modules['tell']=TellCommand(self)
        self.command_modules['help']=HelpCommand(self)
        self.command_modules['last']=LastSubRedditPostCommand(self)
        
        
        
        

    def joined(self, channel):
        #print "Joined %s." % (channel,)
        pass


    def print_usage(self,variables,wrong_usage=False):
        
        
        usage = ''
        
        
        cmds = []
        usage_list = []
        for cmd_name,cmd_module in self.command_modules.iteritems():
            cmds += [cmd_name]
            usage_list += [cmd_module.usage()]
        
        
        usage += '\n\n' + 'Available commands: ' + ' '.join(cmds)
        usage += '\n\n' + 'Usage: \n  ' + '\n  '.join(usage_list) + '\n\n'


        self.msg(variables['user_nick'],usage)

        if variables['in_channel']:
            if wrong_usage:
                self.msg(variables['response_channel'], variables['response_prefix'] + 'umm ... wrong usage ... I pm\'d you proper usage!')
            else:
                self.msg(variables['response_channel'], variables['response_prefix'] + 'I pm\'d you the proper usage.')


    def run_command(self,full_cmd,variables):

        args = shlex.split(full_cmd)
        cmd = args[0]
        args = args[1:]
        
        
        if cmd not in self.command_modules:
            self.print_usage(variables,True)
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
                if msg.lower().find("sholom") != -1:
                
                    dweed_exasperated_msgs = ['Oh Dweed ...', 'JeNug SHoiN!',]
                    self.msg(channel, dweed_exasperated_msgs[random.randint(0,len(dweed_exasperated_msgs)-1)])
                    
                    return
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
            print 'Exception:',e




class BotFactory(protocol.ClientFactory):
    protocol = Bot
    
    def buildProtocol(self, addr):
        bot = protocol.ClientFactory.buildProtocol(self,addr)
        self.bots.append(bot)
        return bot

    def __init__(self, channel, nickname,main_context):
        self.channel = channel
        self.nickname = nickname
        self.bots = []
        self.main_context = main_context

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)

import sys
from twisted.internet import reactor


class RedditService:
    def __init__(self,bot_factory,subreddit):
        self.bot_factory = bot_factory
        self.before = None
        self.subreddit = subreddit
    
    def run(self):
        
        
        import requests
        import json
        from pprint import pprint
        
        
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
                
                for bot in self.bot_factory.bots:
                    bot.msg(bot.factory.channel, 'NEW POST: {title}'.format(title=jpost['data']['title']))
            
            
        finally:
            client.close()


class RedditQuerier:
    def __init__(self):
        import requests
        self._session = requests.session()
    
    def _get_session(self):
        return self._session
    
    session = property(_get_session)

def main():
    import yaml

    config_file = open('config.yml')

    config = None

    try:
        config = yaml.load(config_file)
    except:
        print
        print "ERROR: parsing configuration"
        print
        
        raise

    main_context = {}
    
    main_context['reddit_querier'] = RedditQuerier()
    main_context['config'] = config
    
    bot_factory = BotFactory(config['channel'],config['nick'],main_context)

    reactor.connectTCP(config['server_host'], config['server_port'], bot_factory)
    
    #reactor.connectTCP('irc.freenode.net', 6667, BotFactory('#reddit-judaism','Moses'))
    
    
    services = [RedditService(bot_factory,config['subreddit'])]
    
    def run_services():
        for service in services:
            
            try:
                service.run()
            except Exception as e:
                # TODO, log exception, and pass
                raise
        
    
    from twisted.internet.task import LoopingCall
    lc2 = LoopingCall(run_services)
    
    lc2.start(10)
    
    reactor.run()



if __name__ == "__main__":
    main()
