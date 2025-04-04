import requests
from bs4 import BeautifulSoup
import json
import csv
import re


default_image_url="https://t4.ftcdn.net/jpg/12/06/04/67/240_F_1206046749_MdaIPC3LiU3M113XON2NikeVu3QwNFZt.jpg"

def get_first_movie_image(movie_name): 
    imdb_url = f"https://www.imdb.com/find/?q={movie_name}&ref_=nv_sr_sm"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.imdb.com/"
    }
    response = requests.get(imdb_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch IMDb page. Status Code: {response.status_code}")
        return default_image_url
    soup = BeautifulSoup(response.text, "html.parser")
    target_div = soup.find_all("div", class_="sc-b03627f1-2 gWHDBT")
    target_div = target_div[1]
    if not target_div:
        print("Div with class 'sc-b03627f1-2 gWHDBT' not found.")
        return default_image_url
    first_li = target_div.find("ul").find("li") if target_div.find("ul") else None
    if not first_li:
        print("No <li> elements found inside <ul>.")
        return default_image_url
    img_tag = first_li.find("img")
    if img_tag and "src" in img_tag.attrs:
        return img_tag["src"]
    return default_image_url
    

def scrape_list_page(url, visited=None):
    if visited is None:
        visited = set()  # Initialize visited set

    """
    Scrape the list pages to find final song metadata URLs.
    Returns only the first 2 URLs plus the specific URL you want.
    """
    if url in visited:
        return []  # Avoid infinite loops

    visited.add(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    song_links = []
    final_song_links = []

    # Find all song and list page links
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.startswith('/file/'):  # Found a final song page
            final_song_links.append(f"https://mazafree.com{href}")
        elif href.startswith('/list/'):  # Found another list page
            song_links.append(f"https://mazafree.com{href}")

    # Remove duplicates from final_song_links using a set
    final_song_links = list(set(final_song_links))

    # Recursively process the first 2 list pages
    for link in song_links[:2]:
        final_song_links.extend(scrape_list_page(link, visited))

    # Return only unique final song links
    return list(set(final_song_links))


# Step 2: Scrape song details from the final metadata page (unchanged)
def scrape_song_details(song_url):
    print(song_url)
    """
    Extract metadata from the final song page.
    """
    response = requests.get(song_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    metadata = {
            "name": "",
            "movie": "",
            "artists": [],
            "year": "",
            "file_size": "",
            "genres": [],
            "banner_img": "",
            "source": song_url
    }

    # Extract metadata from the final page
    breadcrumbs = soup.select('h1')  # Get all links in breadcrumb
    if len(breadcrumbs) > 0:
        print("breadcrumbs",breadcrumbs)
        # metadata['name'] = breadcrumbs[-1].get_text(strip=True).replace('Mp3 Song', '').strip()
        breadcrumb_text = breadcrumbs[-1].get_text(strip=True).replace('Mp3 Song', '').strip()
        breadcrumb_text = breadcrumb_text.replace('Free Download', '').strip()
    
    # Split the breadcrumb text into song and movie name
        parts = breadcrumb_text.split(' - ')
    
        if len(parts) > 1:
            song_name = parts[0].strip()
            movie_name_text = parts[1].strip()
        else:
            song_name = parts[0].strip()
            movie_name_text = '' 
        metadata['name'] = song_name
        movie_name = re.sub(r' \d+ Kbps\.mp3$', '', movie_name_text)
        metadata['movie'] = movie_name
        metadata['banner_img'] = get_first_movie_image(movie_name)

    if len(breadcrumbs) > 1:
        metadata['movie'] = breadcrumbs[-2].get_text(strip=True).replace('Mp3 Songs', '').strip()
    file_size = soup.select('center > strong') 
    if file_size:
        # metadata['file_size'] = file_size[0].get_text(strip=True)
        file_size_text = file_size[0].get_text(strip=True)
        metadata['file_size'] = file_size_text.strip('[]').strip()  # Remove extra brackets and spaces if present
    # Extract artists (from the center tag with artist links)
    artist_center = soup.select('center > b > font > a')
    if artist_center:
    # Filter links to only include those with 'artistlist.php' in the href attribute
        artist_links = [artist for artist in artist_center if 'artistlist.php' in artist['href']]
    
    # Store artist names (text) in the metadata dictionary
        metadata['artists'] = [artist.get_text(strip=True) for artist in artist_links]

    # Extract year (from the center tag with year)

    year_center = soup.select_one('center:contains("[Year:") b font')
    if year_center:
        year_text = year_center.get_text(strip=True)
        metadata['year'] = year_text

        # if 'Year:' in year_text:

    # Extract download link and file size
    download_div = soup.find('div', class_='download')
    if download_div:
        download_link = download_div.find('a', href=True)
        if download_link:
            metadata['download_link'] = download_link['href']
            # File size might be in the related files section
            size_tag = soup.find('small')
            if size_tag:
                metadata['file_size'] = size_tag.get_text(strip=True).strip('[]')

    # Extract audio source (from video tag)
    video_tag = soup.find('video')
    if video_tag and video_tag.find('source'):
        metadata['audio_source'] = video_tag.find('source')['src']

    # Extract related files
    related_files = []
    for item in soup.select('div.listing2 a.item'):
        file_name = item.get_text(strip=True)
        file_url = item['href']
        related_files.append({
            'name': file_name,
            'url': f"https://mazafree.com{file_url}" if file_url.startswith('/') else file_url
        })
    metadata['related_files'] = related_files

    return metadata


def save_metadata_to_csv(metadata_list, filename="songs_metadata.csv"):
    if not metadata_list:
        print("No metadata to save.")
        return

    # Define CSV headers
    headers = ["name", "movie", "artists", "year", "file_size", "genres", 
               "banner_img", "source", "audio_source", "related_files"]

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for item in metadata_list:
            metadata = item.get("metadata", {})  # Extract the metadata dictionary
            
            # Convert lists to comma-separated strings
            metadata["artists"] = ", ".join(metadata.get("artists", []))
            metadata["genres"] = ", ".join(metadata.get("genres", []))
            
            # Extract related files and store them as a comma-separated string
            related_files = metadata.get("related_files", [])
            metadata["related_files"] = ", ".join([rf["name"] for rf in related_files])

            # Write the row to the CSV
            writer.writerow({
                "name": metadata.get("name", ""),
                "movie": metadata.get("movie", ""),
                "artists": metadata["artists"],
                "year": metadata.get("year", ""),
                "file_size": metadata.get("file_size", ""),
                "genres": metadata["genres"],
                "banner_img": metadata.get("banner_img", ""),
                "source": metadata.get("source", ""),
                "audio_source": metadata.get("audio_source", ""),
                "related_files": metadata["related_files"]
            })

    print(f"Saved metadata to {filename}")

def main():
    start_url = "https://mazafree.com/list/1/mp3-audio-songs.html"
    final_song_urls = scrape_list_page(start_url)  # Get only the first 2 URLs plus the specific one
    print(len(final_song_urls))
    all_songs_metadata = []

    for song_url in final_song_urls:
        try:
            song_metadata = scrape_song_details(song_url)
            all_songs_metadata.append(song_metadata)
            
            # Print metadata for each song
            print(f"Scraped: {song_url}")
            print(json.dumps(song_metadata, indent=4))
            print("\n" + "="*50 + "\n")
        except Exception as e:
            print(f"Error scraping {song_url}: {str(e)}")

    # Save metadata to JSON file
    # with open('songs_metadata.json', 'w') as f:
    #     json.dump(all_songs_metadata, f, indent=4)

    # Save metadata to CSV file
    # save_metadata_to_csv(all_songs_metadata)

    print(f"Saved metadata for {len(all_songs_metadata)} songs")

if __name__ == '__main__':
    main()
    # soup = get_first_movie_image("Don")
    # print(soup)