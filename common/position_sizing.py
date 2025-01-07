import math

class PositionSizing:
    """
    A class to calculate position size based on either the Kelly Criterion or Fixed Fractional Method.
    """
    def __init__(self, account_balance, risk_per_trade=0.01):
        """
        Initialize the PositionSizing class.

        Args:
            account_balance (float): Total account balance.
            risk_per_trade (float): Percentage of account balance to risk per trade (used in Fixed Fractional Method).
        """
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade

    def calculate_fixed_fractional(self, entry_price, stop_loss_price):
        """
        Calculate position size using the Fixed Fractional Method.

        Args:
            entry_price (float): Entry price of the trade.
            stop_loss_price (float): Stop-loss price of the trade.

        Returns:
            float: Position size.
        """
        risk_amount = self.account_balance * self.risk_per_trade
        stop_loss_distance = abs(entry_price - stop_loss_price)
        if stop_loss_distance == 0:
            raise ValueError("Stop-loss distance cannot be zero.")
        position_size = risk_amount / stop_loss_distance
        return position_size

    def calculate_kelly_criterion(self, win_rate, reward_to_risk_ratio):
        """
        Calculate position size using the Kelly Criterion.

        Args:
            win_rate (float): Probability of a winning trade (as a decimal, e.g., 0.6 for 60%).
            reward_to_risk_ratio (float): Ratio of reward to risk (e.g., 2.0 for a 2:1 reward to risk).

        Returns:
            float: Fraction of account balance to allocate based on Kelly Criterion.
        """
        if win_rate <= 0 or win_rate >= 1:
            raise ValueError("Win rate must be between 0 and 1.")
        if reward_to_risk_ratio <= 0:
            raise ValueError("Reward-to-risk ratio must be greater than 0.")

        kelly_fraction = win_rate - ((1 - win_rate) / reward_to_risk_ratio)
        return max(0, kelly_fraction)  # Kelly Criterion can never allocate negative capital

    def calculate_position_size(self, method, **kwargs):
        """
        Calculate position size based on the selected method.

        Args:
            method (str): The position sizing method ('fixed_fractional' or 'kelly').
            kwargs: Additional parameters needed for the selected method.

        Returns:
            float: Calculated position size.
        """
        if method == 'fixed_fractional':
            return self.calculate_fixed_fractional(
                kwargs['entry_price'], kwargs['stop_loss_price']
            )
        elif method == 'kelly':
            kelly_fraction = self.calculate_kelly_criterion(
                kwargs['win_rate'], kwargs['reward_to_risk_ratio']
            )
            return self.account_balance * kelly_fraction
        else:
            raise ValueError("Invalid method. Choose 'fixed_fractional' or 'kelly'.")

# Example Usage
if __name__ == "__main__":
    # Initialize the PositionSizing class with an account balance of $10,000
    account_balance = 10000
    position_sizing = PositionSizing(account_balance, risk_per_trade=0.02)

    # Fixed Fractional Method
    entry_price = 100
    stop_loss_price = 95
    fixed_fractional_size = position_sizing.calculate_position_size(
        method='fixed_fractional', entry_price=entry_price, stop_loss_price=stop_loss_price
    )
    print(f"Fixed Fractional Position Size: {fixed_fractional_size} units")

    # Kelly Criterion Method
    win_rate = 0.6  # 60% chance of winning
    reward_to_risk_ratio = 2.0  # Reward is twice the risk
    kelly_size = position_sizing.calculate_position_size(
        method='kelly', win_rate=win_rate, reward_to_risk_ratio=reward_to_risk_ratio
    )
    print(f"Kelly Criterion Position Size: ${kelly_size:.2f}")
