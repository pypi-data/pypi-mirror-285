# Spotify CLI Tool


A command-line interface (CLI) tool for interacting with the Spotify API. Perform various tasks such as searching for artists, listing albums, retrieving tracks, and more directly from your terminal.

## Features
- Search for artists by name.
- List albums by artist, including basic and detailed information.
- List tracks from a specific album.
- Search for tracks by name.
- Save album lists to a text file.

## Installation
Ensure you have Python 3.6 or higher installed.

Install the CLI tool:
```sh
pip install spotylist
```
# Usage
### Commands
Search for Artists:

```sh
spotylist searchartist "Artist Name"
```

List Albums (Basic Information):

```sh
spotylist albums "Artist Name"
```

List Albums (Detailed Information):

```sh
spotylist albums-all "Artist Name"
```

List Tracks of an Album:

```sh
spotylist tracks "Album Name"
```

Search for Tracks:

```sh
spotylist searchtrack "Track Name"
```

Save Albums to File:

```sh
spotylist albums-save "Artist Name" "filename"
```

### Examples
List albums by Kanye West:

```sh
spotylist albums "Kanye West"
```

Search for tracks named "Stronger":

```sh
spotylist searchtrack "Stronger"
```

Save albums by Kendrick Lamar to a file named kendrick_albums.txt:

```sh
spotylist albums-save "Kendrick Lamar" kendrick_albums
```


## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- Click - Command line interface creation kit.
- Requests - HTTP library for making requests.
- Tabulate - Pretty-print tabular data.
## Contributing
Contributions are welcome! Please feel free to fork the repository and submit pull requests.