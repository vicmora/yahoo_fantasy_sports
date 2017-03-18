import json
import time
import webbrowser
from rauth import OAuth1Service
from rauth.utils import parse_utf8_qsl

class YahooFantasySports:
    def __init__(self, credentials_file):
        """
        Authenticate with the Yahoo Fantasy Sports API.
        
        Parameters:
        credentials_file: path to a json file
        """

        # load credentials
        self.credentials_file = open(credentials_file)
        self.credentials = json.load(self.credentials_file)   
        self.credentials_file.close()
    
        # create oauth object
        self.oauth = OAuth1Service(consumer_key = self.credentials['consumer_key'],
                                   consumer_secret = self.credentials['consumer_secret'],
                                   name = "yahoo",
                                   request_token_url = "https://api.login.yahoo.com/oauth/v2/get_request_token",
                                   access_token_url = "https://api.login.yahoo.com/oauth/v2/get_token",
                                   authorize_url = "https://api.login.yahoo.com/oauth/v2/request_auth",
                                   base_url = "http://fantasysports.yahooapis.com/")
        # leg 1
        request_token, request_token_secret = self.oauth.get_request_token(params={"oauth_callback": "oob"})
        
        # leg 2
        authorize_url = self.oauth.get_authorize_url(request_token)
        webbrowser.open(authorize_url)
        verify = input('Enter code: ')

        # leg 3
        raw_access = self.oauth.get_raw_access_token(request_token,
                                            request_token_secret,
                                            params={"oauth_verifier": verify})

        parsed_access_token = parse_utf8_qsl(raw_access.content)
        access_token = (parsed_access_token['oauth_token'], parsed_access_token['oauth_token_secret'])

        # log time
        self.start_time = time.time()
        self.end_time = self.start_time + 3600
        
        # store tokens
        self.credentials['access_token'] = parsed_access_token['oauth_token']
        self.credentials['access_token_secret'] = parsed_access_token['oauth_token_secret']
        self.tokens = (self.credentials['access_token'], self.credentials['access_token_secret'])

        # start session
        self.session = self.oauth.get_session(self.tokens)
    
    def refresh_tokens(self):
        """
        Refresh sessions tokens.
        """


        # refresh a session
        self.tokens = self.oauth.get_access_token(parsed_access_token['oauth_token'],
                                                  parsed_access_token['oauth_token_secret'],
                                                  params={'oauth_session_handle':parsed_access_token['oauth_session_handle']}
                                                 )

        # update stored tokens
        self.credentials['access_token'] = self.tokens[0]
        self.credentials['access_token_secret'] = self.tokens[1]

        # update log time
        self.start_time = time.time()
        self.end_time = self.start_time + 3600

        # start a session with updated tokens
        self.session = self.oauth.get_session(self.tokens)