from flask import Flask, request
import logging
import json
from geo import get_country, get_distance, get_coordinates

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')


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
    logging.info('Request: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Я могу сказать в какой стране город или сказать расстояние между городами!'
        return
    cities = get_cities(req)
    if len(cities) == 0:
        country = get_country(cities[0])
        if country is None:
            res['response']['text'] = 'Не могу определить страну для этого города'
        else:
            res['response']['text'] = f'Этот город в стране - {country}'
    elif len(cities) == 2:
        coord1 = get_coordinates(cities[0])
        coord2 = get_coordinates(cities[1])
        if coord1 is None or coord2 is None:
            res['response']['text'] = 'Не могу определить координаты городов'
    else:
        res['response']['text'] = 'Слишком много городов!'


def get_cities(req):
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value'].keys():
                cities.append(entity['value']['city'])

    return cities


if __name__ == '__main__':
    app.run()
