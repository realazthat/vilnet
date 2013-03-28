
    
class Command:
    def __init__(self,bot):
        self.bot = bot
    
    def run(self,cmd,args,variables):
        raise Exception('Implement this')

    def name(self):
        raise Exception('Implement this')
    
    def usage(self):
        raise Exception('Implement this')
