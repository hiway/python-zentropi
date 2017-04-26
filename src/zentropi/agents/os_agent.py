# coding=utf-8

from .. import (Agent,
                on_event,
                on_timer)


class OSAgent(Agent):
    """
    Template to build agents that provide services related to Operating Systems.
    """

    def os_info(self):
        pass

    def network_info(self):
        pass

    def installed_apps(self):
        pass

    def active_apps(self):
        pass

    def background_apps(self):
        pass

    def user_active_since(self):
        pass

    def user_inactive_since(self):
        pass

    @on_timer(10)
    def check_active_app(self):
        pass

    @on_timer(30)
    def check_activity(self):
        pass

    @on_timer(60)
    def check_network_status(self):
        pass

    @on_event('*** started')
    def check_os_info(self, event):
        pass
