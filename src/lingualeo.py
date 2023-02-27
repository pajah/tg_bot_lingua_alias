
import json
import requests

import logging


from config import LINGUALEO_EMAIL, LINGUALEO_PASS, LINGUALEO_DYNAMIC_DICT_JSON
from pprint import pprint

logging.basicConfig(level = 1)
logger = logging.getLogger(__name__)

# logger.warning('')

# logger.setlevel = '1'

# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1


class LinguaAPI:
    
    API_URL = 'https://api.lingualeo.com'

    def __init__(self, email=LINGUALEO_EMAIL, password=LINGUALEO_PASS):
        self.email = email
        self.password = password
        self.session = requests.session()

    
    def perform_request(self, path, method, **kwargs):
        logger.debug(
            'request: path: %s , method: %s, data: %s' % (path, method, kwargs.get('params') or kwargs.get('data') or kwargs.get('json')))

        try:
            return self.session.request(method=method, url=self.API_URL + path, **kwargs).json()
        except Exception as e:
            logger.error('error: %s' % e)



    def auth(self):
        params = {'email': self.email, 'password': self.password}
        req = self.perform_request(path='/login',
                                    method='POST',
                                    data=params,
                                    headers={})
        # print(req)


    def is_authorized(self):
        return self.perform_request('/isauthorized', 'POST').get('is_authorized')




    def get_user_dict(self):

        user_dict = []

        def get_words(resp):            
            user_dict = []
            # pprint(resp)
            # for pool in resp:
            #     words = pool.get('words')
            for w in resp:
                # print(w.get('wd'))
                # user_dict.append((w.get('wd'), w.get('tr'), w.get('id')))
                # user_dict.append({w.get('id'):  (w.get('wordValue'), w.get('combinedTranslation'))})
                if (w.get('wordValue'), w.get('combinedTranslation')) not in user_dict:
                	user_dict.append((w.get('wordValue').lower(), w.get('combinedTranslation')))

            return sorted(user_dict)


        # offset = {}
        # wordset_id = 1
        # date_group = 'start'

        # req_params = {
        #     'apiVersion': '1.0.1',
        #     # 'attrList': WORDS_ATTRIBUTE_LIST,
        #     'category': '',
        #     'dateGroup': date_group,
        #     'mode': 'basic',
        #     'perPage': 1000,
        #     # 'status': status,
        #     'offset': offset,
        #     'search': '',
        #     'training': None,
        #     'wordSetId': wordset_id,
        #     'ctx': {
        #     'config': {
        #       'isCheckData': True,
        #       'isLogging': True}
        #       }
        #     }


        # while True:


        #     resp = self.perform_request('/GetWords', 'POST', data=req_params)
        #     # pprint(resp)

        #     req_params['offset'] = {}

        #     for w_group in resp.get('data'):
        #         date_gr = w_group.get('groupName')
        #         req_params['offset'] = {w_group.get('words')[-1].get('id')}
        #         req_params['dateGroup'] = date_gr


        #         words = get_words(resp)        
        #         print(len(words))
        #         print(words[0], '<-- first in resp\n')
        #         print(words[-1], '<-- last in resp\n')
                
                



        #         for pair in words:
        #             # print(pair)
        #             for wid, wordpair in pair.items():
        #                 if wordpair not in user_dict:
        #                     try:
        #                         user_dict.append(wordpair)
        #                         # last_word_id = wid
        #                         # req_params['offset'] = {'wordId': last_word_id}
        #                     except Exception as e:
        #                         print(e)
        #                         # print(pair)
        #                 else:
        #                     break

        # # pprint(user_dict)

        WORDS_ATTRIBUTE_LIST = {'id': 'id', 'wordValue': 'wd', 'origin': 'wo', 'wordType': 'wt',
                                'translations': 'trs', 'wordSets': 'ws', 'created': 'cd',
                                'learningStatus': 'ls', 'progress': 'pi', 'transcription': 'scr',
                                'pronunciation': 'pron', 'relatedWords': 'rw', 'association': 'as',
                                'trainings': 'trainings', 'listWordSets': 'listWordSets',
                                'combinedTranslation': 'trc', 'picture': 'pic', 'speechPartId': 'pid',
                                'wordLemmaId': 'lid', 'wordLemmaValue': 'lwd', 'context': 'ctx'}

        WORDSETS_ATTRIBUTE_LIST = {
			'association': 'as',
			'combinedTranslation': 'trc',
			'created': 'cd',
			'id': 'id',
			'learningStatus': 'ls',
			'listWordSets': 'listWordSets',
			'origin': 'wo',
			'picture': 'pic',
			'progress': 'pi',
			'pronunciation': 'pron',
			'relatedWords': 'rw',
			'speechPartId': 'pid',
			'trainings': 'trainings',
			'transcription': 'scr',
			'translations': 'trs',
			'wordLemmaId': 'lid',
			'wordLemmaValue': 'lwd',
			'wordSets': 'ws',
			'wordType': 'wt',
			'wordValue': 'wd'
		}

        date_group = 'start'
        offset = {}
        values = {
			'apiVersion': '1.0.1',
			'attrList': WORDSETS_ATTRIBUTE_LIST,
			'category': '',
			'dateGroup': date_group,
			'mode': 'basic',
			'perPage': 999,
			'status': '',
			'wordSetId': 1,
			'offset': 0,
			'traiding': 0,
			'search': '',
			'iDs': [{}]
			}

        words = []
        words_received = 0
        extra_date_group = date_group  # to get into the while loop

        # TODO: Refactor while loop (e.g. request words from each group until it is not empty)
        # Request the words until
        while words_received > 0 or extra_date_group:
            if words_received == 0 and extra_date_group:
                values['dateGroup'] = extra_date_group
                extra_date_group = None
            else:
                values['dateGroup'] = date_group
                values['offset'] = offset
            print('group now: %s' % values['dateGroup'])


            response = self.perform_request('/GetWords', 'POST', json=values, 
            							    headers={
            							    	'Content-Type': 'application/json',
            							    	'Accept': 'application/json',
            							    	'Accept-encoding': 'gzip, deflate, br',

											})
            word_groups = response['data']
            # print(word_groups, '\n')
            words_received = 0
            for word_group in word_groups:
                word_chunk = word_group.get('words')
                if word_chunk:
                    words += word_chunk
                    words_received += len(word_chunk)
                    date_group = word_group.get('groupName')
                    offset = {}
                    offset['wordId'] = word_group.get('words')[-1].get('id')
                    # print('last word in chunk: %s' % word_group.get('words')[-1].get('wd'))
                    # print('last word in chunk: %s' % word_group.get('words')[-1].get('id'))
                elif words_received > 0:
                    ''' 
                    If the next word_chunk is empty, and we completed the previous, 
                    next response should be to the next group
                    '''
                    if words_received < 999:
                        date_group = word_group.get('groupName')
                        extra_date_group = None
                        offset = None
                    else:  # words_received == self.WORDS_PER_REQUEST
                        '''We either need to continue with this group or try the next'''
                        extra_date_group = word_group.get('groupName')
                    break
        # pprint(words)
        
        serialized = get_words(words)
        # pprint(serialized)
        print(len(words))
        return(serialized)




def append_new_words(filepath, wordlist):

    # pprint(wordlist)

    with open(filepath, 'r', encoding='utf-8') as fp:
        old_words = json.load(fp)

    pprint(old_words)

    # new_dict = []
    new_word_count = 0
    for wordpair in wordlist:
    # for i in range(5):
        # wordpair = wordlist[i]
        # oldword = old_words[i]
        if list(wordpair) not in old_words:
            # print('\n', '%s not in %s' % (str(wordpair), str(wordlist[:3])))
            # print(tuple(wordpair))
            # print(tuple(oldword))
            old_words.append(wordpair)
            logger.debug('New wordpair added: %s' % str(wordpair))
            new_word_count += 1

    print(new_word_count)
    
    with open(filepath, 'w', encoding='utf-8') as fp:
        json.dump(old_words, fp, indent=4, ensure_ascii=False)
    logger.debug('Updating dinamyc dictionary is finished. Pairs added: %d' % new_word_count)







if __name__ == '__main__':
    api = LinguaAPI()
    api.auth()
    logger.debug('Is authorized: %s' % api.is_authorized())
    userdict = api.get_user_dict()
    append_new_words(LINGUALEO_DYNAMIC_DICT_JSON, userdict)
