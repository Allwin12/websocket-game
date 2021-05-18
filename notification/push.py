from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def create_push_notification(consumer, m_type, message):
    try:
        group_name = consumer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, {
            "type": m_type,
            "message": message,
        })

    except Exception as e:
        print(f"Error Creating Push Notification. {e}")
