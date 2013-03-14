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
        return '!tell    <nick> <message>    Gives over <message> to user specified by <nick>'



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
        
        self.command_modules[cmd].run(cmd,args,variables)
        
        
        
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

    def __init__(self, channel, nickname):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)

import sys
from twisted.internet import reactor



def main():
    import yaml

    config_file = open('config.json')

    config = None

    try:
        config = yaml.load(config_file)
    except:
        print
        print "ERROR: parsing configuration"
        print
        
        raise

    reactor.connectTCP(config['server_host'], config['server_port'], BotFactory(config['channel'],config['nick']))
    
    #reactor.connectTCP('irc.freenode.net', 6667, BotFactory('#reddit-judaism','Moses'))
    
    reactor.run()



if __name__ == "__main__":
    main()
