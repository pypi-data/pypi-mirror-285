from pydub import AudioSegment
from pydub.utils import make_chunks
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from pyDataverse.api import DataAccessApi, SearchApi
from pyDataverse.api import NativeApi
import base64
import hashlib 
import requests
import os
import jwt
import subprocess
import json
import subprocess as sp
import time
import jwt

class MuseModalities():
    def __init__(self, config, folder=False, ingest=False, debug=False):
        self.DEBUG = debug
        self.ALGO = "HS256"
        self.DEFAULT_LENGTH = 300000
        self.TMPDIR = '/tmp'
        self.config = {}
        self.modalities = {'interviews': 'What authors and creators think about this topic', 'reviews': 'What other people think about this topic', 'books': 'Books if available', 'songs': 'Song if available', 'lyrics': 'Lyrics if available', 'movie': 'Movie if available', 'wikipedia': 'WikiPedia references if available', 'wikidata': 'WikiData entities if available'}
        self.list = {}
        self.transcript = {}
        self.references = {}
        self.comments = {}
        self.metadata = {}
        self.rawlist = []
        
        if config:
            self.config = config
            self.dataversesearch = SearchApi(self.config['ROOT'], self.config['API_TOKEN'])
            self.dataverse_native_api = NativeApi(self.config['ROOT'], self.config['API_TOKEN'])
        else:
            self.dataversesearch = None
            self.dataverse_native_api = None
            
        if folder:
            self.TMPDIR = folder

    def path_encoder(self, input):
        encoded_jwt = jwt.encode(input, "secret", algorithm=self.ALGO)
        return encoded_jwt

    def path_decoder(self, encoded_jwt):
        return jwt.decode(encoded_jwt, "secret", algorithms=[self.ALGO])

    def set_references(self, references):
        self.references = references
        return

    def set_transcript(self, transcript):
        self.transcript = transcript
        return

    def set_comments(self, comments):
        self.comments = comments
        return

    def set_playlist(self, playlist):
        self.rawlist = []
        for item in playlist:
            if 'videoId' in item:
                self.rawlist.append(item['videoId'])
                self.metadata[item['videoId']] = item
        self.playlist = playlist
        return self.rawlist

    def set_searchlist(self, videos):
        self.rawlist = []
        for item in videos['items']:
            if 'videoId' in item['id']:
                self.rawlist.append(item['id']['videoId'])
        return self.rawlist

    def make_file_metadata(self, repo_name, file, url):
        metadata = {}
    
        metadata['description'] = file
        metadata['filename'] = url
        metadata['datafile_id'] = hashlib.md5(url.encode("utf-8"))
        metadata['dataset_id'] = hashlib.md5(repo_name.encode("utf-8"))
        return metadata

    def supersearch(self, query, channel=None):
        data = {}
        if 'SUPERSEARCH_API' in self.config:
            for modality in self.modalities:
                q = "%s intitle:%s" % (modality, query)
                searchurl = "%s/supersearch?query=%s&period=a" % (self.config['SUPERSEARCH_API'], q)
                info = {}
                info['description'] = self.modalities[modality]
                info['references'] = requests.get(searchurl).json()
                data[modality] = info
            return data
        else:
            return data
        
    def split_wav_file(self, file_path, segment_length_ms):
        audio = AudioSegment.from_wav(file_path)
        total_length_ms = len(audio)
        
        segments = []
        for i in range(0, total_length_ms, segment_length_ms):
            segment = audio[i:i + segment_length_ms]
            segments.append(segment)
        
        return segments
    
    def convert_wav_to_mp3(self, wav_file_path, mp3_file_path):
        audio = AudioSegment.from_wav(wav_file_path)
        audio.export(mp3_file_path, format="mp3")
    
        # Example usage:
        #wav_file_path = "/tmp/ZOOM0002.WAV"
        segment_length_ms = self.DEFAULT_LENGTH  # Split into 1-minute segments
        #segments = split_wav_file(wav_file_path, segment_length_ms)
        
        # Save and convert the segments
        output_dir = "output_segments"
        os.makedirs(output_dir, exist_ok=True)
        chunks = make_chunks(audio,segment_length_ms) #Make chunks of one sec 
        print(len(chunks))
        print(chunks)
        for i, chunk in enumerate(chunks): 
        #for i, segment in enumerate(segments):
            print(i)
            wav_segment_path = os.path.join(output_dir, f"segment_{i}.wav")
            mp3_segment_path = os.path.join(output_dir, f"segment_{i}.mp3")
            chunk.export(wav_segment_path, format="wav")
            #self.convert_wav_to_mp3(wav_segment_path, mp3_segment_path)
            #i = i + 1

    def get_video_info(self, url):
        command = [
            'yt-dlp',
            '--dump-json',
            url
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            video_info = json.loads(result.stdout)
            return video_info
        else:
            print("Failed to retrieve video information")
            print(result.stderr)
            return None

    def get_video(self, url):
        command = [
            'yt-dlp',
            '-x',
            '--audio-format',
            'wav',
            '-P',
            self.TMPDIR,
            '-o',
            '%(id)s',
            url
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            video_info = json.loads(result.stdout)
            return video_info
        else:
            print("Failed to retrieve video information")
            print(result.stderr)
            return None

    def ldrecord(self, videoID, video_info, pubdate=None, countries=None):
        voc = {}
        if not 'http' in videoID:
            URL = "https://www.youtube.com/watch?v=%s" % videoID
        else:
            URL = videoID
            
        if video_info:
            data = video_info['snippet']
            statistics = video_info['statistics']
            content_details = video_info['contentDetails']
            thumbnails = data['thumbnails']
            if 'maxres' in thumbnails:
                data['image'] = thumbnails['maxres']['url']

            voc['http://purl.org/dc/terms/title'] = data['title']
            voc["https://dataverse.org/schema/core#restrictions"] = "No restrictions"
            voc["https://dataverse.org/schema/citation/license#uri"] = "http://creativecommons.org/publicdomain/zero/1.0"
            voc["https://dataverse.org/schema/citation/license#name"] = "CC0 1.0"
            voc["http://schema.org/license"] = "http://creativecommons.org/publicdomain/zero/1.0"
            if 'subject' in data:
                voc['http://purl.org/dc/terms/subject'] = data['subject']
            else:
                voc['http://purl.org/dc/terms/subject'] = "Medicine, Health and Life Sciences"
            creator = {}
            creator['https://dataverse.org/schema/citation/authorName'] = 'MuseIT'
            creator['https://dataverse.org/schema/citation/authorAffiliation'] = 'MuseIT'
            voc['http://purl.org/dc/terms/creator'] = creator
            contact = {}
            contact['https://dataverse.org/schema/citation/datasetContactEmail'] = 'finch@mailinator.com'
            contact['https://dataverse.org/schema/citation/datasetContactName'] = 'MuseIT'
            voc['https://dataverse.org/schema/citation/datasetContact'] = contact
            desc = {}
            desc['https://dataverse.org/schema/citation/dsDescriptionValue'] = data['description']
            voc['https://dataverse.org/schema/citation/dsDescription'] = desc
            if pubdate:
                voc['https://dataverse.org/schema/citation/dsDescriptionDate'] = pubdate
            #if 'image' in data:
            #    voc['https://schema.org/distribution'] = data['image']
            if URL:
                publication = {}
                publication['https://schema.org/distribution'] = URL
                voc['http://purl.org/dc/terms/isReferencedBy'] = publication
                voc['https://dataverse.org/schema/citation/alternativeURL'] = publication
            
            if 'language' in data:
                if data['language'] in countries:
                    voc['https://dataverse.org/schema/citation/productionPlace'] = [ countries[data['language']] ]
            if 'channelId' in data:
                voc['https://dataverse.org/schema/citation/distributorURL'] = "https://www.youtube.com/channel/%s" % data['channelId']
            if 'channelTitle' in data:
                voc['https://dataverse.org/schema/citation/distributorName'] = data['channelTitle']
        
            keywords = []
            keyword= {}
            alltags = []
            if 'tags' in data:
                alltags = data['tags']#.split(', ')
            else:
                try:
                    tags = data['text']
                    for tag in {tag.strip("#") for tag in tags.split() if tag.startswith("#")}:
                        alltags.append(tag)
                except:
                    skip = True
        
            for tag in alltags:
                #print(tag)
                keyword= {}
                keyword['https://dataverse.org/schema/citation/keywordValue'] = tag
                keywords.append(keyword)
            if keywords:
                voc['https://dataverse.org/schema/citation/keyword'] = keywords
        return voc
        
    def dataset_upload(self, data, config=None):
        headers = { "X-Dataverse-key" : self.config['API_TOKEN'], 'Content-Type' : 'application/ld+json'}
        url = "%s/%s" % (self.config['ROOT'], "api/dataverses/%s/datasets" % self.config['DATAVERSE_ID'])
        print(url)
        r = requests.post(url, data=json.dumps(data), headers=headers)
        try:
            return json.loads(r.text) 
        except:
            return

    def upload_datafile(self, pid, filename, content):
        metainfo = {"contentType": "json", 'description': 'References, Internet'}
        native_api = NativeApi(self.config['ROOT'], self.config['API_TOKEN'])
        filename = "%s_%s" % (pid.split('/')[-1], filename)
        if 'references' in filename:
            content['pid'] = pid
            metainfo['categories'] = ['social','web','references']
            metainfo['description'] = 'References and citations from Internet'
        elif 'comments' in filename:
            newcontent = {'pid': pid}
            newcontent['comments'] = content
            content = newcontent
            metainfo['categories'] = ['comments','reactions','reviews']
            metainfo['description'] = 'Social media feedback'
        else:
            newcontent = {'pid': pid}
            newcontent['transcript'] = content
            content = newcontent
            metainfo['categories'] = ['transcript', 'speech']
            metainfo['description'] = 'Automated transcript from speech to text not verified by human.'
        with open(filename, "w") as datafile:
            json.dump(content, datafile, indent=4, sort_keys=True)
        try:
            native_api.upload_datafile(pid, filename, json.dumps(metainfo))
            return True
        except:
            return False

class YoutubeModality():
    def __init__(self, config, debug=False):
        self.DEBUG = debug
        self.config = config
        
    def get_video_details(self, video_id):
        youtube = build('youtube', 'v3', developerKey=self.config['YOUTUBE_API_KEY'])
        
        # Call the API's videos.list method to retrieve video details
        request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        )
        response = request.execute()
        
        # Extracting the information
        if 'items' in response and len(response['items']) > 0:
            video_info = response['items'][0]
            return video_info
        else:
            return None
            
    def search_videos(self, query, contenttype='video', limit=10):
        youtube = build('youtube', 'v3', developerKey=self.config['YOUTUBE_API_KEY'])
        
        # Call the API's search.list method to retrieve search results
        request = youtube.search().list(
            part='snippet',
            q=query,
            type=contenttype,  # Restrict to video results
            maxResults=limit  # Number of results to retrieve
        )
        response = request.execute()
        
        return response

    def search_all_videos(self, query, contenttype='video', limit=10):
        youtube = build('youtube', 'v3', developerKey=self.config['YOUTUBE_API_KEY'])
        videos = []
        next_page_token = None
        
        while True:
            # Call the API's search.list method to retrieve search results
            request = youtube.search().list(
                part='snippet',
                q=query,
                type=contenttype,  # Restrict to video results
                maxResults=limit,  # Number of results to retrieve per request
                pageToken=next_page_token
            )
            response = request.execute()
            
            # Append the retrieved videos to the list
            videos.extend(response['items'])
            
            # Get the next page token, if any
            next_page_token = response.get('nextPageToken')
            
            # Break the loop if there are no more pages left
            if not next_page_token:
                break
        
        return videos

    def playlist_videos(self, playlist_id):
        youtube = build('youtube', 'v3', developerKey=self.config['YOUTUBE_API_KEY'])
        
        # List to store video details
        videos = []
        
        # API request to get playlist items
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50  # You can adjust this number as needed
        )
        
        while request:
            response = request.execute()
            
            for item in response['items']:
                snippet = item['snippet']
                video_details = {
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'videoId': snippet['resourceId']['videoId'],
                    'publishedAt': snippet['publishedAt'],
                    'channelTitle': snippet['channelTitle']
                }
                videos.append(video_details)
            
            # Get the next page token, if any
            request = youtube.playlistItems().list_next(request, response)
        
        return videos

    def full_transcript(self, video_id):
        try:
            # Fetch the transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
            # Print the transcript
            for entry in transcript:
                print(f"{entry['start']} - {entry['duration']} : {entry['text']}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def video_comments(self, video_id):
        youtube = build('youtube', 'v3', developerKey=self.config['YOUTUBE_API_KEY'])
        
        comments = []
        next_page_token = None
        
        while True:
            # Call the API's commentThreads.list method to retrieve comments
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=100,  # Number of results to retrieve per request (max is 100)
                pageToken=next_page_token,
                textFormat='plainText'
            )
            response = request.execute()
            
            # Append the retrieved comments to the list
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'author': comment['authorDisplayName'],
                    'text': comment['textDisplay'],
                    'published_at': comment['publishedAt'],
                    'like_count': comment['likeCount']
                })
            
            # Get the next page token, if any
            next_page_token = response.get('nextPageToken')
            
            # Break the loop if there are no more pages left
            if not next_page_token:
                break
        
        return comments

    def channelname_to_channel_id(self, channel_name):
        youtube = build('youtube', 'v3', developerKey=self.config['YOUTUBE_API_KEY'])
        
        request = youtube.search().list(
            part='snippet',
            q=channel_name,
            type='channel',
            maxResults=1
        )
        response = request.execute()
        
        if response['items']:
            channel_id = response['items'][0]['snippet']['channelId']
            return channel_id
        else:
            return None
        
    def videos_by_channel_id(self, channel_id, limit=50):
        # Build the YouTube service object
        youtube = build('youtube', 'v3', developerKey=self.config['YOUTUBE_API_KEY'])
        
        # Retrieve the uploads playlist ID for the channel
        # Retrieve the uploads playlist ID for the channel
        response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()        
        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Retrieve the videos in the uploads playlist
        videos = []
        next_page_token = None
    
        while True:
            playlist_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=limit,
                pageToken=next_page_token
            ).execute()
    
            for item in playlist_response['items']:
                video_id = item['snippet']['resourceId']['videoId']
                videos.append(video_id)
            
            next_page_token = playlist_response.get('nextPageToken')
    
            if not next_page_token:
                break
    
        return videos
