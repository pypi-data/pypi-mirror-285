from enum import Enum


class EventTriggerTypeEnum(str, Enum):
    MANUAL_CANCEL_SERVICE_TICKET = "manual_cancel_service_ticket"
    BOOKING_REMINDING_SERVICE_TICKET = "booking_reminding_service_ticket"
    MANUAL_TRACING_START_SERVICE_TICKET = "manual_tracking_start_service_ticket"
    MANUAL_TRACING_STOP_SERVICE_TICKET = "manual_tracking_stop_service_ticket"
    MANUAL_CREATE_SERVICE_TICKET = "manual_create_service_ticket"
    MANUAL_IMPORT_RESERVATION_SMWS = "manual_import_reservation_smws"
    IMPORT_RESERVATION_CONFLICT_AUTO_CANCEL = "import_reservation_conflict_auto_cancel"
    LPNR_IN = "lpnr_in"
    LPNR_OUT = "lpnr_out"
