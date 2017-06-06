# hello, world

Following the
[tradition](http://stackoverflow.com/questions/602237/where-does-hello-world-come-from)
of introducing new programming tools with a `'hello, world'` example,
let us write our first Zentropian `Agent` that replies to a `hello`
with `hello, world`.

Let us quickly glance at what the finished program will look like,
then we will build it up line-by-line later.

```python
from zentropi import Agent, on_message, run_agents, ZentropiShell


class HelloBot(Agent):
    @on_message('hello')
    def say_hello(self, message):
        return 'hello, world'


if __name__ == '__main__':
    hello_bot = HelloBot(name='hello_bot')
    shell = ZentropiShell(name='shell')
    run_agents(hello_bot, shell)
```


The first line imports some objects from the zentropi module.

```python
from zentropi import Agent, on_message, run_agents, ZentropiShell
```

This syntax allows us to bring `Agent`, `on_message` and other objects
directly in to our program's namespace. We could alternatively use
`import zentropi`, but we would also have to access the objects
and functions with a longer name like `zentropi.Agent`.

Next is the `class` definition for `HelloBot`.

```
class HelloBot(Agent):
    @on_message('hello')
    def say_hello(self, message):
        return 'hello, world'
```

The line, `class HelloBot(Agent):` defines our agent named HelloBot,
which is also an Agent, because we inherit from Agent. This adds some
useful methods to our class automatically, which we will use later.

> `methods` are functions on a class that expect an instance
of the class as the first parameter.

We use the Python decorator syntax on line: `@on_message('hello')`
to mark the following method as a `handler` for messages that
match "hello". A message is what you expect - a text message.
The method `say_hello()` will be called every time HelloBot
receives a message with text "hello".

We define the handler (method) right after the `on_message` decorator.

```
    def say_hello(self, message):
        return 'hello, world'
```

Here `def` starts the handler definition, followed by parameters it
accepts - `self`, which is the instance of `HelloBot` class
and a `message`, which will be passed in automatically when our
handler is called.

For this example, we will not need it, we know that `say_hello()`
will get called only when message exactly matches "hello",
case and white-space included.

The body of the method contains a single line `return 'hello, world'`,
which sends the string `'hello, world'` as a reply to the original
message.

We follow the definition of HelloBot with a convention that tells python
that code block under it will not be executed if we `import` the module.

```
if __name__ == '__main__':
```

Next lines are executed only when we run hello as a script, that is,
as `$ python hello.py` or `$ python -m hello`. Doing so ensures that we
can `import` our agents into other scripts and not worry about them
automatically starting up.

Cool, now let us create an instance of our bot:

```
    hello_bot = HelloBot(name='hello_bot')
```

Zentropi comes with a few built-in agents that we can use along with
the agents we write to provide useful and often-needed functions.
For example, if we are making bots that can respond to text messages,
it would be great to have a way to interact with the agent to test it.

```
    shell = ZentropiShell(name='shell')
```

We now have a shell agent, it can do a few tricks for us, but for now
we need not worry about it much more than this.

And finally, we run our two agents:

```
run_agents(hello_bot, shell)
```

When running multiple agents in a single python process like above,
the agent that interacts with users (`shell`) goes at the end.

And that is all!

Save this file as `hello.py` or you can find a copy in
`examples/00_hello_world/hello.py`.

Finally, bring the agent to life by running it with `$ python hello.py`.

> You will need to type the command in the the same directory as the
file you just saved, for which you may have to `cd` into
`examples/00_hello_world`.

You should see this on your screen:

```
$ python hello.py
⚡ ︎ @shell: '*** started'
⚡ ︎ @shell: 'shell-starting'
⚡ ︎ @shell: 'shell-ready'
〉
```

This is our shell agent displaying all the events it is emitting.
Events are displayed with a lightning bolt, followed by @agent_name
and then the event-name. We'll use events to make agents automatically
perform tasks when certain events are observed, for now, we will go back
to text messages.

We can type any message at the prompt `〉` and the shell agent will
broadcast it for us. Go ahead and type "hello", followed by ENTER.

```
〉hello
✉  @shell: 'hello'
✉  @hello_bot: 'hello, world' {'text': 'hello, world'}
⚡ ︎ @shell: 'shell-ready'
〉
```

If you see output as above, congratulations!

You have successfully created your first Zentropian Agent, connected it
with shell-agent and demonstrated that the message that we
typed in the shell goes to HelloBot and back.
