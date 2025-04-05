# This is the main function that will be used to handle the websocket connection
async def websocket_application(scope, receive, send):
    # While the connection is open
    while True:
        # Receive the event
        event = await receive()

        # If the event is a connection
        if event["type"] == "websocket.connect":
            # Accept the connection
            await send({"type": "websocket.accept"})

        # If the event is a disconnect
        if event["type"] == "websocket.disconnect":
            # Break the loop
            break

        # If the event is a receive
        if event["type"] == "websocket.receive":
            # If the message is ping
            if event["text"] == "ping":
                # Send the message pong
                await send({"type": "websocket.send", "text": "pong!"})
