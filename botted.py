from twisted.words.protocols import irc
from twisted.internet import protocol
import shlex
import random



class Command:
    def __init__(self,bot):
        self.bot = bot
        pass
    
    def run(self,cmd,args,variables):
        pass


class TimeCommand(Command):
    
    def run(self,cmd,args,variables):
        from time import gmtime, strftime, time
        
        t= strftime("%a, %d %b %Y %H:%M:%S", gmtime(time()+3600*2) )
        
        self.bot.msg(variables['response_channel'], 'Time is now {time}'.format(time=t))

    def name(self):
        return '!time'
    
    def usage(self):
        return '!time    Gives the time, in Jerusalem'



class Bot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname,)
        
        
        
        self.command_modules = {}
        
        self.command_modules['time']=TimeCommand(self)
        
        
        
        

    def joined(self, channel):
        #print "Joined %s." % (channel,)
        pass


    def print_usage(self,variables):
        
        
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
            self.msg(variables['response_channel'], variables['response_prefix'] + 'umm ... wrong usage ... I pm\'d you proper usage!')
        

    def run_command(self,full_cmd,variables):

        args = shlex.split(full_cmd)
        cmd = args[0]
        args = args[1:]
        
        
        if cmd not in self.command_modules:
            self.print_usage(variables)
            return
        
        self.command_modules[cmd].run(cmd,args,variables)
        
        
        
    def privmsg(self, user, channel, msg):


        
        
        
        
        try:
            print channel+'>',user+':',msg
            user_nick,_,_ = user.partition('!')
            
            variables = {'nick':self.nickname,'user_nick':user_nick,'response_channel':channel}
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
                self.msg(channel, 'Odd, I thought I heard something.'.format(**variables))
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
    
    #reactor.connectTCP('irc.synirc.net', 6667, BotFactory('#reddit-judaism','Moses'))
    reactor.connectTCP('irc.freenode.net', 6667, BotFactory('#reddit-judaism','Moses'))
    
    reactor.run()



if __name__ == "__main__":
    main()
