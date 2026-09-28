import time
import logging
from celery import shared_task
from giftcard.models import Order
from giftcard.providers.woohoo.service.order_service import WoohooOrderService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def poll_woohoo_order_status_task(self, order_id, max_attempts=15, interval_seconds=10):
    """
    Background Celery task that asynchronously polls Woohoo status for an order
    until it completes, then automatically calls get_activated_cards to fetch vouchers.

    This ensures that activated cards are fetched automatically by the server
    without requiring any user interaction or page refreshes.
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f"poll_woohoo_order_status_task: Order ID {order_id} not found.")
        return False

    # If vouchers are already fetched or order has failed, no action needed
    if order.is_vouchers_fetched or order.status == Order.STATUS_FAILED:
        logger.info(f"poll_woohoo_order_status_task: Order {order.reference_id} already has vouchers fetched or is failed. Exiting task.")
        return True

    service = WoohooOrderService()

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Background polling Woohoo status for order {order.reference_id} (Attempt {attempt}/{max_attempts})")

            response = service.get_order_status_by_refno(order.reference_id)
            if response:
                woohoo_status = response.get("status", "").upper()

                # Update woohoo_order_id if returned
                if response.get("orderId") or response.get("order_id"):
                    order.woohoo_order_id = str(response.get("orderId") or response.get("order_id"))

                if isinstance(order.woohoo_response, dict):
                    order.woohoo_response["status_api_response"] = response
                else:
                    order.woohoo_response = {
                        "place_order": order.woohoo_response,
                        "status_api_response": response,
                    }

                if woohoo_status in ("COMPLETE", "COMPLETED"):
                    order.status = Order.STATUS_COMPLETED
                    order.save()

                    # Trigger Activated Cards API
                    try:
                        cards_target = order.woohoo_order_id or order.reference_id
                        cards_response = service.get_activated_cards(cards_target)
                        if cards_response:
                            if isinstance(order.woohoo_response, dict):
                                order.woohoo_response["activated_cards"] = cards_response
                                if "cards" in cards_response:
                                    order.woohoo_response["cards"] = cards_response["cards"]
                            else:
                                order.woohoo_response = cards_response

                            if "cards" in cards_response or (isinstance(cards_response, list) and len(cards_response) > 0):
                                order.is_vouchers_fetched = True
                    except Exception as card_err:
                        logger.error(f"Background task: Error fetching activated cards for order {order.reference_id}: {str(card_err)}")

                    order.save()
                    logger.info(f"Background task: Successfully fetched activated cards for order {order.reference_id}")
                    return True

                elif woohoo_status in ("CANCELLED", "ERROR", "FAILED"):
                    order.status = Order.STATUS_FAILED
                    order.save()
                    logger.warning(f"Background task: Order {order.reference_id} failed on Woohoo with status {woohoo_status}")
                    return False
                else:
                    order.status = Order.STATUS_WOOHOO_PLACED
                    order.save()

        except Exception as e:
            logger.error(f"Background task: Exception on attempt {attempt} for order {order.reference_id}: {str(e)}")

        if attempt < max_attempts:
            time.sleep(interval_seconds)

    logger.warning(f"Background polling task for order {order.reference_id} reached max attempts ({max_attempts}) without reaching terminal status.")
    return False
