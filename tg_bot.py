import matplotlib.pyplot as plt

# Данные для графика
months = [0, 12, 24, 36, 48, 60]
balance = [1000000, 850000, 680000, 490000, 280000, 0]

# Создание графика
plt.plot(months, balance, marker='o', color='b', label='Остаток долга')

# Настройка оформления
plt.title('График погашения кредита')
plt.xlabel('Месяцы')
plt.ylabel('Сумма (₽)')
plt.grid(True)
plt.legend()

# Отображение
plt.show()