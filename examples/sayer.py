from zentropi import Agent, on_message
import envoy

class Sayer(Agent):
    @on_message('button_press')
    def say_something(self, event):
        envoy.run('say "testing"')

sayer = Sayer(auth='f02838a44a8440228159a1118976a6f3')
sayer.connect('wss://trials.zentropi.com/')
sayer.join('zentropia')
sayer.run()
