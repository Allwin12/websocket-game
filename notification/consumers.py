# chat/consumers.py
import asyncio
import json
import random

from channels.generic.websocket import AsyncWebsocketConsumer


class GroupConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = 'chat_%s' % self.room_name
        self.is_connected = True
        self.joined = 0
        self.player_data = []
        self.game_over = False
        self.winner = None

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()
        print('connected')
        #
        # while self.is_connected:
        #     await asyncio.sleep(2)
        #     await self.send(text_data=self.room_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        event_type = data['type']
        if event_type == "initial":
            players = data.get('players')
            self.players = players
            uuid = data.get('uuid')
            colours = ["BLUE", "GREEN", "YELLOW", "ORANGE", "RED", "BLACK", "PINK", "CYAN"]
            player_colours = colours[0:players] * 4
            random.shuffle(player_colours)

            for i in range(0, players * 4, 4):
                self.player_data.append({'cards': player_colours[i:i + 4], 'turn': False, 'uuid': None})
            self.player_data[0].update({
                'uuid': uuid,
                'turn': True
            })
            self.joined = 1
            await self.send(text_data=json.dumps(self.player_data))
        elif event_type == "join":
            uuid = data.get('uuid')
            for player in self.player_data:
                if player.get('uuid') is None:
                    player['uuid'] = uuid
                    self.joined += 1
                    break
            await self.send(text_data=json.dumps(self.player_data))
        elif event_type == "status":
            await self.send(text_data=json.dumps({"all_joined": self.joined == self.players}))
        elif event_type == "move":
            moved_from = data.get('from')
            to = data.get('to')
            colour = data.get('colour')

            for player in self.player_data:
                if player.get('uuid') == moved_from:
                    cards = player.get('cards')
                    cards.remove(colour)
                    player['cards'] = cards
                    break

            for player in self.player_data:
                if player.get('uuid') == to:
                    cards = player.get('cards')
                    cards.append(colour)
                    player['cards'] = cards
                    break
            self.check_winner()
            result = {
                'game_status': self.player_data,
                'winning_status': {
                    'game_over': self.game_over,
                    'winner': self.winner
                }
            }
            await self.send(text_data=json.dumps(result))

    async def websocket_disconnect(self, event):
        self.is_connected = False
        print("disconnected", event)

    def check_winner(self):
        print(self.player_data)
        for player in self.player_data:
            cards = player.get('cards')
            if len(set(cards)) == 1:
                self.game_over = True
                self.winner = player.get('uuid')

