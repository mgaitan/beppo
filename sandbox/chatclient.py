from twisted.internet import reactor
from twisted.manhole import telnet



def createShellServer( ):

	print 'Creating shell server instance'

	factory = telnet.ShellFactory()

	port = reactor.listenTCP(1025, factory)

	factory.namespace['x'] = 'hello world'

	#factory.username = 'mike'

	#factory.password = 'which1ta'

	print 'Listening on port 1025'

	return port



if __name__ == "__main__":

	reactor.callWhenRunning( createShellServer )

	reactor.run()
