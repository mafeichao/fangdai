#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
房贷月供计算器
支持等额本息、等额本金、公积金自由还款三种还款方式
"""


def calc_equal_installment(principal: float, annual_rate: float, years: int) -> tuple:
    """
    计算等额本息月供

    Args:
        principal: 贷款本金（元）
        annual_rate: 年利率（如 0.039 表示 3.9%）
        years: 贷款年限

    Returns:
        (月供, 总还款额, 总利息)
    """
    if principal <= 0 or years <= 0:
        raise ValueError("贷款金额和年限必须大于 0")

    n = years * 12  # 还款月数
    r = annual_rate / 12  # 月利率

    if r == 0:
        monthly = principal / n
    else:
        # 等额本息公式: M = P * [r(1+r)^n] / [(1+r)^n - 1]
        monthly = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

    total = monthly * n
    total_interest = total - principal

    return round(monthly, 2), round(total, 2), round(total_interest, 2)


def calc_equal_principal(principal: float, annual_rate: float, years: int) -> tuple:
    """
    计算等额本金月供

    每月偿还固定本金，利息随剩余本金递减，首月月供最高、逐月递减。

    Args:
        principal: 贷款本金（元）
        annual_rate: 年利率（如 0.039 表示 3.9%）
        years: 贷款年限

    Returns:
        (首月月供, 末月月供, 总还款额, 总利息)
    """
    if principal <= 0 or years <= 0:
        raise ValueError("贷款金额和年限必须大于 0")

    n = years * 12  # 还款月数
    r = annual_rate / 12  # 月利率
    monthly_principal = principal / n  # 每月偿还本金（固定）

    if r == 0:
        total_interest = 0
        first_month = last_month = monthly_principal
    else:
        # 总利息 = 本金 × 月利率 × (期数+1) / 2
        total_interest = principal * r * (n + 1) / 2
        # 首月月供 = 每月本金 + 本金×月利率
        first_month = monthly_principal + principal * r
        # 末月月供 = 每月本金 + 当月利息 = 每月本金 + 每月本金×月利率
        last_month = monthly_principal + monthly_principal * r

    total = principal + total_interest

    return (
        round(first_month, 2),
        round(last_month, 2),
        round(total, 2),
        round(total_interest, 2),
    )


def schedule_equal_installment(
    principal: float, annual_rate: float, years: int
) -> list:
    """等额本息：生成每月还款明细 [(期数, 月供, 本金, 利息, 剩余本金), ...]"""
    n = years * 12
    r = annual_rate / 12
    if r == 0:
        monthly = principal / n
    else:
        monthly = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    schedule = []
    remaining = principal
    for k in range(1, n + 1):
        interest = remaining * r if r else 0
        principal_pay = monthly - interest
        remaining = remaining - principal_pay
        if k == n:
            remaining = 0
        schedule.append(
            (k, round(monthly, 2), round(principal_pay, 2), round(interest, 2), round(remaining, 2))
        )
    return schedule


def schedule_equal_principal(
    principal: float, annual_rate: float, years: int
) -> list:
    """等额本金：生成每月还款明细 [(期数, 月供, 本金, 利息, 剩余本金), ...]"""
    n = years * 12
    r = annual_rate / 12
    monthly_principal = principal / n
    schedule = []
    remaining = principal
    for k in range(1, n + 1):
        interest = remaining * r if r else 0
        payment = monthly_principal + interest
        remaining = remaining - monthly_principal
        if k == n:
            remaining = 0
        schedule.append(
            (k, round(payment, 2), round(monthly_principal, 2), round(interest, 2), round(remaining, 2))
        )
    return schedule


def schedule_provident_fund_free(
    principal: float, annual_rate: float, monthly_payment: float = 9000
) -> list:
    """
    公积金自由还款：按固定月供还款，直到还清
    每月还款额固定，最后一期不足时只还剩余本息
    返回 [(期数, 月供, 本金, 利息, 剩余本金), ...]
    """
    r = annual_rate / 12
    schedule = []
    remaining = principal
    period = 0
    while remaining > 0.01:  # 避免浮点误差
        period += 1
        interest = remaining * r if r else 0
        pay_off_amount = remaining + interest  # 一次性还清所需金额
        payment = min(monthly_payment, round(pay_off_amount, 2))
        principal_pay = payment - interest
        remaining = remaining - principal_pay
        if remaining < 0.01:
            remaining = 0
        schedule.append(
            (
                period,
                round(payment, 2),
                round(principal_pay, 2),
                round(interest, 2),
                round(remaining, 2),
            )
        )
    return schedule


def print_schedule(schedule: list, principal: float, max_rows: int = 0):
    """按每月一行输出还款计划表（制表符分隔，便于复制到 Excel）；max_rows=0 表示输出全部，>0 时仅输出前 max_rows 行"""
    print()
    print("还款计划（制表符分隔，可直接复制到 Excel）：")
    if max_rows > 0:
        print(f"（仅显示前 {max_rows} 期，共 {len(schedule)} 期）")
    print("说明：差额@3%/4%/5% = 当期提前还款时（若将贷款本金按该年化复利投资至当期的收益−累计还息）")
    # 表头：Tab 分隔，粘贴到 Excel 时自动分列
    headers = ["期数", "月供", "本金", "利息", "累计还息", "差额@3%", "差额@4%", "差额@5%", "剩余本金"]
    print("\t".join(headers))
    cum_interest = 0.0
    r3, r4, r5 = 0.03 / 12, 0.04 / 12, 0.05 / 12
    to_print = schedule[:max_rows] if max_rows > 0 else schedule
    for period, payment, prin, interest, remaining in to_print:
        cum_interest += interest
        inv_3 = principal * ((1 + r3) ** period - 1)
        inv_4 = principal * ((1 + r4) ** period - 1)
        inv_5 = principal * ((1 + r5) ** period - 1)
        diff_3 = inv_3 - cum_interest
        diff_4 = inv_4 - cum_interest
        diff_5 = inv_5 - cum_interest
        # 数字不加重千分位，方便 Excel 识别为数值
        row = [
            period,
            f"{payment:.2f}",
            f"{prin:.2f}",
            f"{interest:.2f}",
            f"{cum_interest:.2f}",
            f"{diff_3:.2f}",
            f"{diff_4:.2f}",
            f"{diff_5:.2f}",
            f"{remaining:.2f}",
        ]
        print("\t".join(str(x) for x in row))


def main():
    print("-" * 50)
    print("            房贷月供计算器")
    print("-" * 50)
    print("还款方式：1. 等额本息  2. 等额本金  3. 公积金自由还款")
    print()

    try:
        choice = input("请选择还款方式（1 / 2 / 3）：").strip()
        principal = float(input("请输入贷款金额（万元）：")) * 10000
        annual_rate_pct = float(input("请输入年利率（%）："))
        annual_rate = annual_rate_pct / 100

        if choice == "3":
            # 公积金自由还款：月供默认 9000
            monthly_input = input("请输入月供（元，留空默认 9000）：").strip()
            monthly_payment = float(monthly_input) if monthly_input else 9000
            if monthly_payment <= 0:
                monthly_payment = 9000
            max_rows_input = input("还款计划输出行数（0 或留空=全部）：").strip()
            max_rows = int(max_rows_input) if max_rows_input else 0
            if max_rows < 0:
                max_rows = 0
        else:
            years = int(input("请输入贷款年限（年）："))
            max_rows_input = input("还款计划输出行数（0 或留空=全部）：").strip()
            max_rows = int(max_rows_input) if max_rows_input else 0
            if max_rows < 0:
                max_rows = 0
    except ValueError:
        print("输入格式有误，请检查后重试。")
        return

    print()
    print("-" * 50)
    print(f"贷款本金：     {principal:,.2f} 元")
    print(f"年利率：       {annual_rate_pct}%")

    if choice == "2":
        # 等额本金
        n_months = years * 12
        print(f"贷款期限：     {years} 年（{n_months} 期）")
        print("-" * 50)
        first_month, last_month, total, total_interest = calc_equal_principal(
            principal, annual_rate, years
        )
        monthly_principal = principal / n_months
        print(f"每月偿还本金： {monthly_principal:,.2f} 元（固定）")
        print(f"首月月供：     {first_month:,.2f} 元")
        print(f"末月月供：     {last_month:,.2f} 元（逐月递减）")
        print(f"还款总额：     {total:,.2f} 元")
        print(f"支付利息：     {total_interest:,.2f} 元")
        print_schedule(schedule_equal_principal(principal, annual_rate, years), principal, max_rows)
    elif choice == "3":
        # 公积金自由还款
        schedule = schedule_provident_fund_free(principal, annual_rate, monthly_payment)
        n_periods = len(schedule)
        total = sum(row[1] for row in schedule)
        total_interest = total - principal
        print(f"月供：         {monthly_payment:,.2f} 元（固定，末月可能不足）")
        print(f"还款期数：     {n_periods} 期（约 {n_periods / 12:.1f} 年）")
        print("-" * 50)
        print(f"还款总额：     {total:,.2f} 元")
        print(f"支付利息：     {total_interest:,.2f} 元")
        print_schedule(schedule, principal, max_rows)
    else:
        # 默认等额本息
        n_months = years * 12
        print(f"贷款期限：     {years} 年（{n_months} 期）")
        print("-" * 50)
        if choice != "1":
            print("未识别的选择，按等额本息计算。")
        monthly, total, total_interest = calc_equal_installment(
            principal, annual_rate, years
        )
        print(f"每月月供：     {monthly:,.2f} 元（固定）")
        print(f"还款总额：     {total:,.2f} 元")
        print(f"支付利息：     {total_interest:,.2f} 元")
        print_schedule(schedule_equal_installment(principal, annual_rate, years), principal, max_rows)

    print("-" * 50)


if __name__ == "__main__":
    main()
