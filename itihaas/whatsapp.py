"""WhatsApp booking confirmations via ``pywhatkit``.

``pywhatkit`` automates WhatsApp Web in a local desktop browser, so this only
works on a machine with a logged-in WhatsApp Web session. It is disabled
unless ``WHATSAPP_ENABLED=1``. For production, replace it with the official
WhatsApp Business Cloud API.
"""
import re
import time
from datetime import datetime, timedelta


def format_phone_number(phone_number):
    """
    Format phone number to include country code (e.g., +91XXXXXXXXXX)
    """
    # Remove any non-digit characters
    phone_number = re.sub(r'\D', '', phone_number)

    # Add country code if not present
    if not phone_number.startswith('91'):
        phone_number = '91' + phone_number

    # Add plus sign for pywhatkit
    return '+' + phone_number

def send_booking_confirmation(phone_number, booking_details):
    """
    Send booking confirmation via WhatsApp using pywhatkit
    """
    try:
        # Import pywhatkit only when needed
        import pywhatkit

        # Format phone number
        formatted_number = format_phone_number(phone_number)

        # Format the message
        message = f"""
🎫 *Booking Confirmation*

Dear {booking_details['name']},

Your booking has been confirmed! Here are the details:

*Monument:* {booking_details['monument_name']}
*Visit Date:* {booking_details['visit_date'].strftime('%d %B %Y')}
*Number of Visitors:* {booking_details['visitors']}
*Total Amount:* ₹{booking_details['total_amount']}
*Booking ID:* {booking_details['id']}

Please present this booking confirmation at the entrance.

Thank you for choosing Itihaas!
        """

        # Get current time and add 30 seconds to ensure proper scheduling
        now = datetime.now()
        send_time = now + timedelta(seconds=30)

        # Ensure we have enough time for WhatsApp Web to load
        if (send_time.minute == now.minute and send_time.second < 30):
            send_time = now + timedelta(minutes=1)

        # Send WhatsApp message
        pywhatkit.sendwhatmsg(
            phone_no=formatted_number,
            message=message,
            time_hour=send_time.hour,
            time_min=send_time.minute,
            wait_time=10,  # Reduced wait time to 10 seconds
            tab_close=True,
            close_time=2
        )

        # Sleep for a moment to ensure the message is sent
        time.sleep(1)

        return True, "Message scheduled successfully"
    except ImportError:
        return False, "pywhatkit is not installed (pip install pywhatkit)"
    except Exception as exc:  # pywhatkit raises a variety of errors
        return False, str(exc)
