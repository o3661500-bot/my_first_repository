while True:
    try:
        # Ввод данных для расчета
        real_estate_value = float(input("Введите стоимость недвижимости: "))
        down_payment = float(input("Введите первоначальный взнос: "))
        term_in_years = float(input("Введите срок кредита в годах: "))
        bid = float(input("Введите годовую процентную ставку: "))

        # Вычисление значений
        mortgage_loan_amount = real_estate_value - down_payment  # Сумма иппотечного кредита

        monthly_interest_rate = bid / 12 / 100  # Месячная процентная ставка

        total_loan_term = term_in_years * 12    # Срок кредита в месяцах

        total_rate = (1 + monthly_interest_rate) ** total_loan_term # Общая ставка

        annuity_payment = mortgage_loan_amount * monthly_interest_rate * total_rate / (total_rate - 1)  # Ежемесячный платеж

        overpayment = annuity_payment * total_loan_term - mortgage_loan_amount  # Переплата

        # Вычет за покупку (13% от стоимости, но не более чем с 2 млн)
        limit_purchase = 2000000
        tax_refund_purchase = min(real_estate_value, limit_purchase) * 0.13

        # Вычет за проценты по ипотеке (13% от переплаты, но не более чем с 3 млн)
        limit_interests = 3000000
        tax_refund_interests = min(overpayment, limit_interests) * 0.13

        total_refund = tax_refund_purchase + tax_refund_interests   # Общая сумма возврата

        K = 3.33540331196581
    except ValueError:
        print("Ошибка: неверный тип данных, допускаются только числа.")
    except ZeroDivisionError:
        print("Ошибка: срок кредита или ставка не могут быть нулевыми.")

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
    if input("Введите q чтобы завершить ввод: ") == "q":
        break
