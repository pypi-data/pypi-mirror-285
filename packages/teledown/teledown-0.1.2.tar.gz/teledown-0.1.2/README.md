# teledown

teledown is a simple CLI tool for internal use to download videos from Telegram (public/private) channels.

## Features

- List all channels
- Search for channels by name
- Count total videos in a specified channel
- Download videos from a specified channel
- Send a message to yourself

## Installation

(Add installation instructions here, including any dependencies)

## Usage

```
python __main__.py [COMMAND] [OPTIONS] [ARGUMENTS]
```

### Available Commands

1. **message**: Send a message to yourself
   ```
   python __main__.py message "Your message here"
   ```

2. **lists**: List all channels
   ```
   python __main__.py lists
   ```

3. **search**: Search for a channel by name
   ```
   python __main__.py search "channel name"
   ```

4. **count**: Count total videos in the specified channel
   ```
   python __main__.py count CHANNEL_ID [--sort asc|desc]
   ```

5. **download**: Download videos from the specified channel
   ```
   python __main__.py download CHANNEL_ID [OPTIONS]
   ```
   Options:
   - `--limit INTEGER`: Limit the number of videos to download (0 for no limit)
   - `--output-dir PATH`: Directory to save downloaded videos (default: 'downloads')
   - `--resume`: Resume the download from where it stopped
   - `--post-ids TEXT`: Comma-separated list of specific post IDs to download

## Configuration

Before using the tool, make sure to set up your Telegram API credentials in the script:

```python
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
phone_number = 'YOUR_PHONE_NUMBER'
```

## Examples

1. List all channels:
   ```
   python __main__.py lists
   ```

2. Search for a channel:
   ```
   python __main__.py search "news channel"
   ```

3. Count videos in a channel:
   ```
   python __main__.py count 1234567890 --sort desc
   ```

4. Download videos from a channel:
   ```
   python __main__.py download 1234567890 --limit 10 --output-dir "my_videos" --resume
   ```

5. Download specific posts from a channel:
   ```
   python __main__.py download 1234567890 --post-ids "123,456,789"
   ```

## Note

This tool is for internal use only. Make sure you have the necessary permissions to access and download content from the Telegram channels you're interacting with.

## License

(Add license information here)