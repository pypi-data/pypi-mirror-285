import json
from typing import Union, List
import time
import pandas as pd
from azure.servicebus import ServiceBusClient, ServiceBusMessage, ServiceBusReceiver, ServiceBusSender, ServiceBusReceivedMessage
from brynq_sdk.brynq import BrynQ


class ServiceBus(BrynQ):

    def __init__(self, label: Union[str, List], debug: bool = False):
        """
        For the full documentation, see: https://pypi.org/project/azure-servicebus/
        """
        super().__init__()
        self.debug = debug
        self.client = self._get_credentials(label)

    def _get_credentials(self, label):
        """
        Get the credentials from BrynQ and get the username and private key from there
        """
        credentials = self.get_system_credential(system='azure-service-bus', label=label)
        if self.debug:
            print(credentials)
        endpoint = credentials['endpoint']
        shared_access_key_name = credentials['shared_access_key_name']
        shared_access_key = credentials['shared_access_key']
        entity_path = credentials['entity_path']
        connection_string = f"Endpoint={endpoint};SharedAccessKeyName={shared_access_key_name};SharedAccessKey={shared_access_key};EntityPath={entity_path}"
        client = ServiceBusClient.from_connection_string(conn_str=connection_string)
        return client

    def receive_data_from_queue(self, subscription_name: str, topic_name: str) -> pd.DataFrame:
        """
        Retrieves messages from a specified Azure Service Bus subscription and topic,
        processes them, and returns the data as a pandas DataFrame.

        This method connects to the Azure Service Bus using the client initialized in the constructor,
        receives messages in batches from the specified subscription and topic, and processes each message.
        The processing involves decoding the message body, parsing it as JSON, and then appending the message
        details along with the JSON data to a pandas DataFrame. The DataFrame is structured with predefined columns.
        If no more messages are received within the specified wait time, the method exits the loop and returns the DataFrame.

        Parameters:
        - subscription_name (str): The name of the subscription from which messages are to be received.
        - topic_name (str): The name of the topic from which messages are to be received.

        Returns:
        - pd.DataFrame: A pandas DataFrame containing the message details and the data extracted from each message.
                        The columns of the DataFrame are ['message_id', 'session_id', 'body', 'processing_status'],
                        with 'processing_status' set to 'pending' for all rows initially.
        """
        df_columns = ['message_id', 'session_id', 'body', 'processing_status']
        df = pd.DataFrame(columns=df_columns)
        with self.client:
            receiver = self.client.get_subscription_receiver(
                subscription_name=subscription_name,
                topic_name=topic_name
            )
            with receiver:
                while True:
                    batch = receiver.receive_messages(max_message_count=100, max_wait_time=5)
                    for msg in batch:
                        if isinstance(msg, ServiceBusMessage):
                            message_body = b''.join(chunk for chunk in msg.body)  # Join all chunks to form complete byte content
                            message = message_body.decode('utf-8')
                            json_message = json.loads(message)

                        row_data = {
                            'message_id': msg.message_id,
                            'session_id': msg.session_id,
                            'processing_status': 'pending'
                        }
                        row_data.update(json_message)
                        df = pd.concat([df, row_data], ignore_index=True)
                    if not batch:
                        break  # Exit if no more messages are received within the wait time
        return df

    def send_data_to_queue(self, topic_name: str, message: dict, session_id: str = int(time.time()), direction: str = None, entity: str = None):
        """
        Sends a message to a specified Azure Service Bus topic.

        This method serializes a given message into JSON format and sends it to the specified topic on the Azure Service Bus.
        It sets additional application properties for the message, including direction, entity, action, and version, which can
        be used for routing or processing logic in receivers. The message is sent within a session, allowing for session-based
        message sequencing and grouping.

        Parameters:
        - topic_name (str): The name of the topic to which the message will be sent.
        - message (dict): The message payload to be sent, which will be serialized to JSON.
        - session_id (str): The session ID to associate with the message, enabling session-based messaging. If not provided, a timestamp is used.
        - direction (str): optional: The direction property of the message, typically used to indicate the message flow.
        - entity (str): optional: The entity property of the message, usually indicating the target entity type.

        Note:
        This method assumes that the ServiceBusClient has been initialized and is connected to the Azure Service Bus.
        """
        application_properties = {
            "Action": "Update",
            "Version": 1
        }
        if direction:
            application_properties["Direction"] = f"{direction}"
        if entity:
            application_properties["Entity"] = f"{entity}"

        with self.client:
            sender = self.client.get_topic_sender(topic_name=topic_name)
            with sender:
                message = ServiceBusMessage(
                    body=json.dumps(message).encode('utf-8'),
                    application_properties=application_properties,
                    session_id=session_id
                )
                sender.send_messages(message)

    def remove_data_from_queue(self, subscription_name: str, topic_name: str, message_id: str):
        """
       Removes a specific message from a queue based on its message ID.

       This method connects to the Azure Service Bus using the client initialized in the constructor,
       receives a batch of messages from the specified subscription and topic, and iterates through them.
       If a message with the specified message ID is found, it is completed (acknowledged) which effectively
       removes it from the queue. This method is useful for processing and removing messages selectively
       based on their content or ID.

       Parameters:
       - subscription_name (str): The name of the subscription from which messages are to be received and removed.
       - topic_name (str): The name of the topic from which messages are to be received and removed.
       - message_id (str): The ID of the message to be removed.

       Note:
       This method assumes that the message ID is unique within the batch of retrieved messages.
       If the specified message ID is not found within the batch, no action is taken.
       """
        with self.client:
            receiver = self.client.get_subscription_receiver(
                subscription_name=subscription_name,
                topic_name=topic_name
            )
            with receiver:
                received_messages = receiver.receive_messages(max_message_count=10, max_wait_time=5)
                for received_message in received_messages:
                    if received_message.message_id == message_id:
                        receiver.complete_message(received_message)
