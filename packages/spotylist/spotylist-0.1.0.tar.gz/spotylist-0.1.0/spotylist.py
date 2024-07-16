import requests
import click
import os
import json
from tabulate import tabulate

# Spotify API endpoints
BASE_URL = 'https://api.spotify.com/v1'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

# Replace with your actual credentials
CLIENT_ID = 'c1247b9fe96b4f19807cbcfd6cfef701'
CLIENT_SECRET = '786b8525b4fd45168d1af514a487c4fe'

CACHE_FILE = 'spotify_cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

@click.group(help="CLI tool for interacting with Spotify API.")
@click.help_option(help="Show help message.")
def cli():
    pass

@cli.command(help="List albums by artist (basic information).")
@click.argument('artist_name', metavar='<artist_name>')
def albums(artist_name):
    """
    Example:
      spotylist albums "Kanye West"
    """
    click.secho(f"Fetching albums by {artist_name}...", fg='cyan')
    
    access_token = get_access_token()
    if not access_token:
        return

    artist_id = get_artist_id(artist_name, access_token)
    
    if artist_id:
        albums = get_artist_albums(artist_id, access_token)
        if albums:
            click.echo("=" * 60)
            for album in albums:
                truncated_name = click.wrap_text(album['name'], width=50)
                click.echo(f"{click.style(truncated_name, fg='green')}")
        else:
            click.echo(f"No albums found for {artist_name}.", fg='yellow')
    else:
        click.echo(f"Artist '{artist_name}' not found.", fg='red')

@cli.command(help="List albums by artist (detailed information).")
@click.argument('artist_name', metavar='<artist_name>')
def albums_all(artist_name):
    """
    Example:
      spotylist albums-all "Kanye West"
    """
    click.secho(f"Fetching detailed albums by {artist_name}...", fg='cyan')
    
    access_token = get_access_token()
    if not access_token:
        return

    artist_id = get_artist_id(artist_name, access_token)
    
    if artist_id:
        albums = get_artist_albums(artist_id, access_token)
        if albums:
            for album in albums:
                click.echo("=" * 60)
                click.echo(f"Album Name: {click.style(album['name'], fg='green')}")
                click.echo(f"Artists: {', '.join([artist['name'] for artist in album['artists']])}")
                click.echo(f"Release Date: {album['release_date']}")
                click.echo(f"Total Tracks: {album['total_tracks']}")
        else:
            click.echo(f"No albums found for {artist_name}.", fg='yellow')
    else:
        click.echo(f"Artist '{artist_name}' not found.", fg='red')

@cli.command(help="List tracks of an album.")
@click.argument('album_name', metavar='<album_name>')
def tracks(album_name):
    """
    Example:
      spotylist tracks "My Beautiful Dark Twisted Fantasy"
    """
    click.secho(f"Fetching tracks for '{album_name}'...", fg='cyan')
    
    access_token = get_access_token()
    if not access_token:
        return

    album_id = get_album_id(album_name, access_token)
    
    if album_id:
        tracks = get_album_tracks(album_id, access_token)
        if tracks:
            click.echo("=" * 60)
            for track in tracks:
                click.echo(f"Track Name: {click.style(track['name'], fg='green')}")
                if 'popularity' in track:
                    click.echo(f"Popularity: {track['popularity']}")
        else:
            click.echo(f"No tracks found for '{album_name}'.", fg='yellow')
    else:
        click.echo(f"Album '{album_name}' not found.", fg='red')


@cli.command(help="Search for artists.")
@click.argument('query', metavar='<query>')
def searchartist(query):
    """
    Example:
      spotylist searchartist "Kanye"
    """
    click.secho(f"Searching for artists with query: {query}...", fg='cyan')

    access_token = get_access_token()
    if not access_token:
        return

    artists = search_artists(query, access_token)

    if artists:
        click.echo("=" * 60)
        for artist in artists:
            click.echo(f"Artist Name: {click.style(artist['name'], fg='green')}")
    else:
        click.echo(f"No results found for '{query}'.", fg='yellow')

@cli.command(help="Display main information about an artist.")
@click.argument('artist_name', metavar='<artist_name>')
def artist(artist_name):
    """
    Example:
      spotylist artist "Kanye West"
    """
    click.secho(f"Fetching artist information for {artist_name}...", fg='cyan')

    access_token = get_access_token()
    if not access_token:
        return

    artist_info = get_artist_info(artist_name, access_token)

    if artist_info:
        click.echo("=" * 60)
        click.echo(f"Artist Name: {click.style(artist_info['name'], fg='green')}")
        click.echo(f"Genres: {', '.join(artist_info['genres'])}")
        click.echo(f"Popularity: {artist_info['popularity']}")
        click.echo(f"Followers: {artist_info['followers']}")
    else:
        click.echo(f"Artist '{artist_name}' not found.", fg='red')

@cli.command(help="Search for tracks.")
@click.argument('query', metavar='<query>')
def searchtrack(query):
    """
    Example:
      spotylist searchtrack "Stronger"
    """
    click.secho(f"Searching for tracks with query: {query}...", fg='cyan')

    access_token = get_access_token()
    if not access_token:
        return

    tracks = search_tracks(query, access_token)

    if tracks:
        click.echo("=" * 60)
        for track in tracks:
            click.echo(f"Track Name: {click.style(track['name'], fg='green')}")
            click.echo(f"Album: {track['album']['name']}")
            artists = ', '.join([click.style(artist['name'], fg='blue') for artist in track['artists']])
            click.echo(f"Artists: {artists}")
    else:
        click.echo(f"No results found for '{query}'.", fg='yellow')

@cli.command(help="List albums by artist and save to file.")
@click.argument('artist_name', metavar='<artist_name>')
@click.argument('file_name', metavar='<file_name>')
def albums_save(artist_name, file_name):
    """
    Example:
      spotylist albums-save "Kanye West" "kanye_albums"
    """
    if not file_name.endswith('.txt'):
        file_name += '.txt'

    click.secho(f"Fetching albums by {artist_name}...", fg='cyan')

    access_token = get_access_token()
    if not access_token:
        return

    artist_id = get_artist_id(artist_name, access_token)

    if artist_id:
        albums = get_artist_albums(artist_id, access_token)
        if albums:
            with open(file_name, 'w', encoding='utf-8') as f:
                for album in albums:
                    f.write(f"{album['name']}\n")
            click.echo(f"Albums saved to {file_name}.")
        else:
            click.echo(f"No albums found for {artist_name}.", fg='yellow')
    else:
        click.echo(f"Artist '{artist_name}' not found.", fg='red')


@cli.command(help="Search for playlists.")
@click.argument('query', metavar='<query>')
def searchplaylist(query):
    """
    Example:
      spotylist searchplaylist "Chill"
    """
    click.secho(f"Searching for playlists with query: {query}...", fg='cyan')
    
    access_token = get_access_token()
    if not access_token:
        return

    playlists = search_playlists(query, access_token)
    
    if playlists:
        click.echo("=" * 60)
        for playlist in playlists:
            click.echo(f"Playlist Name: {click.style(playlist['name'], fg='green')}")
            click.echo(f"Description: {playlist['description']}")
            click.echo(f"Owner: {playlist['owner']['display_name']}")
    else:
        click.echo(f"No results found for '{query}'.", fg='yellow')

def get_access_token():
    """Retrieve access token using client credentials flow."""
    try:
        auth_response = requests.post(TOKEN_URL, {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        })
        auth_response.raise_for_status()
        auth_response_data = auth_response.json()
        return auth_response_data['access_token']
    except requests.exceptions.HTTPError as err:
        click.secho(f"HTTP error occurred: {err}", fg='red')
    except Exception as err:
        click.secho(f"An error occurred: {err}", fg='red')
    return None

def get_artist_id(artist_name, access_token):
    """Retrieve Spotify ID of the artist."""
    cache = load_cache()
    if artist_name in cache:
        return cache[artist_name]['id']
    
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'q': artist_name,
        'type': 'artist',
    }
    try:
        response = requests.get(f"{BASE_URL}/search", headers=headers, params=params)
        response.raise_for_status()
        response_data = response.json()
        artists = response_data.get('artists', {}).get('items', [])
        if artists:
            artist_id = artists[0]['id']
            cache[artist_name] = {'id': artist_id}
            save_cache(cache)
            return artist_id
    except requests.exceptions.HTTPError as err:
        click.secho(f"HTTP error occurred: {err}", fg='red')
    except Exception as err:
        click.secho(f"An error occurred: {err}", fg='red')
    return None

def get_artist_info(artist_name, access_token):
    """Retrieve main information about the artist."""
    cache = load_cache()
    if artist_name in cache and 'info' in cache[artist_name]:
        return cache[artist_name]['info']

    artist_id = get_artist_id(artist_name, access_token)
    if not artist_id:
        return None

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    try:
        response = requests.get(f"{BASE_URL}/artists/{artist_id}", headers=headers)
        response.raise_for_status()
        artist_info = response.json()
        cache[artist_name] = cache.get(artist_name, {})
        cache[artist_name]['info'] = {
            'name': artist_info['name'],
            'genres': artist_info['genres'],
            'popularity': artist_info['popularity'],
            'followers': artist_info['followers']['total'],
        }
        save_cache(cache)
        return cache[artist_name]['info']
    except requests.exceptions.HTTPError as err:
        click.secho(f"HTTP error occurred: {err}", fg='red')
    except Exception as err:
        click.secho(f"An error occurred: {err}", fg='red')
    return None

def get_artist_albums(artist_id, access_token):
    """Retrieve albums by artist with pagination support."""
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    albums = []
    url = f"{BASE_URL}/artists/{artist_id}/albums"
    while url:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            albums.extend(response_data.get('items', []))
            url = response_data.get('next')
        except requests.exceptions.HTTPError as err:
            click.secho(f"HTTP error occurred: {err}", fg='red')
            break
        except Exception as err:
            click.secho(f"An error occurred: {err}", fg='red')
            break
    return albums

def get_album_id(album_name, access_token):
    """Retrieve Spotify ID of the album."""
    cache = load_cache()
    if album_name in cache:
        return cache[album_name]['id']
    
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'q': album_name,
        'type': 'album',
    }
    try:
        response = requests.get(f"{BASE_URL}/search", headers=headers, params=params)
        response.raise_for_status()
        response_data = response.json()
        albums = response_data.get('albums', {}).get('items', [])
        if albums:
            album_id = albums[0]['id']
            cache[album_name] = {'id': album_id}
            save_cache(cache)
            return album_id
    except requests.exceptions.HTTPError as err:
        click.secho(f"HTTP error occurred: {err}", fg='red')
    except Exception as err:
        click.secho(f"An error occurred: {err}", fg='red')
    return None

def get_album_tracks(album_id, access_token):
    """Retrieve tracks of the album."""
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    try:
        response = requests.get(f"{BASE_URL}/albums/{album_id}/tracks", headers=headers)
        response.raise_for_status()
        response_data = response.json()
        tracks = response_data.get('items', [])
        return tracks
    except requests.exceptions.HTTPError as err:
        click.secho(f"HTTP error occurred: {err}", fg='red')
    except Exception as err:
        click.secho(f"An error occurred: {err}", fg='red')
    return []

def search_artists(query, access_token):
    """Search for artists."""
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'q': query,
        'type': 'artist',
    }
    try:
        response = requests.get(f"{BASE_URL}/search", headers=headers, params=params)
        response.raise_for_status()
        response_data = response.json()
        artists = response_data.get('artists', {}).get('items', [])
        return artists
    except requests.exceptions.HTTPError as err:
        click.secho(f"HTTP error occurred: {err}", fg='red')
    except Exception as err:
        click.secho(f"An error occurred: {err}", fg='red')
    return []

def search_tracks(query, access_token):
    """Search for tracks."""
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'q': query,
        'type': 'track',
    }
    try:
        response = requests.get(f"{BASE_URL}/search", headers=headers, params=params)
        response.raise_for_status()
        response_data = response.json()
        tracks = response_data.get('tracks', {}).get('items', [])
        return tracks
    except requests.exceptions.HTTPError as err:
        click.secho(f"HTTP error occurred: {err}", fg='red')
    except Exception as err:
        click.secho(f"An error occurred: {err}", fg='red')
    return []

def search_playlists(query, access_token):
    """Search for playlists."""
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    params = {
        'q': query,
        'type': 'playlist',
    }
    try:
        response = requests.get(f"{BASE_URL}/search", headers=headers, params=params)
        response.raise_for_status()
        response_data = response.json()
        playlists = response_data.get('playlists', {}).get('items', [])
        return playlists
    except requests.exceptions.HTTPError as err:
        click.secho(f"HTTP error occurred: {err}", fg='red')
    except Exception as err:
        click.secho(f"An error occurred: {err}", fg='red')
    return []

if __name__ == '__main__':
    cli()