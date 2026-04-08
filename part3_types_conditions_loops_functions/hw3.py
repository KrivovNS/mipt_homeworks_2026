#!/usr/bin/env python

from typing import Any

ARGS_COUNT_TWO = 2
ARGS_COUNT_THREE = 3
ARGS_COUNT_FOUR = 4
FEBRUARY_DAYS_COUNT_IN_LEAP_YEAR = 29
FEBRUARY_MONTH_NUM = 2
MONTH_COUNT = 12

MONTH_DAYS = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31}

OPERATION_TYPE_KEY = "operation_type"
CATEGORY_KEY = "category"
DATE_KEY = "date"
AMOUNT_KEY = "amount"

INCOME_OPERATION = "income"
COST_OPERATION = "cost"
STATS_OPERATION = "stats"

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"
INCORRECT_AMOUNT_MSG = "Incorrect amount!"
INCORRECT_ARGS_COUNT_MSG = "Incorrect count of arguments!"

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

ParsedDate = tuple[int, int, int]

financial_transactions_storage: list[dict[str, Any]] = []


def add_error_stub() -> None:
    financial_transactions_storage.append({})


def is_leap_year(year: int) -> bool:
    if year % 4 == 0 and year % 100 != 0:
        return True
    return year % 400 == 0


def extract_date(raw: str) -> ParsedDate | None:
    parts = raw.split("-")

    has_valid_parts_count = len(parts) == ARGS_COUNT_THREE
    all_parts_are_digits = all(part.isdigit() for part in parts)

    if not (has_valid_parts_count and all_parts_are_digits):
        return None

    day, month, year = (int(part) for part in parts)
    if month < 1 or month > MONTH_COUNT or year < 0:
        return None

    if month == FEBRUARY_MONTH_NUM and is_leap_year(year):
        return (day, month, year) if 1 <= day <= FEBRUARY_DAYS_COUNT_IN_LEAP_YEAR else None
    return (day, month, year) if 1 <= day <= MONTH_DAYS[month] else None


def valid_date(raw: str) -> bool:
    return extract_date(raw) is not None


def parse_amount(raw_amount: str) -> float | None:
    amount = raw_amount.replace(",", ".")
    if not amount:
        return None
    body = amount[1:] if amount[0] in "+-" else amount
    if not body or body == "." or body.count(".") > 1:
        return None
    if not all(ch.isdigit() or ch == "." for ch in body):
        return None
    return float(amount)


def parse_category(category_name: str) -> tuple[str, str] | None:
    parts = category_name.split("::")
    if len(parts) != ARGS_COUNT_TWO:
        return None
    return parts[0], parts[1]


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        add_error_stub()
        return NONPOSITIVE_VALUE_MSG

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        add_error_stub()
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {OPERATION_TYPE_KEY: INCOME_OPERATION, AMOUNT_KEY: amount, DATE_KEY: parsed_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if amount <= 0:
        add_error_stub()
        return NONPOSITIVE_VALUE_MSG

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        add_error_stub()
        return INCORRECT_DATE_MSG

    parsed_category = parse_category(category_name)
    if parsed_category is None:
        add_error_stub()
        return NOT_EXISTS_CATEGORY
    common_category, target_category = parsed_category
    if common_category not in EXPENSE_CATEGORIES or target_category not in EXPENSE_CATEGORIES[common_category]:
        add_error_stub()
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append(
        {OPERATION_TYPE_KEY: COST_OPERATION, CATEGORY_KEY: category_name, AMOUNT_KEY: amount, DATE_KEY: parsed_date}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    rows: list[str] = [f"{common_category}::{target_category}"
                       for common_category, target_categories in EXPENSE_CATEGORIES.items()
                       for target_category in target_categories]
    return "\n".join(rows)


def is_date_before(date: str, target_date: str) -> bool:
    parsed_date = extract_date(date)
    parsed_target_date = extract_date(target_date)
    if parsed_date is None or parsed_target_date is None:
        return False
    return is_parsed_date_before(parsed_date, parsed_target_date)


def is_parsed_date_before(parsed_date: ParsedDate, parsed_target_date: ParsedDate) -> bool:
    day1, month1, year1 = parsed_date
    day2, month2, year2 = parsed_target_date
    return (year1, month1, day1) <= (year2, month2, day2)


def parse_record_date(record: dict[str, Any]) -> ParsedDate | None:
    raw_date = record.get(DATE_KEY)
    if isinstance(raw_date, tuple):
        return raw_date
    if isinstance(raw_date, str):
        return extract_date(raw_date)
    return None


def is_record_in_report_period(record: dict[str, Any], parsed_report_date: ParsedDate) -> bool:
    parsed_current_date = parse_record_date(record)
    if parsed_current_date is None:
        return False
    if not is_parsed_date_before(parsed_current_date, parsed_report_date):
        return False
    return is_in_report_month(parsed_current_date, parsed_report_date)


def is_in_report_month(parsed_current_date: ParsedDate, parsed_report_date: ParsedDate) -> bool:
    _, month, year = parsed_current_date
    _, report_month, report_year = parsed_report_date
    return month == report_month and year == report_year


def is_cost_record(record: dict[str, Any]) -> bool:
    operation_type = record.get(OPERATION_TYPE_KEY)
    return operation_type == COST_OPERATION or (
            operation_type is None and CATEGORY_KEY in record
    )


def add_cost_record(record: dict[str, Any], costs_by_categories: dict[str, float]) -> float:
    amount = float(record.get(AMOUNT_KEY, 0))
    category = record.get(CATEGORY_KEY)

    if not isinstance(category, str):
        return 0

    costs_by_categories[category] = costs_by_categories.get(category, 0) + amount
    return amount


def add_income_record(record: dict[str, Any]) -> float:
    return float(record.get(AMOUNT_KEY, 0))


def collect_stats(parsed_report_date: ParsedDate) -> tuple[float, float, dict[str, float]]:
    costs_amount: float = 0
    incomes_amount: float = 0
    costs_by_categories: dict[str, float] = {}

    for record in financial_transactions_storage:
        if not record or not is_record_in_report_period(record, parsed_report_date):
            continue

        if is_cost_record(record):
            costs_amount += add_cost_record(record, costs_by_categories)
            continue

        incomes_amount += add_income_record(record)

    return costs_amount, incomes_amount, costs_by_categories


def round_amounts_in_categories(costs_by_categories: dict[str, float]) -> dict[str, float]:
    return {
        category: round(amount, 2)
        for category, amount in costs_by_categories.items()
    }


def count_stats_for_date(report_date: str) -> tuple[float, float, dict[str, float]]:
    parsed_report_date = extract_date(report_date)
    if parsed_report_date is None:
        return 0, 0, {}

    costs_amount, incomes_amount, costs_by_categories = collect_stats(parsed_report_date)

    return (
        round(costs_amount, 2),
        round(incomes_amount, 2),
        round_amounts_in_categories(costs_by_categories),
    )


def form_stats_answer(report_date: str, stats: tuple[float, float, dict[str, float]]) -> str:
    costs_amount, incomes_amount, costs_by_categories = stats
    total_capital = round(costs_amount - incomes_amount, 2)
    amount_word = "loss" if total_capital < 0 else "profit"

    category_rows = []
    for index, (category, amount) in enumerate(costs_by_categories.items()):
        category_rows.append(f"{index}. {category}: {amount}")
    category_details_in_string = "\n".join(category_rows)

    return (
        f"Your statistics as of {report_date}:\n"
        f"Total capital: {total_capital} rubles\n"
        f"This month, the {amount_word} amounted to {total_capital} rubles.\n"
        f"Income: {costs_amount} rubles\n"
        f"Expenses: {incomes_amount} rubles\n\n"
        f"Details (category: amount):\n"
        f"{category_details_in_string}\n")


def stats_handler(report_date: str) -> str:
    if not valid_date(report_date):
        return INCORRECT_DATE_MSG
    return form_stats_answer(report_date, count_stats_for_date(report_date))


def process_command(*args: str) -> None:
    if not args:
        print(UNKNOWN_COMMAND_MSG)
        return

    if args[0] == INCOME_OPERATION:
        process_income_command(args)
        return

    if args[0] == COST_OPERATION:
        process_cost_command(args)
        return

    if args[0] == STATS_OPERATION:
        process_stats_command(args)
        return

    print(UNKNOWN_COMMAND_MSG)


def process_income_command(args: tuple[str, ...]) -> None:
    if len(args) != ARGS_COUNT_THREE:
        print(INCORRECT_ARGS_COUNT_MSG)
        return
    amount = parse_amount(args[1])
    if amount is None:
        print(INCORRECT_AMOUNT_MSG)
    else:
        print(income_handler(amount, args[2]))


def process_cost_command(args: tuple[str, ...]) -> None:
    if len(args) == ARGS_COUNT_TWO and args[1] == "categories":
        print(cost_categories_handler())
        return
    if len(args) == ARGS_COUNT_FOUR:
        amount = parse_amount(args[2])
        if amount is None:
            print(INCORRECT_AMOUNT_MSG)
        else:
            print(cost_handler(args[1], amount, args[3]))
        return
    print(INCORRECT_ARGS_COUNT_MSG)


def process_stats_command(args: tuple[str, ...]) -> None:
    if len(args) == ARGS_COUNT_TWO:
        print(stats_handler(args[1]))
        return
    print(INCORRECT_ARGS_COUNT_MSG)


def main() -> None:
    request = input()
    while request:
        process_command(*request.split())
        request = input()


if __name__ == "__main__":
    main()
