from discord import Embed

from src.utils.funcs import timeStrToDatetime


def push(data):
    headcommit = data["head_commit"]
    commits = data["commits"]
    e = Embed(
        title=f"{len(commits)} New Commit{'' if len(commits) == 1 else 's'}",
        description=headcommit['url']
    )
    e.set_author(name=data["repository"]["full_name"] + f" ({data['ref']})",
                 icon_url="https://media.discordapp.net/attachments/771698457391136798/927918869702647808/github.png")
    for commit in commits:
        user = commit["committer"]["username"]
        message = commit["message"].replace("_", "\_").replace("*", "\*")
        e.description += f"\n`{commit['id'][:7]}...{commit['id'][-7:]}` " + \
                         f"{message[:100] + ('...' if len(message) > 100 else '')} " + \
                         f"- [{user}](https://github.com/{user})"
    e.description = e.description[:2048]
    e.set_footer(text=f"Commit time: {timeStrToDatetime(headcommit['timestamp'])} UTC")
    return e
