# -*- coding: utf-8 -*-
import uuid
import subprocess as subp
from dotdict import dotdict


class GenericStep(object):

    expected_out = None
    on_success_hint = None
    on_wrong_out_hint = None
    on_err_hint = None

    def __call__(self, user_input):
        out, err, returncode = self.run_command(user_input)
        json_result = self.analyze(out, err, returncode)
        return json_result

    def get_uuid(self):
        if not hasattr(self, '_uuid'):
            self._uuid = str(uuid.uuid4())
        return self._uuid

    def run_command(self, user_input):
        command = self.get_command(user_input)
        pipe = subp.Popen(command, stdout=subp.PIPE, stderr=subp.PIPE)
        out, err = pipe.communicate()
        out = out.rstrip() or None
        err = err.rstrip() or None
        return out, err, pipe.returncode

    def get_command(self, user_input):
        """
        Return a tuple ([command, to, execute], "stdin")
        """
        raise NotImplementedError('Must be implemented in subclass')

    def analyze(self, out, err, returncode):
        ret = {
            'goto_next': False,
            'hint': None,
            'ok_text': out,
            'err_text': err,
        }
        if out and out.lower() == self.expected_out:
            ret['hint'] = self.on_success_hint
            ret['goto_next'] = True
        elif err:
            ret['hint'] = self.on_err_hint
        else:
            ret['hint'] = self.on_wrong_out_hint
        return dotdict(ret)

    def get_task(self):
        return self.__doc__
