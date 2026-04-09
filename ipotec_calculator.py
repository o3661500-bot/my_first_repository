import matplotlib.pyplot as plt

def mortgage_calculator(real_estate_value, down_payment, term_in_years, bid):
    while True:
        try:
            # Вычисление значений
            mortgage_loan_amount = real_estate_value - down_payment  # Сумма иппотечного кредита

            monthly_interest_rate = bid / 12 / 100  # Месячная процентная ставка

            total_loan_term = term_in_years * 12    # Срок кредита в месяцах

            total_rate = (1 + monthly_interest_rate) ** total_loan_term # Общая ставка

            annuity_payment = mortgage_loan_amount * monthly_interest_rate * total_rate / (total_rate - 1)  # Ежемесячный платеж

            overpayment = annuity_payment * total_loan_term - mortgage_loan_amount  # Переплата

            # Вычет за покупку (13% от стоимости, но не более чем с 2 млн)
            limit_purchase = 2_000_000
            tax_refund_purchase = min(real_estate_value, limit_purchase) * 0.13

            # Вычет за проценты по ипотеке (13% от переплаты, но не более чем с 3 млн)
            limit_interests = 3_000_000
            tax_refund_interests = min(overpayment, limit_interests) * 0.13

            total_refund = tax_refund_purchase + tax_refund_interests   # Общая сумма возврата



            K = 3.33540331196581
            print(f"Сумма кредита:{mortgage_loan_amount} ₽")
            print(f"Ежемесячный платёж:{(annuity_payment):.0f} ₽")
            print(f"Переплата по кредиту:{(overpayment):.0f} ₽")
            print(f"Общая выплата:{(mortgage_loan_amount + overpayment):.0f} ₽")
            print(f"Рекомендуемый доход:{(annuity_payment * K):.0f}")
            print("НАЛОГОВЫЙ ВЫЧЕТ (НДФЛ):")
            print(f"За покупку жилья: {tax_refund_purchase:.0f} ₽")
            print(f"За уплаченные проценты: {tax_refund_interests:.0f} ₽")
            print(f"Можно вернуть: {total_refund:.0f} ₽")
            print("\nНажмите клавишу Enter, чтобы продолжить")
            return mortgage_loan_amount, total_loan_term, annuity_payment, monthly_interest_rate

        except ValueError:
            print("Ошибка: неверный тип данных, допускаются только числа.")
        except ZeroDivisionError:
            print("Ошибка: срок кредита или ставка не могут быть нулевыми.")
        except NameError:
            pass


def plot_debt_schedule(mortgage_loan_amount, total_loan_term):
    plt.plot(mortgage_loan_amount, total_loan_term, marker='o', color='b', label='Остаток долга')

    plt.title('График погашения кредита')
    plt.xlabel('Месяцы')
    plt.ylabel('Сумма (₽)')
    plt.grid(True)
    plt.legend()

    plt.show()


def calculate_balance_schedule(loan_amount, monthly_rate, total_months):
    months = list(range(int(total_months) + 1))
    balances = []

    for k in months:
        if monthly_rate == 0:
            balance = loan_amount * (1 - k / total_months)
        else:
            # Формула остатка долга при аннуитете
            factor = (1 + monthly_rate) ** total_months
            balance = loan_amount * (factor - (1 + monthly_rate) ** k) / (factor - 1)
        balances.append(balance)
    return months, balances


if __name__ == "__main__":
    real_estate_value = float(input("Введите стоимость недвижимости: "))
    down_payment = float(input("Введите первоначальный взнос: "))
    term_in_years = float(input("Введите срок кредита в годах: "))
    bid = float(input("Введите годовую процентную ставку: "))

    # Получаем все нужные данные из калькулятора
    mortgage_loan_amount, total_loan_term, annuity_payment, monthly_interest_rate = mortgage_calculator(
        real_estate_value, down_payment, term_in_years, bid
    )

    # Строим правильный график остатка долга
    months, balances = calculate_balance_schedule(mortgage_loan_amount, monthly_interest_rate, total_loan_term)
    plot_debt_schedule(months, balances)