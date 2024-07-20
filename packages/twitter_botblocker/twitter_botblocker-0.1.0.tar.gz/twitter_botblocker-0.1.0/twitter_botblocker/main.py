import asyncio
from twikit import Client
import asyncclick as click
import time
from rich.progress import Progress
from rich.progress import track



# Initialize client
client = Client('en-US')
@click.command()
@click.option('--auth', hide_input=True , prompt='Enter Auth Token',
    help='Can be obtained by opening twitter, going into devmode (Ctrl + Shift + I) and opening Storage -> Cookies on Firefox or Application -> Local Storage on anything Chromium based')
@click.option('--ct', hide_input=True, prompt='Enter ct0',)

async def main(auth,ct):
    spamnumber = 0
    cookies = {
        'auth_token':auth,
        'ct0':ct
    }
    client.set_cookies(cookies)
    id = await client.user_id()
    all_followers = []
    follower_ids = await client.get_followers_ids(id, count=5000)
    all_followers += follower_ids
    while len(follower_ids) > 0:
        try:
            follower_ids = await follower_ids.next()
            all_followers += follower_ids
        except:
            break
    for x in track(all_followers, description="Scanning for bots..."):
        victim = x
        user = await client.get_user_by_id(victim)
        if user.statuses_count < 10:
            print ("blocked " + user.screen_name)
            spamnumber = spamnumber + 1
            await user.block()

    print("Thank you for running BotBlocker! We found and blocked " + str(spamnumber) + " bots! meaning that " + str((round(spamnumber / len(all_followers) * 100))) + "% of your followers were bots! Have a great day!")


if __name__ == '__main__':
    main(_anyio_backend="asyncio")
