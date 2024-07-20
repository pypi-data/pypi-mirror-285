import threading
import time
from .context import JobContext


class Worker(threading.Thread):
    def __init__(self, resource, channel, logger, context:JobContext):
        super().__init__()
        self.daemon = True
        self.resource = resource
        self.channel = channel
        self.logger = logger
        self.context = context

    def run(self):
        r = self.resource(logger=self.logger,
                          channel=self.channel,
                          context=self.context)

        # joblog start message
        tm_st = int(time.time())
        self.channel.publish_notify(self.context, 'job start', 2)
        self.logger.info("main, start app, %s", self.context.action_app)

        """user main function invoke
        return value
            success = 0
            failure = 1
        """
        rt = r.main()
        if rt == 0:
            tm_ed = int(time.time())
            self.logger.info("main, end   app, %s", self.context.action_app)
            self.channel.publish_job(self.context)
            self.channel.publish_notify(self.context, 'job end, success', 4, tm_ed-tm_st)
        else:
            self.logger.warning("main, end   app, %s", self.context.action_app)
            self.channel.publish_notify(self.context, 'job end, failed', 7)
