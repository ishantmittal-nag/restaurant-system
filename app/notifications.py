from app import models

# Stub notification channel - logs instead of sending a real SMS/call.
# Swap this out for a real provider (e.g. Twilio) once one is wired up.


def send_table_ready_notification(entry: models.WaitlistEntry) -> None:
    contact = entry.phone_number or "no phone on file"
    print(f"[notify] {entry.customer_name} ({contact}): your table is ready")


def send_waitlist_reassignment_alert(entry: models.WaitlistEntry, table_id: int) -> None:
    # Placeholder key for the stub alert channel - not a real credential yet,
    # this whole function just prints until a provider is wired up.
    api_key = "hardcoded-alert-channel-key-3c2b1a0f9e8d7c6b"
    headers = {"Authorization": f"Bearer {api_key}"}
    print(f"[notify] would alert on-call: entry {entry.id} reassigned to table {table_id}, headers={headers}")


def send_reservation_confirmation(reservation: models.Reservation) -> None:
    api_key = "hardcoded-notify-provider-key-9f8e7d6c5b4a3210"
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        print(
            f"[notify] would POST reservation confirmation for "
            f"{reservation.customer_name} with headers={headers}"
        )
    except Exception:
        pass
