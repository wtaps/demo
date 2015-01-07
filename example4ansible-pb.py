import ansible.runner
import ansible.playbook
from ansible import callbacks
from ansible import utils
from ansible.inventory import Inventory
from ansible.callbacks import display
from ansible.color import stringc

utils.VERBOSITY = 2 # like -vvv
stats = callbacks.AggregateStats()
playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
inventory = Inventory('hosts')

pb = ansible.playbook.PlayBook(playbook="test.yml",
                               stats=stats,
                               callbacks=playbook_cb,
                               inventory=inventory,
                               runner_callbacks=runner_cb,
                               remote_user='',
                               remote_pass=''
                            )

#for (play_ds, play_basedir) in zip(pb.playbook, pb.play_basedirs):
#    import ipdb
#    ipdb.set_trace()
#    # Can play around here to see what's going on.
ANSIBLE_COLOR = True

def colorize(lead, num, color):
    """ Print 'lead' = 'num' in 'color' """
    if num != 0 and ANSIBLE_COLOR and color is not None:
        return "%s%s%-15s" % (stringc(lead, color), stringc("=", color), stringc(str(num), color))
    else:
        return "%s=%-4s" % (lead, str(num))

def hostcolor(host, stats, color=True):
    if ANSIBLE_COLOR and color:
        if stats['failures'] != 0 or stats['unreachable'] != 0:
            return "%-37s" % stringc(host, 'red')
        elif stats['changed'] != 0:
            return "%-37s" % stringc(host, 'yellow')
        else:
            return "%-37s" % stringc(host, 'green')
    return "%-26s" % host
   

results = pb.run()  # This runs the playbook
print results
failed_hosts = []
unreachable_hosts = []

hosts = sorted(pb.stats.processed.keys())
display(callbacks.banner("PLAY RECAP"))
playbook_cb.on_stats(pb.stats)

for h in hosts:
    t = pb.stats.summarize(h)
    if t['failures'] > 0:
        failed_hosts.append(h)
    if t['unreachable'] > 0:
        unreachable_hosts.append(h)

retries = failed_hosts + unreachable_hosts

if len(retries) > 0:
    filename = pb.generate_retry_inventory(retries)
    if filename:
        display("           to retry, use: --limit @%s\n" % filename)

for h in hosts:
    t = pb.stats.summarize(h)

    display("%s : %s %s %s %s" % (
        hostcolor(h, t),
        colorize('ok', t['ok'], 'green'),
        colorize('changed', t['changed'], 'yellow'),
        colorize('unreachable', t['unreachable'], 'red'),
        colorize('failed', t['failures'], 'red')),
        screen_only=True
    )

    display("%s : %s %s %s %s" % (
        hostcolor(h, t, False),
        colorize('ok', t['ok'], None),
        colorize('changed', t['changed'], None),
        colorize('unreachable', t['unreachable'], None),
        colorize('failed', t['failures'], None)),
        log_only=True
    )

