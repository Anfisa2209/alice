import logging

from flask import Flask, request, jsonify
from googletrans import Translator

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

LANGUAGES = {'en': "английский",
             'zh-cn': "китайский (упрощенный)",
             'ko': "корейский",
             "de": "немецкий",
             "es": 'испанский'}
sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return jsonify(response)


def handle_dialog(res, req):
    if req['session']['new']:
        res['response']['text'] = 'Привет! Я могу перевести что-нибудь! Для этого напиши: переведи слово <слово>'
        res['response']['buttons'] = [
            {
                'title': 'Покажи как',
                'hide': True
            },
            {
                'title': 'Помощь',
                'hide': True
            }
        ]
        return
    if 'помощь' in req['request']['nlu']['tokens']:
        res['response']['text'] = 'Введи: переведи слово <слово> - и я переведу'
        res['response']['buttons'] = [
            {
                'title': 'Переведи слово Привет',
                'hide': True
            },
            {
                'title': 'Помощь',
                'hide': True
            }
        ]
        return
    elif 'покажи' in req['request']['nlu']['tokens']:
        result = translate(word='Вот так я умею переводить!', dest='multi')
        res['response']['text'] = result + "\nТак что переведем?"
        res['response']['buttons'] = [
            {
                'title': 'Переведи слово Привет',
                'hide': True
            },
            {
                'title': 'Помощь',
                'hide': True
            }
        ]
        return
    elif "переведи слово" in req['request']["original_utterance"].lower():
        word = req['request']["original_utterance"].split()[-1]
        res['response']['text'] = "Перевожу... (это займет пару секунд)"
        result = translate(word=word, dest='multi')
        res['response']['text'] = result
        return
    else:
        res['response']['text'] = "Не понимаю... Повтори-ка еще"
        return


def translate(word, dest):
    translator = Translator()
    result = f'Вот перевод "{word}" на несколько языков:\n'
    if dest == 'multi':
        for lang, description in LANGUAGES.items():
            translation = translator.translate(word, dest=lang)
            result += f"На {description}: " + translation.text + '\n'

    return result


if __name__ == '__main__':
    app.run()
