from dataclasses import dataclass


@dataclass
class OrderDto:
    order_id: str
    json_body: str
