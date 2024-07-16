# api-ugpt (pgpt)

This API service provides pgpt functionality to Dash and SDK clients:

* conversational interface that the user interacts with to get AI responses
* events for actions such as "Start navigation", "Play music" and entities like POI or Music suggestions

More details on the design are in [the architecture doc](./docs/architecture.md).

## API

The API enables clients to send user conversation messages and to receive events with conversation responses, entities(POI/Music/Reservations), actions(Nav controls, Music controls), and other relevant information from the AI assistant. 

Generally, the client:
1. Connects to the websocket endpoint on start
1. Sends user conversation messages in POST request
1. Receives and acts on events that arrive over the websocket

Server-sent messages do not always have to correspond to a specific user conversation message, they can be sent at any time.

### Endpoints

There are currently 2 endpoints. 
1. Connection endpoint(Websocket API) for initiating/terminating a connection, getting session id of the connection, receiving events(conversation responses,actions,entites) for the session id
2. Conversation endpoint(REST API) for posting user prompts during a conversation. This endpoint returns success/failure status code immediately after request is sent. Response is sent as `conversation` event via websocket connection.

#### Connection

The websocket connection is used listen for events sent by the server and for getting the session ID, if previously unset. Events will arrive on this websocket as soon as they are generated in the backend.

The client and server messages that may be sent through the websocket channel are [documented here](./docs/ws-messages.md).


**Request Headers**
* `Authorization`: must be set with the user's access token
* `Session-Id`: may be set with an existing session-id if the client already has one. Session id allows to restore an existig user conversation when the client re-connects.

Example python code to initiate connection and receive session ID. See [available backends](./contributing.md#environments) for connection: 

```py
import websocket
import json

ws = websocket.WebSocket()
ws.connect("wss://pgpt-ppp-ws.xxx.com", header={"Authorization": access_token, "Session-Id": existing-session-id})
ws.send(json.dumps({"action":"get-session-id"})) # request session ID for the connection
print(ws.recv()) # returns session ID
```

This session id should be preserved on the client to be able to provide as header during subsequent connect requests. 
Not providing session id will generate a new conversation on the backend without any history. This could be used a debug option if the user/tester desires to "Reset Conversation".

More on websocket messages [here](./docs/ws-messages.md#start-session).

Client can re-request events sent previously upon reconnection if desired, see `resend-events` action [as shown here](./docs/ws-messages.md#resend-events).

#### Conversation

Send the user's query along with their coordinates and place name. The assistant's reply will be sent as conversation events over the websocket.
The current conversation endpoint version is `v1`.

`POST /v1/conversation/{session-id}`

**Request Headers**
- Authorization : xxx access token

**Request Body**
- context (object, required) : Current state about client and user. See [context.md](./docs/context.md) for details.
- prompt (string, required) : User query
- profile_id (string, optional) : Customers can control pgpt behaviour through profiles. Eg. `pgpt/autopilot`, `renault/user_manual`. This should be an input setting on the client app.
- capabilities (array of strings, optional) : List of capabilities that the client device can handle. Eg: `["spotifymusic", "entities_v0.control_vehicle"]`. See [events](./docs/action-events.md) for list of capabilities

Example:
```sh
curl -v --header "Authorization: ${xxxAccessToken}" https://pgpt-testing-api.tilestream.net/v1/conversation/{session-id} -d '{ "context": { "user_context": { "lat": "40", "lon": "-77", "place_name": "Baltimore" }, "app_context": { "locale":"en-US" } }, "prompt": "Play the most popular song of all time", "capabilities": [] }'
```

or, using [HTTPie](https://httpie.io/cli)

```sh
https -v pgpt-testing-api.tilestream.net/v1/conversation/{session-id} Authorization:$xxxAccessToken 'context[user_context][lat]=40' 'context[user_context][lon]=-77' 'context[user_context][place_name]=Baltimore' 'context[app_context][locale]=en-US' prompt='Play the most popular song of all time'
```

This will respond immediately with empty response upon successful validation of access token and request body.
AI conversation response and events are asynchronously emitted over the websocket connection established above.


### Supported Languages

pgpt currently supports queries in following languages as defined in [source](./agent/pgpt_agent/language.py).

* English
* Spanish
* French
* German
* Italian
* Japanese
* Korean
* Chinese
* Hebrew
* Dutch

The language iso code is specified as `locale` in `context` in Conversation request body.

Although, user input is allowed in other languages, pgpt response will be in English.

## Architecture

See [architecture.md](./docs/architecture.md) for the details

## Session ID sharing

See [Session ID sharing](./docs/session_id_sharing.md) for the details

## So you want to be a contributor?

See [contributing.md](./contributing.md)
