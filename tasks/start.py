from invoke import Collection

from tasks.assets import MultiprocessTask

mp_tasks = MultiprocessTask('all')


@mp_tasks.add
def web(c):
    from scrat.web.app import app
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host = '', port = 5000, debug = True)


@mp_tasks.add
def bot(c):
    from scrat.bot.app import run
    run()


start_collection = Collection('start')
mp_tasks.add_to_collection(start_collection)
