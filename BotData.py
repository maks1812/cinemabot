import re
import typing as tp


def _find_with_pattern(text: str, pattern: str, len_pattern):
    """
       Find some pattern (regular expression) in text
       :param text: text
       :param pattern: target string to find
       :param len_pattern: number of symbol that should be cut from  answer
       :return: finding expression without first 'len_pattern' symbol
       """
    match = re.search(pattern, text)
    return match[0][len_pattern:] if match else 'Not found'


class BotData:
    """
    Class for  storage and retrieval film info for telegrambot
    :param base_url: url for searching films
    :param api_token: Telegram bot api
    """

    def __init__(self, base_url: str, api_token: str) -> None:
        self._base_url = base_url
        self._api_token = api_token
        self._film_name = ''
        self._description = ''
        self._film_info = {}
        self._all_res = []

    def find_film_name(self, text: str) -> str:
        """
        Find request in phrase. request should be in quotes
        :param text:  some text to search for.
        :return: film name(request)
        """
        tokens = re.split(r'"', text)
        if len(tokens) > 1:
            self._film_name = tokens[1]
        else:
            self._film_name = ''
        return self._film_name

    def give_urls(self, only_best: bool = False) -> tp.Union[tp.List[str], str]:
        """
        Give film urls
        :param only_best: if True return first url, else return all film urls
        :return: film url or urls
        """
        if only_best:
            return self._base_url + self._all_res[0]
        return [self._base_url + res for res in self._all_res]

    def search_info(self, text: str) -> None:
        """
        Search some info in text
        :param text: some text to search for.
        """
        self._film_name = _find_with_pattern(text, r'"name":"[^"]+', 8)
        self._description = _find_with_pattern(text, r'"description" content="[^"]+', 23)
        self._film_info['год выпуска: '] = _find_with_pattern(text, r'"datePublished":"\d+', 17)
        self._film_info['Рейтинг на КиноПоиске: '] = _find_with_pattern(text, r'КиноПоиск \d,\d', 10)
        self._film_info['Страна: '] = _find_with_pattern(text, r'"countryOfOrigin":"\w+', 19)
        self._film_info['Возраст: '] = _find_with_pattern(text, r'"contentRating":"\d+', 17)
        self._film_info['жанр: '] = _find_with_pattern(text, r'"genre":"[^"]+', 9)

    def search_film(self, text: str) -> bool:
        """
        Search film reference in text
        :param text: some text to search for.
        :return: if found smth true else false
        """
        self._all_res = re.findall(r'/watch/\d+', text)
        if self._all_res:
            return True
        return False

    def give_film_info(self) -> str:
        '''
        Give some information about film
        :return: some film info
        '''
        info = []
        info.append(f'Название: {self._film_name}')
        for key, value in self._film_info.items():
            info.append(key + value)
        info.append(f'Ссылка для просмотра: {self.give_urls(only_best=True)}')
        return "\n".join(info)
