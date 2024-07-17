import click
import os
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
from tabulate import tabulate
from tqdm.asyncio import tqdm
import json

# Define API credentials
api_id = '23134370'
api_hash = '1ba7aec9b4f45da82c09297397e7a88d'
phone_number = '+66631028299'

# Create the client and connect
client = TelegramClient('teledown', api_id, api_hash)

@click.group()
def cli():
    """A SIMPLE CLI TOOL FOR INTERNAL USE TO DOWNLOAD VIDEO FROM TELEGRAM (PUBLIC/PRIVATE) CHANNEL."""
    pass

@cli.command()
@click.argument('message')
def message(message):
    """Send a message to yourself."""
    with client:
        client.loop.run_until_complete(client.send_message('me', message))
        print("Message sent!")

@cli.command()
def lists():
    """List all channels."""
    async def get_channels():
        await client.start(phone=phone_number)
        dialogs = await client.get_dialogs()
        channels = [d for d in dialogs if d.is_channel]
        for channel in channels:
            username = channel.entity.username if channel.entity.username else "No username"
            print(f'Channel: {channel.name}, ID: {channel.id}, Username: {username})')

    with client:
        client.loop.run_until_complete(get_channels())

@cli.command()
@click.argument('name')
def search(name):
    """Search for a channel by name."""
    async def search_channels(name):
        await client.start(phone=phone_number)
        dialogs = await client.get_dialogs()
        channels = [d for d in dialogs if d.is_channel and name.lower() in d.name.lower()]
        if channels:
            for channel in channels:
                username = channel.entity.username if channel.entity.username else "No username"
                print(f'Found Channel: {channel.name} (ID: {channel.id}, Username: {username})')
        else:
            print(f'No channels found with name containing "{name}".')

    with client:
        client.loop.run_until_complete(search_channels(name))

@cli.command()
@click.argument('channel_id', type=int)
@click.option('--sort', type=click.Choice(['asc', 'desc']), default=None, help='Sort videos by length')
def count(channel_id, sort):
    """Count total videos in the specified channel."""
    async def get_video_count(channel_id, sort):
        await client.start(phone=phone_number)
        channel_entity = await client.get_entity(channel_id)
        videos = []

        async for message in client.iter_messages(channel_id):
            if message.video:
                for attribute in message.video.attributes:
                    if isinstance(attribute, DocumentAttributeVideo):
                        videos.append((message.video, attribute.duration))

        if sort:
            videos.sort(key=lambda v: v[1], reverse=(sort == 'desc'))

        total_videos = len(videos)
        print(f'{total_videos} videos')

    with client:
        client.loop.run_until_complete(get_video_count(channel_id, sort))

def channel_id_type(value):
    try:
        return int(value)
    except ValueError:
        return str(value)

@cli.command()
@click.argument('channel_id', type=channel_id_type)
@click.option('--limit', type=int, default=0, help='Limit the number of videos to download (0 for no limit)')
@click.option('--output-dir', type=click.Path(), default='downloads', help='Directory to save downloaded videos')
@click.option('--resume', is_flag=True, help='Resume the download from where it stopped')
@click.option('--post-ids', type=str, help='Comma-separated list of specific post IDs to download')
@click.option('--progress', type=click.Path(), help='Custom path for the progress file')
def download(channel_id, limit, output_dir, resume, post_ids, progress):
    """Download videos from the specified channel."""
    
    # Determine the progress file path
    if progress:
        progress_file = progress
    else:
        progress_file = os.path.join(os.path.expanduser('~'), "telegram_downloader_progress.json")
    
    async def download(channel_id, limit, output_dir, resume, downloaded_ids, post_ids_list):
        await client.start(phone=phone_number)
        channel_entity = await client.get_entity(channel_id)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        downloaded_count = 0
        downloaded_videos = []

        if post_ids_list:
            # Download specific post IDs
            for post_id in post_ids_list:
                message = await client.get_messages(channel_id, ids=int(post_id))
                if message.video:
                    if message.id in downloaded_ids:
                        continue  # Skip already downloaded videos

                    file_path = os.path.join(output_dir, message.file.name if message.file and message.file.name else f"{message.id}.mp4")
                    with tqdm(total=message.file.size, unit='B', unit_scale=True, unit_divisor=1024, desc=f"Downloading {message.id}") as video_pbar:
                        await message.download_media(file=file_path, progress_callback=lambda d, t: video_pbar.update(d - video_pbar.n))
                    downloaded_videos.append([message.id, file_path])
                    downloaded_ids.add(message.id)
                    downloaded_count += 1

                    # Save progress
                    with open(progress_file, 'w') as f:
                        json.dump(list(downloaded_ids), f)

                    if limit > 0 and downloaded_count >= limit:
                        break
        else:
            # Download videos in general
            async for message in client.iter_messages(channel_id, limit=None if limit == 0 else limit):
                if message.video:
                    if message.id in downloaded_ids:
                        continue  # Skip already downloaded videos

                    file_path = os.path.join(output_dir, message.file.name if message.file and message.file.name else f"{message.id}.mp4")
                    with tqdm(total=message.file.size, unit='B', unit_scale=True, unit_divisor=1024, desc=f"Downloading {message.id}") as video_pbar:
                        await message.download_media(file=file_path, progress_callback=lambda d, t: video_pbar.update(d - video_pbar.n))
                    downloaded_videos.append([message.id, file_path])
                    downloaded_ids.add(message.id)
                    downloaded_count += 1

                    # Save progress
                    with open(progress_file, 'w') as f:
                        json.dump(list(downloaded_ids), f)

                    if limit > 0 and downloaded_count >= limit:
                        break

        table = [["Message ID", "File Path"]]
        table.extend(downloaded_videos)
        print(tabulate(table, headers="firstrow", tablefmt="grid"))
        print(f"Total downloaded videos: {downloaded_count}")

    async def download_with_progress(channel_id, limit, output_dir, resume, post_ids):
        downloaded_ids = set()

        # Load progress if resume is True
        if resume and os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                downloaded_ids = set(json.load(f))

        post_ids_list = [int(id.strip()) for id in post_ids.split(',')] if post_ids else []

        await download(channel_id, limit, output_dir, resume, downloaded_ids, post_ids_list)

    with client:
        client.loop.run_until_complete(download_with_progress(channel_id, limit, output_dir, resume, post_ids))

if __name__ == '__main__':
    cli()