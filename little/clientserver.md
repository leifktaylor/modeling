DRAFT 1:

                                # Listen for client
                                loop forever:
                                    for each client:
                                        server.listen()


# Get user input and tick heartbeat timer
client.timer += 1
client.action = client_get_input()  # Get user input if any, ignore input if local cooldown

# Request changes update from server
if client.action or heartbeat == timer:
    client.request_update(username, password, current_room, action(yes/no))
    client.timer.reset()

                                # Update room with changes if any, server waits for action if valid
                                server.if changes:
                                    server.send_update(data, client)
                                server.else:
                                    server.send_update(None, client)
                                server.if not action:
                                    server.next_client()  # If there was no action, listen for next client

    client.if changes:
        client.room.update(changes)  # Update room data
        client.update_room_graphics(changes)  # Update room graphics

    ----- if there is an action by the client, continue reading -----

                                server.wait_for_update_from_client() # Wait for a while, and then move on if timeout


    client.if action:
        valid = client.do_action()   # Update local room data for action, and show graphical effects
                                     # Will return 0 if action went through, or errorcode if it didn't

        client.if action == valid:
            client.send_update(room_data, server)
        else:
            client.send_update(None, server)

                                if update not None:
                                    server.update_room()

        client.update_room_graphics()  # Update room graphics (objects on tiles, etc)


DRAFT 2:

                                # Listen for client
                                loop forever:
                                    for each client:
                                        server.listen()


# Get user input and tick heartbeat timer
client.timer += 1
client.action = client_get_input()  # Get user input if any, ignore input if local cooldown

# Request changes update from server
if client.action or heartbeat == timer:
    client.request_update(username, password, current_room, action(yes/no))
    client.timer.reset()

                                # Update room with changes if any, server waits for action if valid
                                server.if changes:
                                    server.send_update(data, client)
                                server.else:
                                    server.send_update(None, client)
                                server.if not action:
                                    server.next_client()  # If there was no action, listen for next client

    client.if changes:
        client.room.update(changes)  # Update room data
        client.update_room_graphics(changes)  # Update room graphics

    ----- if there is an action by the client, continue reading -----

                                server.wait_for_update_from_client() # Wait for a while, and then move on if timeout


    client.if action:
        valid = client.do_action()   # Update local room data for action, and show graphical effects
                                     # Will return 0 if action went through, or errorcode if it didn't

        client.if action == valid:
            client.send_update(room_data, server)
        else:
            client.send_update(None, server)

                                if update not None:
                                    server.update_room()

        client.update_room_graphics()  # Update room graphics (objects on tiles, etc) 