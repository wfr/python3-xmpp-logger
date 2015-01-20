#!/usr/bin/env python3
"""
    Jabber/XMPP logging handler for Python 3
    (c) Wolfgang Frisch <wfr@roembden.net>
    License: BSD 2-Clause
"""


import logging
import sleekxmpp 
#from sleekxmpp.exceptions import IqError, IqTimeout


class LogBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
    
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # ping


    def session_start(self, event):
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        """respond to incoming messages"""
        #if msg['type'] in ('chat', 'normal'):
        #    msg.reply("Thanks for sending\n%(body)s" % msg).send()
        pass



class JabberLogHandler(logging.StreamHandler):
    connected = False

    def __init__(self, jid, password, recipient):
        logging.StreamHandler.__init__(self)
        # the handler must ignore its own logging
        self.addFilter(lambda record: (record.name.find("sleekxmpp") == -1))
        self.recipient = recipient
        
        self.xmpp = LogBot(jid, password)
        try:
            self.xmpp.connect()
            self.xmpp.process(threaded=True)
            self.connected = True
        except Exception as e:
            logging.error("cannot connect to server, disabling")
            self.connected = False


    def emit(self, record):
        if self.connected:
            try:
                msg = self.format(record)
                self.xmpp.send_message(mto=self.recipient, mbody=msg)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)

    def close(self):
        self.xmpp.disconnect()
        logging.StreamHandler.close(self)


if __name__ == "__main__":
    # manual testing
    import sys
    import time

    if len(sys.argv) != 4:
        print("./jabberlog.py JID PASSWORD RECIPIENT", file=sys.stderr)
        sys.exit(1)
    
    JID, PASS, RECIPIENT = sys.argv[1:]

    LOG_FORMAT = '[%(asctime)-15s %(levelname)6s %(name)s]  %(message)s'
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    jabberLogHandler = JabberLogHandler(jid=JID, password=PASS, recipient=RECIPIENT)
    jabberLogHandler.setFormatter(logging.Formatter(LOG_FORMAT))
    jabberLogHandler.setLevel(logging.INFO)
    logger.addHandler(jabberLogHandler)
   
    time.sleep(3)

    logging.warning("testing 1 2 3")
    
    time.sleep(3)
    jabberLogHandler.close()
    
    


# vim:set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:

