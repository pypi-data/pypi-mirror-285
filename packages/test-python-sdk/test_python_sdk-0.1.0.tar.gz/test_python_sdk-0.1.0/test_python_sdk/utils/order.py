from test_python_sdk.api_client.types.models import OrderStatus


def get_open_order_statuses():
    return [
        OrderStatus.MatchedStatusZero.value, 
        OrderStatus.MatchedStatusInit.value, 
        OrderStatus.MatchedStatusWaitingForTrigger.value, 
        OrderStatus.MatchedStatusValidated.value, 
        OrderStatus.MatchedStatusPartialMatchConfirmed.value, 
        OrderStatus.MatchedStatusSentFailed.value, 
        OrderStatus.MatchedStatusBlocked.value, 
        OrderStatus.MatchedStatusPartialMatchPending.value, 
        OrderStatus.MatchedStatusFullMatchPending.value, 
        OrderStatus.MatchStatusCanceledPending.value
    ]