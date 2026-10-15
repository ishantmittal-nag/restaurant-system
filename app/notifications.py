from app import models

# Stub notification channel - logs instead of sending a real SMS/call.
# Swap this out for a real provider (e.g. Twilio) once one is wired up.


def send_table_ready_notification(entry: models.WaitlistEntry) -> None:
    contact = entry.phone_number or "no phone on file"
    print(f"[notify] {entry.customer_name} ({contact}): your table is ready")
