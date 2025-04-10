from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}
animals = ['слон', "кролик", "кот"]
current_animal_idx = 0


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

    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    return jsonify(response)


def handle_dialog(req, res):
    global current_animal_idx
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        # Заполняем текст ответа
        res['response']['text'] = f'Привет! Купи {animals[0]}а!'
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id)
        return
    words = req['request']['nlu']['tokens']

    if [word for word in words if word in ['ладно',
                                           'куплю',
                                           'покупаю',
                                           'хорошо']]:
        if current_animal_idx + 1 > len(animals):
            res['response']['text'] = 'Все можно найти на Яндекс.Маркете!'
            res['response']['end_session'] = True
            return
        current_animal_idx += 1
        if len(animals) == current_animal_idx:
            res['response']['text'] = 'Все можно найти на Яндекс.Маркете! Спасибо за покупки'
            res['response']['end_session'] = True
            return
        res['response']['text'] = f'{animals[current_animal_idx - 1]}а можно найти на Яндекс.Маркете! ' \
                                  f'А теперь купи {animals[current_animal_idx]}а'
        res['response']['buttons'] = get_suggests(user_id)
        return

    res['response']['text'] = f'Все говорят "%s", а ты купи {animals[current_animal_idx]}а!' % (
        req['request']['original_utterance']
    )
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={animals[current_animal_idx]}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
