# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject -- Repeat a list of sub-steps
# :Created:   sab 21 mag 2016 14:00:00 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017, 2018, 2024 Lele Gaifax
#

from questionary import prompt

from . import Step, run_steps


class Repeat(Step):
    def __init__(self, state, config):
        super().__init__(state, config)
        self.description = config.get('description')
        self.answers_name = config.get('answers')
        self.count = config.get('count')
        self.until = config.get('until')
        self.steps = config['steps']
        self.again_message = config.get('again_message', 'Another loop?')

    def announce(self):
        if self.description:
            print("\n%s\n" % self.description)

    def __call__(self, defaults, prompt_only=False, no_prompt=False):
        if self.answers_name:
            answers = self.state.answers[self.answers_name] = []
            register_answers = answers.append
        else:
            def register_answers(answers):
                raise RuntimeError('Missing "answers" name in config')

        if self.count:
            for _i in range(self.count):
                run_steps(self.state, self.steps, {}, register_answers,
                          prompt_only=prompt_only, no_prompt=no_prompt)
        else:
            while True:
                run_steps(self.state, self.steps, {}, register_answers,
                          prompt_only=prompt_only, no_prompt=no_prompt)
                if self.until:
                    if not self.state.check(self.until):
                        break
                else:
                    again = prompt(dict(type='confirm',
                                        name='again',
                                        message=self.again_message))['again']
                    if not again:
                        break
