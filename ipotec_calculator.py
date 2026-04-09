import matplotlib.pyplot as plt

def mortgage_calculator(real_estate_value, down_payment, term_in_years, bid, payment_type):

    # payment_type: 1 - аннуитетный, 2 - дифференцированный

    while True:
        try:
            # Вычисление значений
            mortgage_loan_amount = real_estate_value - down_payment  # Сумма иппотечного кредита

            monthly_interest_rate = bid / 12 / 100  # Месячная процентная ставка

            total_loan_term = term_in_years * 12    # Срок кредита в месяцах

            if payment_type == 1:
                # Аннуитетный платёж
                total_rate = (1 + monthly_interest_rate) ** total_loan_term
                annuity_payment = mortgage_loan_amount * monthly_interest_rate * total_rate / (total_rate - 1)
                overpayment = annuity_payment * total_loan_term - mortgage_loan_amount
                first_payment = annuity_payment
                last_payment = annuity_payment
            elif payment_type == 2:
                # Дифференцированный платёж
                monthly_principal = mortgage_loan_amount / total_loan_term
                # Первый платёж
                first_payment = monthly_principal + mortgage_loan_amount * monthly_interest_rate
                # Последний платёж
                last_payment = monthly_principal + monthly_principal * monthly_interest_rate
                # Переплата = сумма процентов (арифметическая прогрессия)
                overpayment = monthly_interest_rate * mortgage_loan_amount * (total_loan_term + 1) / 2
                annuity_payment = None  # для аннуитета не используется
            else:
                raise ValueError("Неверный тип платежа. Выберите 1 или 2.")

            # Налоговый вычет за покупку
            limit_purchase = 2_000_000
            tax_refund_purchase = min(real_estate_value, limit_purchase) * 0.13

            # Вычет по процентам
            limit_interests = 3_000_000
            tax_refund_interests = min(overpayment, limit_interests) * 0.13
            total_refund = tax_refund_purchase + tax_refund_interests

            K = 3.33540331196581
            print(f"Сумма кредита: {mortgage_loan_amount:.0f} ₽")
            if payment_type == 1:
                print(f"Ежемесячный платёж (аннуитет): {annuity_payment:.0f} ₽")
                recommended_income = annuity_payment * K
            else:
                print(f"Первый платёж (дифференцированный): {first_payment:.0f} ₽")
                print(f"Последний платёж (дифференцированный): {last_payment:.0f} ₽")
                recommended_income = first_payment * K
            print(f"Переплата по кредиту: {overpayment:.0f} ₽")
            print(f"Общая выплата: {(mortgage_loan_amount + overpayment):.0f} ₽")
            print(f"Рекомендуемый доход: {recommended_income:.0f} ₽")
            print("НАЛОГОВЫЙ ВЫЧЕТ (НДФЛ):")
            print(f"За покупку жилья: {tax_refund_purchase:.0f} ₽")
            print(f"За уплаченные проценты: {tax_refund_interests:.0f} ₽")
            print(f"Можно вернуть: {total_refund:.0f} ₽")
            print("\nНажмите клавишу Enter, чтобы продолжить")

            return mortgage_loan_amount, total_loan_term, annuity_payment if payment_type == 1 else first_payment, monthly_interest_rate, payment_type

        except ValueError as e:
            print(f"Ошибка: {e}")
        except ZeroDivisionError:
            print("Ошибка: срок кредита или ставка не могут быть нулевыми.")
        except NameError:
            pass


def plot_debt_schedule(months, balances, payment_type):
    plt.plot(months, balances, marker='o', markersize=2, linewidth=1.5, color='b', label='Остаток долга')
    plt.title(f'График погашения кредита ({"аннуитет" if payment_type == 1 else "дифференцированный"})')
    plt.xlabel('Месяцы')
    plt.ylabel('Сумма (₽)')
    plt.grid(True)
    plt.legend()
    plt.show()


def calculate_balance_schedule(loan_amount, monthly_rate, total_months, payment_type):
    months = list(range(int(total_months) + 1))
    balances = []

    if payment_type == 2:
        # Дифференцированный способ платежа
        for k in months:
            balance = loan_amount * (1 - k / total_months)
            balances.append(balance)
    else:
        # Аннуитетный способ платежа
        if monthly_rate == 0:
            for k in months:
                balance = loan_amount * (1 - k / total_months)
                balances.append(balance)
        else:
            factor = (1 + monthly_rate) ** total_months
            for k in months:
                balance = loan_amount * (factor - (1 + monthly_rate) ** k) / (factor - 1)
                balances.append(balance)
    return months, balances


if __name__ == "__main__":
    real_estate_value = float(input("Введите стоимость недвижимости: "))
    down_payment = float(input("Введите первоначальный взнос: "))
    term_in_years = float(input("Введите срок кредита в годах: "))
    bid = float(input("Введите годовую процентную ставку: "))
    while True:
        try:
            payment_type = int(input("Выберите тип платежа (1 - аннуитетный, 2 - дифференцированный): "))
            if payment_type in (1, 2):
                break
            else:
                print("Введите 1 или 2.")
        except ValueError:
            print("Введите целое число 1 или 2.")

    # Получение данных из калькулятора
    mortgage_loan_amount, total_loan_term, _, monthly_interest_rate, payment_type = mortgage_calculator(
        real_estate_value, down_payment, term_in_years, bid, payment_type
    )

    # Построение графика остатка долга
    months, balances = calculate_balance_schedule(mortgage_loan_amount, monthly_interest_rate, total_loan_term, payment_type)
    plot_debt_schedule(months, balances, payment_type)