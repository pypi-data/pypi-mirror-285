from twilio.rest import Client
from includes import sms_id

account_sid = sms_id.acc_id
auth_token = sms_id.auth_token

def send_message(msg):
  try:
    client = Client(account_sid, auth_token)
    message = client.messages.create(
      from_=sms_id.twilio_no,
      body=f'Open Redirect Vulnerablity found!: \n\n{msg}',
      to= sms_id.whatsapp_no
    )
    print(f"\nMessage sent successfully: {message.sid}\n ")
  except Exception as e:
    print(f"Failed to send the message : {e}")

