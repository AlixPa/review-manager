from src.models.database import House


def main() -> None:
    h = House(user_id=15)
    print(h)
    print(h.model_dump())

    h2 = House(user_id=145, has_toire_betsu=True)
    print(h2)
    h3 = House(user_id=145, has_toire_betsu=1)
    print(h3)
    h4 = House(user_id=145, has_toire_betsu=0)
    print(h4)
